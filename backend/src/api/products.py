from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from backend.src.utils.security import has_role
from backend.src.utils.db import get_db
from backend.src import models, schemas

router = APIRouter(
    prefix="/product",
    tags=["products"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"}
    },
)
@router.get("/all", response_model=List[schemas.Product])
async def get_all_products(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Product).options(
            selectinload(models.Product.country),
            selectinload(models.Product.category)
        )
    )
    products = result.scalars().all()
    return products

@router.get("/{id}", response_model=schemas.Product)
async def get_product(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Product).options(
            selectinload(models.Product.country),
            selectinload(models.Product.category)
        ).filter(models.Product.id_product == id)
    )
    product = result.scalars().first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return product

@router.get("/country/{id}", response_model=List[schemas.Product])
async def get_products_by_country(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    country_result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    if country_result.scalars().first() is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена")

    result = await db.execute(
        select(models.Product).options(
            selectinload(models.Product.country),
            selectinload(models.Product.category)
        ).filter(models.Product.id_country == id)
    )
    products = result.scalars().all()
    return products

@router.post("", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_data: schemas.ProductCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    cat_res = await db.execute(select(models.Category).filter(models.Category.id_category == product_data.id_category))
    if not cat_res.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Категория с ID {product_data.id_category} не найдена")

    country_res = await db.execute(select(models.Country).filter(models.Country.id_country == product_data.id_country))
    if not country_res.scalars().first():
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Страна с ID {product_data.id_country} не найдена")

    db_product = models.Product(**product_data.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    result_with_relations = await db.execute(
        select(models.Product).options(
            selectinload(models.Product.country),
            selectinload(models.Product.category)
        ).filter(models.Product.id_product == db_product.id_product)
    )
    final_product = result_with_relations.scalars().first()
    return final_product

@router.put("/{id}", response_model=schemas.Product)
async def update_product(
    id: int,
    product_update_data: schemas.ProductUpdate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Product).filter(models.Product.id_product == id))
    db_product = result.scalars().first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    update_data = product_update_data.model_dump(exclude_unset=True)

    if 'id_category' in update_data:
        cat_res = await db.execute(select(models.Category).filter(models.Category.id_category == update_data['id_category']))
        if not cat_res.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Категория с ID {update_data['id_category']} не найдена")
    if 'id_country' in update_data:
        country_res = await db.execute(select(models.Country).filter(models.Country.id_country == update_data['id_country']))
        if not country_res.scalars().first():
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Страна с ID {update_data['id_country']} не найдена")

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления")

    for key, value in update_data.items():
        setattr(db_product, key, value)

    await db.commit()
    await db.refresh(db_product)

    result_with_relations = await db.execute(
        select(models.Product).options(
            selectinload(models.Product.country),
            selectinload(models.Product.category)
        ).filter(models.Product.id_product == db_product.id_product)
    )
    final_product = result_with_relations.scalars().first()
    return final_product


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Product).filter(models.Product.id_product == id))
    db_product = result.scalars().first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    await db.delete(db_product)
    await db.commit()
    return {"message": "Товар удален"}
