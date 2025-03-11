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
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    return jsonify(message='Invalid credentials'), 401

# Grocery list routes
@app.route('/lists', methods=['POST'])
@jwt_required()
def create_list():
    current_user_id = int(get_jwt_identity())
    
    if not request.is_json or 'items' not in request.json:
        return jsonify(message='Missing items in request'), 400
        
    if not isinstance(request.json['items'], list):
        return jsonify(message='Items must be an array'), 400
    
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
    current_user_id = int(get_jwt_identity())
    lists = GroceryList.query.filter_by(user_id=current_user_id).all()
    return jsonify([{'id': l.id, 'items': l.items} for l in lists]), 200

# Add update and delete endpoints similarly
@app.route('/lists/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_list(list_id):
    current_user_id = int(get_jwt_identity())
    grocery_list = GroceryList.query.filter_by(
        id=list_id, 
        user_id=current_user_id
    ).first()
    
    if not grocery_list:
        return jsonify(message='List not found'), 404
    
    if not request.is_json or 'items' not in request.json:
        return jsonify(message='Missing items in request'), 400
        
    if not isinstance(request.json['items'], list):
        return jsonify(message='Items must be an array'), 400
    
    grocery_list.items = request.json.get('items', grocery_list.items)
    db.session.commit()
    return jsonify(message='List updated'), 200

@app.route('/lists/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    current_user_id = int(get_jwt_identity())
    grocery_list = GroceryList.query.filter_by(
        id=list_id, 
        user_id=current_user_id
    ).first()
    
    if not grocery_list:
        return jsonify(message='List not found'), 404
    
    db.session.delete(grocery_list)
    db.session.commit()
    return jsonify(message='List deleted'), 200

# Error handlers
@app.errorhandler(422)
def handle_unprocessable_entity(err):
    return jsonify({
        "message": "Validation error",
        "errors": getattr(err, 'data', {}).get('messages', ["Invalid request data"])
    }), 422

@app.errorhandler(400)
def handle_bad_request(err):
    return jsonify({"message": "Bad request", "error": str(err)}), 400

@app.errorhandler(404)
def handle_not_found(err):
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(500)
def handle_server_error(err):
    return jsonify({"message": "Internal server error"}), 500

if __name__ == '__main__':
    app.run()
