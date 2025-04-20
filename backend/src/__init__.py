from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.src.api import init_routes
from backend.src.utils.db import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Создаем экземпляр FastAPI
app = FastAPI(
    title="Fruit Shop API",
    description="API для управления фруктовой лавкой",
    version="1.0.0",
    lifespan=lifespan
)

init_routes(app)

@app.get("/")
async def read_root():
    """
    Главная страница API
    """
    return {"message": "Добро пожаловать в API фруктовой лавки!"}