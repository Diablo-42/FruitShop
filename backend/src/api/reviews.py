from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from backend.src.utils.security import get_current_active_user
from backend.src.utils.db import get_db
from backend.src import models, schemas

router = APIRouter(
    prefix="/review",
    tags=["reviews"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"}
    },
)

@router.get("/all", response_model=List[schemas.Review])
async def get_all_reviews(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Review).options(
            selectinload(models.Review.product),
            selectinload(models.Review.user)
        )
    )
    reviews = result.scalars().unique().all()
    return reviews

@router.get("/{id}", response_model=schemas.Review)
async def get_review(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Review).options(
            selectinload(models.Review.product),
            selectinload(models.Review.user)
         ).filter(models.Review.id_review == id)
    )
    review = result.scalars().unique().first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")
    return review

@router.get("/product/{id}", response_model=List[schemas.Review])
async def get_reviews_by_product(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    product_result = await db.execute(select(models.Product).filter(models.Product.id_product == id))
    if product_result.scalars().first() is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Продукт не найден")

    result = await db.execute(
        select(models.Review).options(
            selectinload(models.Review.user)
        ).filter(models.Review.id_product == id)
    )
    reviews = result.scalars().unique().all()
    return reviews


@router.get("/user/{user_id}", response_model=List[schemas.Review])
async def get_reviews_by_user(
    user_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для просмотра чужих отзывов")

    user_check_result = await db.execute(select(models.User).filter(models.User.id == user_id))
    if user_check_result.scalars().first() is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    result = await db.execute(
        select(models.Review).options(
            selectinload(models.Review.product)
        ).filter(models.Review.id_user == user_id)
    )
    reviews = result.scalars().unique().all()
    return reviews

@router.post("", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
async def add_review(
    review_data: schemas.ReviewCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    review_dict = review_data.model_dump()

    product_result = await db.execute(select(models.Product).filter(models.Product.id_product == review_dict['id_product']))
    if not product_result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Продукт с ID {review_dict['id_product']} не найден")

    user_id = current_user.id
    review_dict['id_user'] = user_id

    existing_review = await db.execute(
        select(models.Review).filter(
            models.Review.id_user == user_id,
            models.Review.id_product == review_dict['id_product']
        )
    )
    if existing_review.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оставили отзыв на этот товар."
        )

    db_review = models.Review(**review_dict)

    db.add(db_review)
    await db.commit()

    result_with_relations = await db.execute(
        select(models.Review).options(
            selectinload(models.Review.product),
            selectinload(models.Review.user)
        ).filter(models.Review.id_review == db_review.id_review)
    )
    final_review = result_with_relations.scalars().unique().first()

    return final_review

@router.put("/{id}", response_model=schemas.Review)
async def update_review(
    id: int,
    review_update_data: schemas.ReviewUpdate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Review).filter(models.Review.id_review == id))
    db_review = result.scalars().first()
    if db_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")

    if current_user.role != "admin" and current_user.id != db_review.id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для изменения этого отзыва")

    update_data = review_update_data.model_dump(exclude_unset=True)

    if not update_data:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления (можно обновить 'rating' и 'comment')")

    for key, value in update_data.items():
        setattr(db_review, key, value)

    await db.commit()

    result_with_relations = await db.execute(
        select(models.Review).options(
            selectinload(models.Review.product),
            selectinload(models.Review.user)
        ).filter(models.Review.id_review == db_review.id_review)
    )
    final_review = result_with_relations.scalars().unique().first()

    return final_review

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Review).filter(models.Review.id_review == id))
    db_review = result.scalars().first()
    if db_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отзыв не найден")

    if current_user.role != "admin" and current_user.id != db_review.id_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для удаления этого отзыва")

    await db.delete(db_review)
    await db.commit()
    return None