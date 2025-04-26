from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# --- Страны ---
class CountryBase(BaseModel):
    name_country: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    id_country: int

    class Config:
        from_attributes = True

# --- Категории ---
class CategoryBase(BaseModel):
    name_category: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id_category: int

    class Config:
        from_attributes = True

# --- Продукты ---
class UnitType(str, Enum):
    KG = "кг"
    PIECE = "шт"

class ProductBase(BaseModel):
    name: str
    price_per_unit: float
    unit_type: UnitType
    expiration_date: date

class ProductCreate(ProductBase):
    id_country: int
    id_category: int

class ProductUpdate(BaseModel):
    name: str | None = None
    price_per_unit: float | None = None
    unit_type: UnitType | None = None
    expiration_date: date | None = None
    id_country: int | None = None
    id_category: int | None = None

class Product(ProductBase):
    id_product: int
    country: Country
    category: Category

    class Config:
        from_attributes = True

class ProductInCart(ProductBase):
    id_product: int
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Корзины ---
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id_cart_item: int
    user_id: int
    product: ProductInCart

    model_config = ConfigDict(from_attributes=True)

# --- Детали Заказа ---
class OrderDetailBase(BaseModel):
    id_product: int
    quantity: float

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetail(OrderDetailBase):
    id_order_detail: int
    id_order: int
    unit_type: UnitType
    price: float

    class Config:
        from_attributes = True

# --- Заказы ---
class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    id_user: int

class OrderCreate(OrderBase):
    order_details: List[OrderDetailCreate]

class OrderUpdate(BaseModel):
    status: OrderStatusEnum | None = None

class Order(OrderBase):
    id_order: int
    order_date: datetime
    total_amount: float
    status: OrderStatusEnum
    order_details: List[OrderDetail]

    class Config:
        from_attributes = True

# --- Отзывы ---
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str

class ReviewCreate(ReviewBase):
    id_user: int
    id_product: int

class ReviewUpdate(ReviewBase):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Review(ReviewBase):
    id_review: int
    id_user: int
    id_product: int

    class Config:
        from_attributes = True

# --- Пользователи ---
class UserProfileUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    address: str | None = None
    phone: str | None = None
    password: str | None = None

class UserAdminUpdate(UserProfileUpdate):
    role: str | None = None
    is_active: bool | None = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    email: str
    password: str
    full_name: str | None = None
    address: str | None = None
    phone: str | None = None

class UserPublic(UserBase):
    id: int
    full_name: str | None = None

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    email: str
    full_name: str | None = None
    address: str | None = None
    phone: str | None = None
    is_active: bool
    role: str

    class Config:
        from_attributes = True
        
# --- Токены ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None
    role: str | None = None