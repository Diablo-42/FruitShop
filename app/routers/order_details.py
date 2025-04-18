from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/order-detail",
    tags=["order_details"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.OrderDetail])
async def get_all_order_details(
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех деталей заказов (только для администраторов)
    """
    result = await db.execute(select(models.OrderDetail))
    order_details = result.scalars().all()
    return order_details

@router.get("/{id}", response_model=schemas.OrderDetail)
async def get_order_detail(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение детали заказа по ID (требуется авторизация)
    """
    result = await db.execute(
        select(models.OrderDetail)
        .filter(models.OrderDetail.id_order_detail == id)
    )
    order_detail = result.scalars().first()
    if order_detail is None:
        raise HTTPException(status_code=404, detail="Деталь заказа не найдена")
    
    if current_user.role != "admin":
        order = await db.execute(
            select(models.Order)
            .filter(models.Order.id_order == order_detail.id_order)
        )
        order = order.scalars().first()
        if order.id_client != current_user.id:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return order_detail

@router.get("/order/{order_id}", response_model=List[schemas.OrderDetail])
async def get_order_details_by_order(
    order_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение всех деталей конкретного заказа (требуется авторизация)
    """
    # Проверяем права доступа
    order = await db.execute(
        select(models.Order).filter(models.Order.id_order == order_id)
    )
    order = order.scalars().first()
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if current_user.role != "admin" and order.id_client != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    result = await db.execute(
        select(models.OrderDetail)
        .filter(models.OrderDetail.id_order == order_id)
    )
    order_details = result.scalars().all()
    return order_details

@router.post("", response_model=schemas.OrderDetail, status_code=201)
async def add_order_detail(
    order_detail: schemas.OrderDetailCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление новой детали заказа (требуется авторизация)
    """
    product = await db.execute(
        select(models.Product)
        .filter(models.Product.id_product == order_detail.id_product)
    )
    product = product.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    if order_detail.unit_type != product.unit_type:
        raise HTTPException(
            status_code=400,
            detail=f"Неверный тип единицы измерения для товара {product.name}"
        )

    db_order_detail = models.OrderDetail(**order_detail.model_dump())
    db_order_detail.price = product.price_per_unit
    
    db.add(db_order_detail)
    await db.commit()
    await db.refresh(db_order_detail)

    order = await db.execute(
        select(models.Order)
        .filter(models.Order.id_order == db_order_detail.id_order)
    )
    order = order.scalars().first()
    if order:
        order.total_amount = order.total_amount + (db_order_detail.quantity * db_order_detail.price)
        await db.commit()

    return db_order_detail

@router.put("/{id}", response_model=schemas.OrderDetail)
async def update_order_detail(
    id: int,
    order_detail: schemas.OrderDetailUpdate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление детали заказа по ID (требуется авторизация)
    """
    result = await db.execute(
        select(models.OrderDetail)
        .filter(models.OrderDetail.id_order_detail == id)
    )
    db_order_detail = result.scalars().first()
    if db_order_detail is None:
        raise HTTPException(status_code=404, detail="Деталь заказа не найдена")

    # Проверяем права доступа
    order = await db.execute(
        select(models.Order)
        .filter(models.Order.id_order == db_order_detail.id_order)
    )
    order = order.scalars().first()
    if current_user.role != "admin" and order.id_client != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    old_total = db_order_detail.quantity * db_order_detail.price
    
    update_data = order_detail.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order_detail, key, value)
    new_total = db_order_detail.quantity * db_order_detail.price
    if new_total != old_total:
        order.total_amount = order.total_amount - old_total + new_total
    
    await db.commit()
    await db.refresh(db_order_detail)
    return db_order_detail

@router.delete("/{id}")
async def delete_order_detail(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление детали заказа по ID (требуется авторизация)
    """
    result = await db.execute(
        select(models.OrderDetail)
        .filter(models.OrderDetail.id_order_detail == id)
    )
    db_order_detail = result.scalars().first()
    if db_order_detail is None:
        raise HTTPException(status_code=404, detail="Деталь заказа не найдена")

    order = await db.execute(
        select(models.Order)
        .filter(models.Order.id_order == db_order_detail.id_order)
    )
    order = order.scalars().first()
    if current_user.role != "admin" and order.id_client != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    total_amount = db_order_detail.quantity * db_order_detail.price
    order.total_amount = order.total_amount - total_amount

    await db.delete(db_order_detail)
    await db.commit()
    return {"message": "Деталь заказа удалена"}