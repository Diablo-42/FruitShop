import os

from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.utils.db import get_db
from backend.src import models, schemas

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY не найден в переменных окружения")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_by_username(db: AsyncSession, username: str) -> models.User | None:
    """Получает пользователя из БД по имени пользователя."""
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    """Получает пользователя из БД по ID."""
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def decode_access_token(token: str = Depends(oauth2_scheme)) -> schemas.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительные учетные данные (токен)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("user_id")
        role: str | None = payload.get("role")

        if username is None or user_id is None or role is None:
            raise credentials_exception

        token_data = schemas.TokenData(username=username, user_id=user_id, role=role)

    except JWTError:
        raise credentials_exception
    return token_data

async def get_current_user(
    token_data: schemas.TokenData = Depends(decode_access_token),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    if token_data.user_id is None:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительные учетные данные (нет user_id в токене)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь из токена не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Неактивный пользователь")
    return current_user

def has_role(required_role: str):
    async def role_checker(current_user: models.User = Depends(get_current_active_user)) -> models.User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав (требуется роль: {required_role})",
            )
        return current_user
    return role_checker