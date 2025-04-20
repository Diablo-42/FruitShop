from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from typing import List
from datetime import datetime

from backend.src.utils.security import get_current_active_user, has_role
from backend.src.utils.db import get_db
from backend.src import models, schemas

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"}
    },
)

@router.get("/all", response_model=List[schemas.Order])
async def get_all_orders(
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Order).options(
            selectinload(models.Order.order_details).options(selectinload(models.OrderDetail.product))
        )
    )
    orders = result.scalars().unique().all()
    return orders

@router.get("/{id}", response_model=schemas.Order)
async def get_order(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Order).options(
            selectinload(models.Order.order_details).options(selectinload(models.OrderDetail.product))
        ).filter(models.Order.id_order == id)
    )
    order = result.scalars().unique().first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

    if current_user.role != "admin" and current_user.id != order.id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")

    return order

@router.get("/{id}/items", response_model=List[schemas.OrderDetail])
async def get_order_items(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    order_result = await db.execute(
        select(models.Order).filter(models.Order.id_order == id)
    )
    order = order_result.scalars().first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

    if current_user.role != "admin" and order.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для просмотра деталей этого заказа")

    result = await db.execute(select(models.OrderDetail).filter(models.OrderDetail.id_order == id))
    order_details = result.scalars().all()
    return order_details


@router.post("", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: schemas.OrderCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    user_id_for_order = current_user.id

    if not order_data.order_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ должен содержать хотя бы один товар")

    db_order = models.Order(
        id_user=user_id_for_order,
        order_date=datetime.now(),
        status=schemas.OrderStatusEnum.PENDING,
        total_amount=0.0
    )
    db.add(db_order)
    await db.flush()

    total_amount = 0.0
    order_details_to_add = []

    product_ids = [detail.id_product for detail in order_data.order_details]
    product_results = await db.execute(
        select(models.Product).filter(models.Product.id_product.in_(product_ids))
    )
    products_map = {p.id_product: p for p in product_results.scalars()}

    for detail_data in order_data.order_details:
        product = products_map.get(detail_data.id_product)
        if not product:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Товар с ID {detail_data.id_product} не найден")

        unit_type = product.unit_type
        price = product.price_per_unit

        db_detail = models.OrderDetail(
            id_order=db_order.id_order,
            id_product=detail_data.id_product,
            quantity=detail_data.quantity,
            unit_type=unit_type,
            price=price
        )
        order_details_to_add.append(db_detail)
        total_amount += detail_data.quantity * price

    if not order_details_to_add:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ должен содержать хотя бы один товар")

    db_order.total_amount = total_amount
    db.add_all(order_details_to_add)

    await db.commit()

    final_order_result = await db.execute(
        select(models.Order).options(
            selectinload(models.Order.order_details).options(selectinload(models.OrderDetail.product))
        ).filter(models.Order.id_order == db_order.id_order)
    )
    final_order = final_order_result.scalars().unique().first()

    return final_order


@router.put("/{id}", response_model=schemas.Order)
async def update_order(
    id: int,
    order_update_data: schemas.OrderUpdate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Order).filter(models.Order.id_order == id))
    db_order = result.scalars().first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для изменения статуса заказа")

    update_data = order_update_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления")

    for key, value in update_data.items():
        setattr(db_order, key, value)

    await db.commit()

    final_order_result = await db.execute(
        select(models.Order).options(
            selectinload(models.Order.order_details).options(selectinload(models.OrderDetail.product))
        ).filter(models.Order.id_order == db_order.id_order)
    )
    final_order = final_order_result.scalars().unique().first()

    return final_order


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Order).filter(models.Order.id_order == id))
    db_order = result.scalars().first()
    if db_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

    await db.delete(db_order)
    await db.commit()
    return {"message: Заказ удален"}
