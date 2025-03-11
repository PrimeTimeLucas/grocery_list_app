from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, GroceryList, GroceryItem

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
    data = request.get_json()
    
    if not request.is_json or 'items' not in data:
        return jsonify(message='Missing items in request'), 400
        
    if not isinstance(data['items'], list):
        return jsonify(message='Items must be an array'), 400
    
    new_list = GroceryList(
        user_id=current_user_id,
        store_name=data.get('store_name')
    )
    
    # Add items with validation
    for item in data['items']:
        if not isinstance(item, dict) or 'name' not in item or 'price' not in item:
            return jsonify(message='Each item must have name and price'), 400
            
        try:
            price = float(item['price'])
        except (ValueError, TypeError):
            return jsonify(message='Price must be a number'), 400
            
        new_item = GroceryItem(
            name=item['name'],
            price=price,
            store=item.get('store') or data.get('store_name')
        )
        new_list.items.append(new_item)
    
    db.session.add(new_list)
    db.session.commit()
    
    return jsonify({
        'id': new_list.id,
        'total': float(sum(float(item.price) for item in new_list.items))
    }), 201

@app.route('/lists', methods=['GET'])
@jwt_required()
def get_lists():
    current_user_id = int(get_jwt_identity())
    lists = GroceryList.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([{
        'id': l.id,
        'store': l.store_name,
        'total': float(sum(float(item.price) for item in l.items)),
        'item_count': len(l.items),
        'created_at': l.created_at.isoformat() if l.created_at else None
    } for l in lists]), 200

@app.route('/lists/<int:list_id>', methods=['GET'])
@jwt_required()
def get_list(list_id):
    current_user_id = int(get_jwt_identity())
    grocery_list = GroceryList.query.filter_by(
        id=list_id, 
        user_id=current_user_id
    ).first()
    
    if not grocery_list:
        return jsonify(message='List not found'), 404
    
    return jsonify({
        'id': grocery_list.id,
        'store': grocery_list.store_name,
        'total': float(sum(float(item.price) for item in grocery_list.items)),
        'items': [{
            'name': item.name,
            'price': float(item.price),
            'store': item.store
        } for item in grocery_list.items]
    }), 200

# Update endpoint
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
    
    data = request.get_json()
    if not data:
        return jsonify(message='Missing request data'), 400
    
    # Update store name if provided
    if 'store_name' in data:
        grocery_list.store_name = data['store_name']
    
    # Update items if provided
    if 'items' in data:
        if not isinstance(data['items'], list):
            return jsonify(message='Items must be an array'), 400
        
        # Clear existing items
        for item in grocery_list.items:
            db.session.delete(item)
        
        # Add new items
        for item in data['items']:
            if not isinstance(item, dict) or 'name' not in item or 'price' not in item:
                return jsonify(message='Each item must have name and price'), 400
                
            try:
                price = float(item['price'])
            except (ValueError, TypeError):
                return jsonify(message='Price must be a number'), 400
                
            new_item = GroceryItem(
                name=item['name'],
                price=price,
                store=item.get('store') or grocery_list.store_name
            )
            grocery_list.items.append(new_item)
    
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

@app.route('/stats/monthly', methods=['GET'])
@jwt_required()
def monthly_stats():
    current_user_id = int(get_jwt_identity())
    
    # Get all lists for the user
    lists = GroceryList.query.filter_by(user_id=current_user_id).all()
    
    # Group by month
    monthly_totals = {}
    for grocery_list in lists:
        if not grocery_list.created_at:
            continue
            
        month_key = grocery_list.created_at.strftime('%Y-%m')
        if month_key not in monthly_totals:
            monthly_totals[month_key] = {
                'total': 0,
                'list_count': 0,
                'stores': {}
            }
        
        # Calculate list total
        list_total = sum(float(item.price) for item in grocery_list.items)
        
        # Update monthly stats
        monthly_totals[month_key]['total'] += list_total
        monthly_totals[month_key]['list_count'] += 1
        
        # Track spending by store
        store = grocery_list.store_name or 'Unknown'
        if store not in monthly_totals[month_key]['stores']:
            monthly_totals[month_key]['stores'][store] = 0
        monthly_totals[month_key]['stores'][store] += list_total
    
    # Convert to sorted list for response
    result = []
    for month, data in sorted(monthly_totals.items(), reverse=True):
        result.append({
            'month': month,
            'total': round(data['total'], 2),
            'list_count': data['list_count'],
            'stores': {store: round(amount, 2) for store, amount in data['stores'].items()}
        })
    
    return jsonify(result), 200

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
