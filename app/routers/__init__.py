from fastapi import FastAPI
from app.routers import orders, products, countries, categories, reviews, users

# Функция для регистрации всех маршрутов в приложении
def init_routes(app: FastAPI):
    app.include_router(users.router)
    app.include_router(products.router)
    app.include_router(orders.router)
    app.include_router(countries.router)
    app.include_router(categories.router)
    app.include_router(reviews.router)