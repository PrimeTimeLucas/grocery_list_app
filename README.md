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
    "items": ["item1", "item2"]
}
```
- Response: `201 Created` with list ID

**Get All Lists**
- `GET /lists`
- Headers: `Authorization: Bearer <jwt_token>`
- Response: `200 OK` with array of lists
```json
[
    {
        "id": 1,
        "items": ["item1", "item2"]
    }
]
```

**Update List**
- `PUT /lists/<list_id>`
- Headers: `Authorization: Bearer <jwt_token>`
- Request body:
```json
{
    "items": ["updated_item1", "updated_item2"]
}
```
- Response: `200 OK` with success message

**Delete List**
- `DELETE /lists/<list_id>`
- Headers: `Authorization: Bearer <jwt_token>`
- Response: `200 OK` with success message

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
