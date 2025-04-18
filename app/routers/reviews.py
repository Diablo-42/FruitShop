from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/review",
    tags=["reviews"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.Review])
async def get_all_reviews(
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех отзывов (требуется авторизация)
    """
    result = await db.execute(select(models.Review))
    reviews = result.scalars().all()
    return reviews

@router.get("/{id}", response_model=schemas.Review)
async def get_review(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение отзыва по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Review).filter(models.Review.id_review == id))
    review = result.scalars().first()
    if review is None:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    return review

@router.get("/product/{id}", response_model=List[schemas.Review])
async def get_reviews_by_product(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение всех отзывов по ID продукта (требуется авторизация)
    """
    result = await db.execute(select(models.Review).filter(models.Review.id_product == id))
    reviews = result.scalars().all()
    return reviews

@router.get("/client/{id}", response_model=List[schemas.Review])
async def get_reviews_by_client(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение всех отзывов по ID клиента (требуется авторизация)
    """
    if current_user.role != "admin" and current_user.id != id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    result = await db.execute(select(models.Review).filter(models.Review.id_client == id))
    reviews = result.scalars().all()
    return reviews

@router.post("", response_model=schemas.Review, status_code=201)
async def add_review(
    review: schemas.ReviewCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление нового отзыва (требуется авторизация)
    """
    review_data = review.model_dump()
    if current_user.role != "admin":
        review_data['id_client'] = current_user.id
    
    db_review = models.Review(**review_data)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.put("/{id}", response_model=schemas.Review)
async def update_review(
    id: int,
    review: schemas.ReviewCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление отзыва по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Review).filter(models.Review.id_review == id))
    db_review = result.scalars().first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    
    if current_user.role != "admin" and current_user.id != db_review.id_client:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    for key, value in review.model_dump().items():
        setattr(db_review, key, value)
    
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.delete("/{id}")
async def delete_review(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление отзыва по ID (требуется авторизация)
    """
    result = await db.execute(select(models.Review).filter(models.Review.id_review == id))
    db_review = result.scalars().first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    
    if current_user.role != "admin" and current_user.id != db_review.id_client:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await db.delete(db_review)
    await db.commit()
    return {"message": "Отзыв удален"}