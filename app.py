from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Database configuration
# IMPORTANT: Replace <YOUR PASSWORD> with your actual MySQL root password
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:40Lamonerie%40@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)


# ==================== DATABASE MODELS ====================

# Association table for Many-to-Many relationship between Orders and Products
order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # One-to-Many relationship: One User can have many Orders
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Many-to-Many relationship: Many Orders can have many Products
    products = db.relationship('Product', secondary=order_product, backref='orders', lazy='dynamic')
    
    def __repr__(self):
        return f'<Order {self.id}>'


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Product {self.product_name}>'


# ==================== MARSHMALLOW SCHEMAS ====================

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
    
    name = fields.String(required=True)
    email = fields.Email(required=True)
    address = fields.String()


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
    
    product_name = fields.String(required=True)
    price = fields.Float(required=True)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        include_fk = True
    
    order_date = fields.DateTime()
    user_id = fields.Integer(required=True)
    products = fields.Nested(ProductSchema, many=True)


# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


# ==================== USER ENDPOINTS ====================

@app.route('/users', methods=['GET'])
def get_users():
    """Retrieve all users"""
    try:
        users = User.query.all()
        return jsonify(users_schema.dump(users)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """Retrieve a user by ID"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        # Validate and deserialize input
        user_data = user_schema.load(request.json)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=user_data.email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        
        db.session.add(user_data)
        db.session.commit()
        
        return jsonify(user_schema.dump(user_data)), 201
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    """Update a user by ID"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get the data from request
        data = request.json
        
        # Check if email is being updated and if it already exists
        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update fields
        if 'name' in data:
            user.name = data['name']
        if 'address' in data:
            user.address = data['address']
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """Delete a user by ID"""
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== PRODUCT ENDPOINTS ====================

@app.route('/products', methods=['GET'])
def get_products():
    """Retrieve all products"""
    try:
        products = Product.query.all()
        return jsonify(products_schema.dump(products)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """Retrieve a product by ID"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        # Validate and deserialize input
        product_data = product_schema.load(request.json)
        
        db.session.add(product_data)
        db.session.commit()
        
        return jsonify(product_schema.dump(product_data)), 201
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    """Update a product by ID"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get the data from request
        data = request.json
        
        # Update fields
        if 'product_name' in data:
            product.product_name = data['product_name']
        if 'price' in data:
            product.price = data['price']
        
        db.session.commit()
        
        return jsonify(product_schema.dump(product)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Delete a product by ID"""
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ORDER ENDPOINTS ====================

@app.route('/orders', methods=['POST'])
def create_order():
    """Create a new order (requires user ID and order date)"""
    try:
        data = request.json
        
        # Validate user exists
        user = User.query.get(data.get('user_id'))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create order
        order = Order(
            user_id=data['user_id'],
            order_date=datetime.fromisoformat(data['order_date']) if 'order_date' in data else datetime.utcnow()
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify(order_schema.dump(order)), 201
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    """Add a product to an order (prevent duplicates)"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product is already in the order (prevent duplicates)
        if product in order.products:
            return jsonify({'error': 'Product already in order'}), 400
        
        order.products.append(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product added to order successfully',
            'order': order_schema.dump(order)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    """Remove a product from an order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product is in the order
        if product not in order.products:
            return jsonify({'error': 'Product not in order'}), 400
        
        order.products.remove(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product removed from order successfully',
            'order': order_schema.dump(order)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        orders = Order.query.filter_by(user_id=user_id).all()
        return jsonify(orders_schema.dump(orders)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_order_products(order_id):
    """Get all products for an order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        products = order.products.all()
        return jsonify(products_schema.dump(products)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== DATABASE INITIALIZATION ====================

@app.route('/init-db', methods=['GET'])
def init_db():
    """Initialize database tables"""
    try:
        db.create_all()
        return jsonify({'message': 'Database tables created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== HOME ROUTE ====================

@app.route('/', methods=['GET'])
def home():
    """Home route with API information"""
    return jsonify({
        'message': 'E-Commerce API',
        'endpoints': {
            'users': {
                'GET /users': 'Get all users',
                'GET /users/<id>': 'Get user by ID',
                'POST /users': 'Create new user',
                'PUT /users/<id>': 'Update user',
                'DELETE /users/<id>': 'Delete user'
            },
            'products': {
                'GET /products': 'Get all products',
                'GET /products/<id>': 'Get product by ID',
                'POST /products': 'Create new product',
                'PUT /products/<id>': 'Update product',
                'DELETE /products/<id>': 'Delete product'
            },
            'orders': {
                'POST /orders': 'Create new order',
                'PUT /orders/<order_id>/add_product/<product_id>': 'Add product to order',
                'DELETE /orders/<order_id>/remove_product/<product_id>': 'Remove product from order',
                'GET /orders/user/<user_id>': 'Get all orders for a user',
                'GET /orders/<order_id>/products': 'Get all products for an order'
            }
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True)