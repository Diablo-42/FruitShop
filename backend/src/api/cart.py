from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from backend.src import models, schemas
from backend.src.utils.db import get_db
from backend.src.utils.security import get_current_active_user

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("", response_model=List[schemas.CartItem])
async def read_user_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.CartItem)
        .where(models.CartItem.user_id == current_user.id)
        .options(selectinload(models.CartItem.product))
    )
    cart_items = result.scalars().all()
    return cart_items

@router.post("/items", response_model=schemas.CartItem, status_code=status.HTTP_201_CREATED)
async def add_product_to_cart(
    item_in: schemas.CartItemCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.CartItem)
        .where(models.CartItem.user_id == current_user.id, models.CartItem.product_id == item_in.product_id)
        .options(selectinload(models.CartItem.product))
    )
    existing_item = result.scalars().first()

    db_item: models.CartItem

    if existing_item:
        # Если товар уже есть, увеличиваем количество
        new_quantity = existing_item.quantity + item_in.quantity
        existing_item.quantity = max(1, new_quantity)
        db_item = existing_item
    else:
        # Если товара нет, создаем новую запись
        product_exists = await db.get(models.Product, item_in.product_id)
        if not product_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товар с id {item_in.product_id} не найден")

        db_item = models.CartItem(
            user_id=current_user.id,
            product_id=item_in.product_id,
            quantity=max(1, item_in.quantity)
        )
        db.add(db_item)

    await db.commit()
    await db.refresh(db_item)
    await db.refresh(db_item, attribute_names=['product'])
    return db_item


@router.put("/items/{product_id}", response_model=schemas.CartItem)
async def update_product_quantity_in_cart(
    product_id: int,
    quantity_update: schemas.CartItemUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.CartItem)
        .where(models.CartItem.user_id == current_user.id, models.CartItem.product_id == product_id)
        .options(selectinload(models.CartItem.product))
    )
    db_item = result.scalars().first()

    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден в корзине")

    new_quantity = max(1, quantity_update.quantity)
    db_item.quantity = new_quantity

    await db.commit()
    await db.refresh(db_item)
    await db.refresh(db_item, attribute_names=['product'])
    return db_item


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_from_cart(
    product_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.CartItem)
        .where(models.CartItem.user_id == current_user.id, models.CartItem.product_id == product_id)
    )
    db_item = result.scalars().first()

    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден в корзине")

    await db.delete(db_item)

    await db.commit()
    return None

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_cart_endpoint(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.CartItem).where(models.CartItem.user_id == current_user.id)
    )
    items_to_delete = result.scalars().all()
    for item in items_to_delete:
        await db.delete(item)

    await db.commit()
    return None

