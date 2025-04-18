from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/category",
    tags=["categories"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.Category])
async def get_all_categories(
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех категорий (требуется авторизация)
    """
    result = await db.execute(select(models.Category))
    categories = result.scalars().all()
    return categories

@router.get("/{id}", response_model=schemas.Category)
async def get_category(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение категории по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    category = result.scalars().first()
    if category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category

@router.get("/{id}/products", response_model=List[schemas.Product])
async def get_category_products(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение всех продуктов по ID категории (требуется авторизация)
    """
    result = await db.execute(select(models.Product).filter(models.Product.id_category == id))
    products = result.scalars().all()
    return products

@router.post("", response_model=schemas.Category, status_code=201)
async def add_category(
    category: schemas.CategoryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление новой категории (только для администраторов)
    """
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.put("/{id}", response_model=schemas.Category)
async def update_category(
    id: int,
    category: schemas.CategoryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление категории по ID (только для администраторов)
    """
    result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    db_category = result.scalars().first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.delete("/{id}")
async def delete_category(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление категории по ID (только для администраторов)
    """
    result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    db_category = result.scalars().first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    await db.delete(db_category)
    await db.commit()
    return {"message": "Категория удалена"}