from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Модели для стран
class CountryBase(BaseModel):
    name_country: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    id_country: int

    class Config:
        from_attributes = True

# Модели для категорий
class CategoryBase(BaseModel):
    name_category: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id_category: int

    class Config:
        from_attributes = True

# Модели для продуктов
class UnitType(str, Enum):
    KG = "кг"
    PIECE = "шт"

class ProductBase(BaseModel):
    name: str
    id_country: int
    id_category: int
    price_per_unit: float
    unit_type: UnitType
    expiration_date: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id_product: int

    class Config:
        from_attributes = True

# Модели для клиентов
class ClientBase(BaseModel):
    name: str
    surname: str
    phone_number: str
    email: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id_client: int

    class Config:
        from_attributes = True

# Модели для заказов
class OrderDetailBase(BaseModel):
    id_product: int
    quantity: float
    unit_type: UnitType
    price: float

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetail(OrderDetailBase):
    id_order_detail: int
    id_order: int

    class Config:
        from_attributes = True

class OrderDetailUpdate(BaseModel):
    quantity: Optional[float] = None
    unit_type: Optional[UnitType] = None
    price: Optional[float] = None

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    id_client: int

class OrderCreate(OrderBase):
    order_details: List[OrderDetailCreate]

class Order(OrderBase):
    id_order: int
    order_date: datetime
    total_amount: float
    order_details: List[OrderDetail]

    class Config:
        from_attributes = True

# Модели для отзывов
class ReviewBase(BaseModel):
    id_client: int
    id_product: int
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id_review: int

    class Config:
        from_attributes = True 

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str = None 
    role: str = None  

class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None