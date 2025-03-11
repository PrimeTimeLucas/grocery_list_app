from app import app
from models import db, User, GroceryList  # Explicit model imports

with app.app_context():
    db.create_all()
    print('Database tables created!')  # Add confirmation message
