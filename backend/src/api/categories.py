from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from backend.src.utils.security import has_role
from backend.src.utils.db import get_db
from backend.src import models, schemas

router = APIRouter(
    prefix="/category",
    tags=["categories"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"}
    },
)

@router.get("/all", response_model=List[schemas.Category])
async def get_all_categories(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Category))
    categories = result.scalars().all()
    return categories

@router.get("/{id}", response_model=schemas.Category)
async def get_category(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    category = result.scalars().first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    return category

@router.get("/{id}/products", response_model=List[schemas.Product])
async def get_category_products(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    category_result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    if category_result.scalars().first() is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    result = await db.execute(
        select(models.Product).options(
            selectinload(models.Product.country),
            selectinload(models.Product.category)
        ).filter(models.Product.id_category == id)
    )
    products = result.scalars().all()
    return products


@router.post("", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
async def add_category(
    category: schemas.CategoryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.put("/{id}", response_model=schemas.Category)
async def update_category(
    id: int,
    category_update: schemas.CategoryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    db_category = result.scalars().first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    update_data = category_update.model_dump()
    for key, value in update_data.items():
        setattr(db_category, key, value)

    await db.commit()
    await db.refresh(db_category)
    return db_category

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Category).filter(models.Category.id_category == id))
    db_category = result.scalars().first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    await db.delete(db_category)
    await db.commit()
    return {"message": "Категория удалена"}