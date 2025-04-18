from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/order",
    tags=["orders"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.Order])
async def get_all_orders(
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех заказов (только для администраторов)
    """
    result = await db.execute(select(models.Order))
    orders = result.scalars().all()
    return orders

@router.get("/{id}", response_model=schemas.Order)
async def get_order(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение заказа по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Order).filter(models.Order.id_order == id))
    order = result.scalars().first()
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if current_user.role != "admin" and current_user.id != order.id_client:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return order

@router.post("", response_model=schemas.Order, status_code=201)
async def create_order(
    order: schemas.OrderCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создание нового заказа с деталями
    """
    if current_user.role != "admin" and current_user.id != order.id_client:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    db_order = models.Order(
        id_client=order.id_client,
        order_date=datetime.now(),
        total_amount=0
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    total_amount = 0
    for detail in order.order_details:
        result = await db.execute(
            select(models.Product).filter(models.Product.id_product == detail.id_product)
        )
        product = result.scalars().first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар {detail.id_product} не найден")

        if detail.unit_type != product.unit_type:
            raise HTTPException(
                status_code=400, 
                detail=f"Неверный тип единицы измерения для товара {product.name}"
            )

        db_detail = models.OrderDetail(
            id_order=db_order.id_order,
            id_product=detail.id_product,
            quantity=detail.quantity,
            unit_type=detail.unit_type,
            price=product.price_per_unit
        )
        db.add(db_detail)
        
        total_amount += detail.quantity * product.price_per_unit

    db_order.total_amount = total_amount
    await db.commit()
    await db.refresh(db_order)

    return db_order

@router.put("/{id}", response_model=schemas.Order)
async def update_order(
    id: int,
    order: schemas.OrderCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление заказа по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Order).filter(models.Order.id_order == id))
    db_order = result.scalars().first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if current_user.role != "admin" and current_user.id != db_order.id_client:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    for key, value in order.model_dump(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    await db.commit()
    await db.refresh(db_order)
    return db_order

@router.delete("/{id}")
async def delete_order(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление заказа по ID (только для администраторов)
    """
    result = await db.execute(select(models.Order).filter(models.Order.id_order == id))
    db_order = result.scalars().first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    await db.delete(db_order)
    await db.commit()
    return {"message": "Заказ удален"}