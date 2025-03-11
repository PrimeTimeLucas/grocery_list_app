from app import app
from models import db, User, GroceryList, GroceryItem  # Import all models

with app.app_context():
    db.drop_all()  # Drop existing tables
    db.create_all()  # Create new tables with current schema
    print('Database schema updated successfully!')
