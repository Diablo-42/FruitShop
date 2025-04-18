from fastapi import FastAPI
from app.routers import orders, products, clients, countries, categories, reviews, auth, order_details

# Функция для регистрации всех маршрутов в приложении
def init_routes(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(products.router)
    app.include_router(clients.router)
    app.include_router(countries.router)
    app.include_router(categories.router)
    app.include_router(reviews.router)