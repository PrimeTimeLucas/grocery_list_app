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

**Get All Lists**
- `GET /lists`
- Headers: `Authorization: Bearer <jwt_token>`

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
