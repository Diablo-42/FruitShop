from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from backend.src.utils.db import Base
from backend.src.schemas import UnitType, OrderStatusEnum
import datetime

class Order(Base):
    __tablename__ = 'orders'
    id_order = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    order_date = Column(DateTime, default=datetime.datetime.now)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False)
       
    user = relationship("User", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = 'products'
    id_product = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    id_country = Column(Integer, ForeignKey('countries.id_country'))
    id_category = Column(Integer, ForeignKey('categories.id_category'))
    price_per_unit = Column(Float)
    unit_type = Column(Enum(UnitType))
    expiration_date = Column(Date)
    
    country = relationship("Country", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_details = relationship("OrderDetail", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

class Country(Base):
    __tablename__ = 'countries'
    id_country = Column(Integer, primary_key=True, index=True)
    name_country = Column(String(100))
    
    products = relationship("Product", back_populates="country")

class Review(Base):
    __tablename__ = 'reviews'
    id_review = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey('users.id')) 
    id_product = Column(Integer, ForeignKey('products.id_product'))
    rating = Column(Integer)
    comment = Column(Text)
       
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

class Category(Base):
    __tablename__ = 'categories'
    id_category = Column(Integer, primary_key=True, index=True)
    name_category = Column(String(100))

    products = relationship("Product", back_populates="category")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user", nullable=False)
    full_name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

class OrderDetail(Base):
    __tablename__ = "order_details"

    id_order_detail = Column(Integer, primary_key=True, index=True)
    id_order = Column(Integer, ForeignKey("orders.id_order"))
    id_product = Column(Integer, ForeignKey("products.id_product"))
    quantity = Column(Float, nullable=False)
    unit_type = Column(Enum(UnitType), nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product", back_populates="order_details") 