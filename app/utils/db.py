from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Config 
from typing import AsyncGenerator

engine = create_async_engine(
    Config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()