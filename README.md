# API endpoints
## Category 

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/category/all` | Получение списка всех категорий |
| GET | `/category/{id}` | Получение категории по ID |
| GET | `/category/{id}/products` | Получение всех продуктов по ID категории |
| POST | `/category` | Добавление новой категории |
| PUT | `/category/{id}` | Обновление категории по ID |
| DELETE | `/category/{id}` | Удаление категории по ID |

## Country 

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/country/all` | Получение списка всех стран |
| GET | `/country/{id}` | Получение страны по ID |
| POST | `/country` | Добавление новой страны |
| PUT | `/country/{id}` | Обновление страны по ID |
| DELETE | `/country/{id}` | Удаление страны по ID |

## Orders 

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/all` | Получение списка всех заказов |
| GET | `/orders/{id}` | Получение заказа по ID |
| GET | `/orders/{id}/item/{itemid}` | Получение информации о продукте из заказа |
| POST | `/orders` | Создание нового заказа |
| PUT | `/orders/{id}` | Обновление заказа по ID |
| DELETE | `/orders/{id}` | Удаление заказа по ID |

## Product

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product/all` | Получение списка всех товаров |
| GET | `/product/{id}` | Получение товара по ID |
| GET | `/product/country/{id}` | Получение товаров по ID страны |
| POST | `/product` | Добавление нового товара |
| PUT | `/product/{id}` | Обновление товара по ID |
| DELETE | `/product/{id}` | Удаление товара по ID |

## Review 

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/review/all` | Получение списка всех отзывов |
| GET | `/review/{id}` | Получение отзыва по ID |
| GET | `/review/product/{id}` | Получение всех отзывов по ID продукта  |
| GET | `/review/client/{id}` | Получение всех отзывов по ID клиента |
| POST | `/review` | Добавление нового отзыва |
| PUT | `/review/{id}` | Обновление отзыва по ID |
| DELETE | `/review/{id}` | Удаление отзыва по ID |

## Swagger
  `/docs`
