from typing import List
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.utils.db import get_db
from app.utils.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    get_current_active_user, 
    has_role
)
from app import schemas, models

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={401: {"description": "Unauthorized"}},
)

# Аутентификация
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Регистрация и управление пользователями
@router.post("/register", response_model=schemas.User, status_code=201)
async def register_user(
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверка уникальности username и email
    result = await db.execute(
        select(models.User).filter(models.User.username == user_data.username)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    result = await db.execute(
        select(models.User).filter(models.User.email == user_data.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создание нового пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        address=user_data.address,
        phone=user_data.phone
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[schemas.User])
async def get_users(
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех пользователей (только для администраторов)"""
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о пользователе по ID"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра данных другого пользователя"
        )
    
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление данных пользователя"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения данных другого пользователя"
        )

    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    update_data = user_data.model_dump(exclude_unset=True)
    
    if "role" in update_data and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может менять роль пользователя"
        )

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Удаление пользователя (только для администраторов)"""
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    await db.delete(db_user)
    await db.commit()
    return {"message": "Пользователь удален"}

@router.post("/{user_id}/make-admin")
async def make_user_admin(
    user_id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Назначение пользователя администратором (только для администраторов)"""
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    db_user.role = "admin"
    await db.commit()
    await db.refresh(db_user)
    return {"message": "Пользователь назначен администратором"} 