from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.utils.security import get_current_active_user, has_role

from app.utils.db import get_db
from app import models, schemas

router = APIRouter(
    prefix="/client",
    tags=["clients"],
    responses={404: {"description": "Not found"}, 401: {"description": "Unauthorized"}},
)

@router.get("/all", response_model=List[schemas.Client])
async def get_all_clients(
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех клиентов (только для администраторов)
    """
    result = await db.execute(select(models.Client))
    clients = result.scalars().all()
    return clients

@router.get("/{id}", response_model=schemas.Client)
async def get_client(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение клиента по ID (требуется авторизация)
    """
    if current_user.role != "admin" and current_user.id != id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    result = await db.execute(select(models.Client).filter(models.Client.id_client == id))
    client = result.scalars().first()
    if client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@router.get("/{id}/orders", response_model=List[schemas.Order])
async def get_client_orders(
    id: int,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение всех заказов клиента по его ID (требуется авторизация)
    """
    if current_user.role != "admin" and current_user.id != id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    result = await db.execute(select(models.Order).filter(models.Order.id_client == id))
    orders = result.scalars().all()
    return orders

@router.post("", response_model=schemas.Client, status_code=201)
async def add_client(
    client: schemas.ClientCreate,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Добавление нового клиента (только для администраторов)
    """
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

@router.put("/{id}", response_model=schemas.Client)
async def update_client(
    id: int,
    client: schemas.ClientCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление клиента по ID (требуется авторизация)
    """
    if current_user.role != "admin" and current_user.id != id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    result = await db.execute(select(models.Client).filter(models.Client.id_client == id))
    db_client = result.scalars().first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    for key, value in client.model_dump().items():
        setattr(db_client, key, value)
    
    await db.commit()
    await db.refresh(db_client)
    return db_client

@router.delete("/{id}")
async def delete_client(
    id: int,
    current_user: schemas.User = Depends(has_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление клиента по ID (только для администраторов)
    """
    result = await db.execute(select(models.Client).filter(models.Client.id_client == id))
    db_client = result.scalars().first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    await db.delete(db_client)
    await db.commit()
    return {"message": "Клиент удален"}