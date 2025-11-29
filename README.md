# E-Commerce API

A fully functional RESTful e-commerce API built with Flask, SQLAlchemy, Marshmallow, and MySQL.

## Features

- **User Management**: Full CRUD operations for users
- **Product Management**: Full CRUD operations for products
- **Order Management**: Create orders, add/remove products, view order history
- **Database Relationships**: 
  - One-to-Many: Users to Orders
  - Many-to-Many: Orders to Products
- **Data Validation**: Marshmallow schemas for input validation and serialization
- **Duplicate Prevention**: Prevents duplicate products in orders

## Technology Stack

- **Backend**: Flask
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Serialization**: Marshmallow
- **Database Connection**: MySQL Connector

## Setup Instructions

### 1. Create MySQL Database

Open MySQL Workbench and run:

```sql
CREATE DATABASE ecommerce_api;
```

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd ecommerce-api
```

### 3. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Database Connection

Open `app.py` and update line 13 with your MySQL password:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/ecommerce_api'
```

Replace `YOUR_PASSWORD` with your actual MySQL root password.

### 6. Initialize Database Tables

Start the Flask application:

```bash
python app.py
```

Then visit `http://localhost:5000/init-db` in your browser or use curl:

```bash
curl http://localhost:5000/init-db
```

This will create all necessary tables in your MySQL database.

## API Endpoints

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Retrieve all users |
| GET | `/users/<id>` | Retrieve a user by ID |
| POST | `/users` | Create a new user |
| PUT | `/users/<id>` | Update a user by ID |
| DELETE | `/users/<id>` | Delete a user by ID |

#### Example: Create User

```json
POST /users
{
  "name": "John Doe",
  "email": "john@example.com",
  "address": "123 Main St, City, State"
}
```

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | Retrieve all products |
| GET | `/products/<id>` | Retrieve a product by ID |
| POST | `/products` | Create a new product |
| PUT | `/products/<id>` | Update a product by ID |
| DELETE | `/products/<id>` | Delete a product by ID |

#### Example: Create Product

```json
POST /products
{
  "product_name": "Laptop",
  "price": 999.99
}
```

### Order Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create a new order |
| PUT | `/orders/<order_id>/add_product/<product_id>` | Add a product to an order |
| DELETE | `/orders/<order_id>/remove_product/<product_id>` | Remove a product from an order |
| GET | `/orders/user/<user_id>` | Get all orders for a user |
| GET | `/orders/<order_id>/products` | Get all products for an order |

#### Example: Create Order

```json
POST /orders
{
  "user_id": 1,
  "order_date": "2024-11-28T10:30:00"
}
```

Note: `order_date` is optional and will default to current time if not provided.

#### Example: Add Product to Order

```
PUT /orders/1/add_product/1
```

## Database Schema

### Users Table
- `id`: Integer, Primary Key
- `name`: String(100), Not Null
- `email`: String(100), Unique, Not Null
- `address`: String(200)

### Products Table
- `id`: Integer, Primary Key
- `product_name`: String(100), Not Null
- `price`: Float, Not Null

### Orders Table
- `id`: Integer, Primary Key
- `order_date`: DateTime, Not Null
- `user_id`: Integer, Foreign Key → Users

### Order_Product Association Table
- `order_id`: Integer, Foreign Key → Orders
- `product_id`: Integer, Foreign Key → Products
- Composite Primary Key: (order_id, product_id)

## Testing with Postman

1. Import the provided Postman collection (`ecommerce_api_postman_collection.json`)
2. Test each endpoint in sequence:
   - Create users
   - Create products
   - Create orders
   - Add products to orders
   - Retrieve data
   - Update records
   - Delete records

## Project Structure

```
ecommerce-api/
│
├── app.py                              # Main Flask application
├── requirements.txt                     # Python dependencies
├── README.md                           # Project documentation
└── ecommerce_api_postman_collection.json  # Postman test collection
```

## Error Handling

The API includes comprehensive error handling:
- 404: Resource not found
- 400: Bad request (validation errors, duplicates)
- 500: Server errors


## Common Issues and Solutions

### Issue: Can't connect to MySQL
**Solution**: Ensure MySQL server is running and credentials are correct in `app.py`

### Issue: Table already exists error
**Solution**: Drop existing tables in MySQL Workbench or use a fresh database

### Issue: Foreign key constraint fails
**Solution**: Ensure referenced records (users, products) exist before creating relationships

