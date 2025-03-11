# Grocery List App

## API Documentation

### Authentication Endpoints

**Register User**
- `POST /register`
- Request body:
```json
{
    "username": "string",
    "password": "string"
}
```

**Login**
- `POST /login`
- Returns JWT token for authenticated requests

### Grocery List Endpoints

**Create List**
- `POST /lists`
- Headers: `Authorization: Bearer <jwt_token>`
- Request body:
```json
{
    "store_name": "Supermarket ABC",
    "items": [
        {
            "name": "Milk",
            "price": 2.99,
            "store": "Dairy Section"
        },
        {
            "name": "Bread",
            "price": 3.49
        }
    ]
}
```
- Response: `201 Created` with list ID and total
```json
{
    "id": 1,
    "total": 6.48
}
```

**Get All Lists**
- `GET /lists`
- Headers: `Authorization: Bearer <jwt_token>`
- Response: `200 OK` with array of lists
```json
[
    {
        "id": 1,
        "store": "Supermarket ABC",
        "total": 6.48,
        "item_count": 2,
        "created_at": "2023-04-15T14:30:45"
    }
]
```

**Get List Details**
- `GET /lists/<list_id>`
- Headers: `Authorization: Bearer <jwt_token>`
- Response: `200 OK` with list details
```json
{
    "id": 1,
    "store": "Supermarket ABC",
    "total": 6.48,
    "items": [
        {
            "name": "Milk",
            "price": 2.99,
            "store": "Dairy Section"
        },
        {
            "name": "Bread",
            "price": 3.49,
            "store": "Supermarket ABC"
        }
    ]
}
```

**Update List**
- `PUT /lists/<list_id>`
- Headers: `Authorization: Bearer <jwt_token>`
- Request body:
```json
{
    "store_name": "Updated Store",
    "items": [
        {
            "name": "Updated Item",
            "price": 4.99
        }
    ]
}
```
- Response: `200 OK` with success message

**Delete List**
- `DELETE /lists/<list_id>`
- Headers: `Authorization: Bearer <jwt_token>`
- Response: `200 OK` with success message

**Monthly Spending Stats**
- `GET /stats/monthly`
- Headers: `Authorization: Bearer <jwt_token>`
- Response: `200 OK` with monthly spending data
```json
[
    {
        "month": "2023-04",
        "total": 125.45,
        "list_count": 5,
        "stores": {
            "Supermarket ABC": 75.20,
            "Farmers Market": 50.25
        }
    },
    {
        "month": "2023-03",
        "total": 98.75,
        "list_count": 4,
        "stores": {
            "Supermarket ABC": 98.75
        }
    }
]
```

## Setup Instructions

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Initialize database:
```bash
python init_db.py
```

3. Start server:
```bash
python app.py
```

## Testing
Run the test notebook:
```bash
jupyter notebook Grocery_List_API_Test.ipynb
```
