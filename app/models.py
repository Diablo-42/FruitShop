from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from app.utils.db import Base
import datetime
import enum

class UnitType(str, enum.Enum):
    KG = "кг"
    PIECE = "шт"

class Order(Base):
    __tablename__ = 'orders'
    id_order = Column(Integer, primary_key=True, index=True)
    id_client = Column(Integer, ForeignKey('clients.id_client'))
    order_date = Column(DateTime, default=datetime.datetime.now)
    total_amount = Column(Float, default=0)  # Общая сумма заказа
    
    client = relationship("Client", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")

class Product(Base):
    __tablename__ = 'products'
    id_product = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    id_country = Column(Integer, ForeignKey('countries.id_country'))
    id_category = Column(Integer, ForeignKey('categories.id_category'))
    price_per_unit = Column(Float)
    unit_type = Column(Enum(UnitType))
    expiration_date = Column(Integer)
    
    country = relationship("Country", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_details = relationship("OrderDetail", back_populates="product")
    reviews = relationship("Review", back_populates="product")

class Country(Base):
    __tablename__ = 'countries'
    id_country = Column(Integer, primary_key=True, index=True)
    name_country = Column(String(100))
    
    products = relationship("Product", back_populates="country")

class Client(Base):
    __tablename__ = 'clients'
    id_client = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    surname = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(100))
    
    orders = relationship("Order", back_populates="client")
    reviews = relationship("Review", back_populates="client")

class Review(Base):
    __tablename__ = 'reviews'
    id_review = Column(Integer, primary_key=True, index=True)
    id_client = Column(Integer, ForeignKey('clients.id_client'))
    id_product = Column(Integer, ForeignKey('products.id_product'))
    rating = Column(Integer)
    comment = Column(Text)
    
    client = relationship("Client", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

class Category(Base):
    __tablename__ = 'categories'
    id_category = Column(Integer, primary_key=True, index=True)
    name_category = Column(String(100))

    products = relationship("Product", back_populates="category")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")

class OrderDetail(Base):
    __tablename__ = "order_details"

    id_order_detail = Column(Integer, primary_key=True, index=True)
    id_order = Column(Integer, ForeignKey("orders.id_order"))
    id_product = Column(Integer, ForeignKey("products.id_product"))
    quantity = Column(Float)  # Количество (может быть дробным для кг)
    unit_type = Column(Enum(UnitType))  # Тип единицы измерения (кг/шт)
    price = Column(Float)  # Цена на момент заказа

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details") 