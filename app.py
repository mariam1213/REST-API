from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
# Set up SQL Alchemy database URI(Uniform Resource Identifier), making sure we can correctly locate the database file

with app.app_context():
    from flask import current_app
    app_instance = current_app

basedir = os.path.abspath(os.path.dirname(__file__))        # Base directory        
# __file__ is a variable that contains the path to the module that is currently being imported

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
# This will look for the fil in the current folder structure
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Not needed nut if it is not made the console will warn us

# Init database
db = SQLAlchemy(app)    

# Init marshmallow
ma = Marshmallow(app)


# Product Class/Model
class Product(db.Model):             # Where we add all of our fields
    id = db.Column(db.Integer, primary_key=True)                   # The way we assign fields (db.column)                          
                # (data type, set as primary key - auto increment by default)

    name = db.Column(db.String(100), unique=True)
                  # (String(char limit set), only product that can have this name )
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    # Init/Constructor
    def __init__(self, name, description, price, qty):      # When these are passed in we want ot add them to the instance
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty
# NOTE: When building a real production API, you would put the classes in different files
# Search flask-sqlalchemy documentation, section: Minimal Application, shows template on class creation and
# how to add catgories to APIs 

# Product Schema
class ProductSchema(ma.Schema):         # Marshmaellow is used
    class Meta:                         # Fields we are allowed/want to show
        fields = ('id', 'name', 'description', 'price', 'qty')      # Everything is shown, if GET requested is made

# Init Schema
product_schema = ProductSchema()     # If not provided console will warn us
products_schema = ProductSchema(many=True)                                # This is needed because we can deal with muliple products

with app.app_context():
    db.create_all()


# Create our Routes/Endpoints - how we interact with our database
# Create a Product
@app.route('/product', methods=['POST'])        # Method is restricted to POST
def add_product():                              # "get" request  
    # When making our requests we are attaching fields
    name = request.json['name']                 # Variables set to fetch this data, using request
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    new_product = Product(name, description, price, qty)        # Set new variable to Product class - instantaiting an object
                                                                
    db.session.add(new_product)                                 # Call to add new_prodcut     

    db.session.commit()                                         # Saves to the database

    return product_schema.jsonify(new_product)                  # What gets returned to the client

# Get All Products
@app.route('/product', methods=['GET'])
def get_products():                                             # Create a function 
    all_products = Product.query.all()                          # Product class has a method called query, gets all products for us
    result = products_schema.dump(all_products)
    return jsonify({'data' : result})                                 # result created above
                                                                # has a property called data that gives you the list of data - products
# Get single Product
@app.route('/product/<id>', methods=['GET'])                    # Query parameter <id> is added to amek sure we can find single item - 
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product) 

# Update a Product
@app.route('/product/<id>', methods=['PUT'])                    # When updating on the server, a PUT request is used
def update_product(id):
    product = Product.query.get(id)                             # Fetch the product, pass in specific id
    name = request.json['name'] 
    description = request.json['description']
    price = request.json['price']
    qty = request.json['qty']

    product.name = name                                                     # Construct a new product to submit to the database
    product.description = description
    product.price = price
    product.qty = qty

    db.session.commit()

    return product_schema.jsonify(product)

# Delet Product
@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product) 


# Run server

if __name__ == '__main__':
    app.run(debug=True)
