from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, GroceryList

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
jwt = JWTManager(app)

# Auth routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify(message='Username already exists'), 400
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message='User created'), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify(message='Invalid credentials'), 401

# Grocery list routes
@app.route('/lists', methods=['POST'])
@jwt_required()
def create_list():
    current_user_id = get_jwt_identity()
    new_list = GroceryList(
        user_id=current_user_id,
        items=request.json.get('items', [])
    )
    db.session.add(new_list)
    db.session.commit()
    return jsonify(new_list.id), 201

@app.route('/lists', methods=['GET'])
@jwt_required()
def get_lists():
    current_user_id = get_jwt_identity()
    lists = GroceryList.query.filter_by(user_id=current_user_id).all()
    return jsonify([{'id': l.id, 'items': l.items} for l in lists]), 200

# Add update and delete endpoints similarly

if __name__ == '__main__':
    app.run()
