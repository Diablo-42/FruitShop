from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from backend.src.utils.security import has_role
from backend.src.utils.db import get_db
from backend.src import models, schemas

router = APIRouter(
    prefix="/country",
    tags=["countries"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"}
    },
)

@router.get("/all", response_model=List[schemas.Country])
async def get_all_countries(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Country))
    countries = result.scalars().all()
    return countries

@router.get("/{id}", response_model=schemas.Country)
async def get_country(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    country = result.scalars().first()
    if country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена")
    return country

@router.post("", response_model=schemas.Country, status_code=status.HTTP_201_CREATED)
async def add_country(
    country: schemas.CountryCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    db_country = models.Country(**country.model_dump())
    db.add(db_country)
    await db.commit()
    await db.refresh(db_country)
    return db_country

@router.put("/{id}", response_model=schemas.Country)
async def update_country(
    id: int,
    country_update: schemas.CountryCreate, # Используем Create для полного обновления
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    db_country = result.scalars().first()
    if db_country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена")

    update_data = country_update.model_dump() # Полное обновление
    for key, value in update_data.items():
        setattr(db_country, key, value)

    await db.commit()
    await db.refresh(db_country)
    return db_country

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Country).filter(models.Country.id_country == id))
    db_country = result.scalars().first()
    if db_country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Страна не найдена")

    await db.delete(db_country)
    await db.commit()
    return {"message": "Страна удалена"}
