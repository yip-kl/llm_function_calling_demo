# Create a flask application to interact with the database with CRUD operations
# This file contains the API for the database operations

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Initialize the flask application
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize the database
db = SQLAlchemy(app)
# Initialize the marshmallow
ma = Marshmallow(app)

# Create a class for the database model

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(255), nullable=False)
    name_cn = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, name_en, name_cn, category, price, quantity):
        self.name_en = name_en
        self.name_cn = name_cn
        self.category = category
        self.price = price
        self.quantity = quantity

# Create a schema for the database model
class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name_en', 'name_cn', 'category', 'price', 'quantity')

# Initialize the schema
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

# Add sample data to the database
app.app_context().push()
db.create_all()
initial_items = [
    Item('Water', '水', 'Food and beverages', 1.0, 100),
    Item('Coca-cola', '可樂', 'Food and beverages', 2.0, 200),
    Item('Hamburger', '漢堡包', 'Food and beverages', 13.0, 0),
    Item('Fried rice', '炒飯', 'Food and beverages', 9.0, 300),
    Item('Newspaper', '報紙', 'Miscellaneous', 2.0, 100),
    Item('Cigarettes', '煙', 'Miscellaneous', 5.0, 100),
]
for item in initial_items:
    db.session.add(item)
db.session.commit()

# Create a route to add a item to the database
# @app.route('/item', methods=['POST'])
# def add_item():
#     name_en = request.json['name_en']
#     name_cn = request.json['name_cn']
#     price = request.json['price']
#     quantity = request.json['quantity']

#     new_item = Item(name_en, name_cn, price, quantity)

#     db.session.add(new_item)
#     db.session.commit()

#     return item_schema.jsonify(new_item)

# Create a route to get all the items from the database
# @app.route('/item', methods=['GET'])
# def get_items():
#     all_items = Item.query.all()
#     result = items_schema.dump(all_items)
#     return jsonify(result)

# Create a route to get the unique categories
@app.route('/category', methods=['GET'])
def get_categories():
    categories = Item.query.with_entities(Item.category).distinct().all()
    result = [category[0] for category in categories]
    return jsonify(result)

# Create a route to get a item by ids, multiple ids are separated by comma
@app.route('/item', methods=['GET'])
def get_items():
    ids = request.args.get('id')
    categories = request.args.get('category')
    if ids:
        ids = ids.split(',')
        items = Item.query.filter(Item.id.in_(ids)).all()
        result = items_schema.dump(items)
    elif categories:
        categories = categories.split(',')
        items = Item.query.filter(Item.category.in_(categories)).all()
        result = items_schema.dump(items)
    else:
        items = Item.query.all()
        result = items_schema.dump(items)
    return jsonify(result)

# # Create a route to update a item by id
# @app.route('/item/<id>', methods=['PUT'])
# def update_item(id):
#     item = Item.query.get(id)
#     name_en = request.json['name_en']
#     name_cn = request.json['name_cn']
#     price = request.json['price']
#     quantity = request.json['quantity']

#     item.name_en = name_en
#     item.name_cn = name_cn
#     item.price = price
#     item.quantity = quantity

#     db.session.commit()

#     return item_schema.jsonify(item)

# # Create a route to delete a item by id
# @app.route('/item/<id>', methods=['DELETE'])
# def delete_item(id):
#     item = Item.query.get(id)
#     db.session.delete(item)
#     db.session.commit()

#     return item_schema.jsonify(item)

# Create a route to deduct the quantity of a item by id
@app.route('/item/purchase', methods=['POST'])
def purchase_item():
    
    id = request.json['id']
    quantity = request.json['quantity']
    item = Item.query.get(id)

    item.quantity = item.quantity - quantity

    db.session.commit()

    return item_schema.jsonify(item)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

# End of file