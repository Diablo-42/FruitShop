from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/product",
    tags=["products"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.Product])
async def get_all_products(
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех товаров (требуется авторизация)
    """
    result = await db.execute(select(models.Product))
    products = result.scalars().all()
    return products

@router.get("/{id}", response_model=schemas.Product)
async def get_product(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение товара по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Product).filter(models.Product.id_product == id))
    product = result.scalars().first()
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product

@router.get("/country/{id}", response_model=List[schemas.Product])
async def get_products_by_country(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение товаров по ID страны (требуется авторизация)
    """
    result = await db.execute(select(models.Product).filter(models.Product.id_country == id))
    products = result.scalars().all()
    return products

@router.post("", response_model=schemas.Product, status_code=201)
async def add_product(
    product: schemas.ProductCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление нового товара (только для администраторов)
    """
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.put("/{id}", response_model=schemas.Product)
async def update_product(
    id: int,
    product: schemas.ProductCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление товара по ID (только для администраторов)
    """
    result = await db.execute(select(models.Product).filter(models.Product.id_product == id))
    db_product = result.scalars().first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.delete("/{id}")
async def delete_product(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление товара по ID (только для администраторов)
    """
    result = await db.execute(select(models.Product).filter(models.Product.id_product == id))
    db_product = result.scalars().first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    await db.delete(db_product)
    await db.commit()
    return {"message": "Товар удален"}