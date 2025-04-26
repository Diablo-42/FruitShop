from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_routes(app)

@app.get("/")
async def read_root():
    return {"message": "Добро пожаловать в API фруктовой лавки!"}