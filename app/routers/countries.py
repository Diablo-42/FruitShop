from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/country",
    tags=["countries"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.Country])
async def get_all_countries(
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех стран (требуется авторизация)
    """
    result = await db.execute(select(models.Country))
    countries = result.scalars().all()
    return countries

@router.get("/{id}", response_model=schemas.Country)
async def get_country(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение страны по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    country = result.scalars().first()
    if country is None:
        raise HTTPException(status_code=404, detail="Страна не найдена")
    return country

@router.post("", response_model=schemas.Country, status_code=201)
async def add_country(
    country: schemas.CountryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление новой страны (только для администраторов)
    """
    db_country = models.Country(**country.model_dump())
    db.add(db_country)
    await db.commit()
    await db.refresh(db_country)
    return db_country

@router.put("/{id}", response_model=schemas.Country)
async def update_country(
    id: int,
    country: schemas.CountryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление страны по ID (только для администраторов)
    """
    result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    db_country = result.scalars().first()
    if db_country is None:
        raise HTTPException(status_code=404, detail="Страна не найдена")
    
    for key, value in country.model_dump().items():
        setattr(db_country, key, value)
    
    await db.commit()
    await db.refresh(db_country)
    return db_country

@router.delete("/{id}")
async def delete_country(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление страны по ID (только для администраторов)
    """
    result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    db_country = result.scalars().first()
    if db_country is None:
        raise HTTPException(status_code=404, detail="Страна не найдена")
    
    await db.delete(db_country)
    await db.commit()
    return {"message": "Страна удалена"}