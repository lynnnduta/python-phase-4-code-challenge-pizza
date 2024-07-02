#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET', 'DELETE'])
def restaurants():
    if request.method == 'GET':
        restaurants_list = []
        for restaurant in Restaurant.query.all():
            restaurant_dict = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            restaurants_list.append(restaurant_dict)
        response = make_response(
            jsonify(restaurants_list),
            200
        )
        return response
    elif request.method == 'DELETE':
        Restaurant.query.delete()
        db.session.commit()
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    if request.method == 'GET':
        restaurant = Restaurant.query.get(id)
        if restaurant:
            restaurant_pizzas = [
                {
                    "id": restaurant_pizza.id,
                    "price": restaurant_pizza.price,
                    "pizza": {
                        "id": restaurant_pizza.pizza.id,
                        "name": restaurant_pizza.pizza.name,
                        "ingredients": restaurant_pizza.pizza.ingredients
                    }
                } for restaurant_pizza in restaurant.restaurant_pizzas
            ]
            restaurant_dict = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": restaurant_pizzas
            }
            return make_response(jsonify(restaurant_dict), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    elif request.method == 'DELETE':
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response(jsonify({}), 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas_list = []
    for pizza in Pizza.query.all():
        pizza_dict = {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
        pizzas_list.append(pizza_dict)
    response = make_response(
        jsonify(pizzas_list),
        200
    )
    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    errors = []

    try:
        price = data['price']
        pizza_id = data['pizza_id']
        restaurant_id = data['restaurant_id']

        if not isinstance(price, (int, float)) or not (1 <= price <= 30):
            errors.append("validation errors")

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza:
            errors.append("validation errors")

        if not restaurant:
            errors.append("validation errors")

        if errors:
            return make_response(jsonify({"errors": errors}), 400)

        restaurant_pizza = RestaurantPizza(
            restaurant_id=restaurant_id, pizza_id=pizza_id, price=price)

        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = {
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza": {
                "id": restaurant_pizza.pizza.id,
                "name": restaurant_pizza.pizza.name,
                "ingredients": restaurant_pizza.pizza.ingredients
            },
            "restaurant": {
                "id": restaurant_pizza.restaurant.id,
                "name": restaurant_pizza.restaurant.name,
                "address": restaurant_pizza.restaurant.address
            }
        }

        return make_response(jsonify(response_data), 201)

    except KeyError:
        return make_response(jsonify({'error': ["validation_errors"]}), 400)

    except Exception as e:
        return make_response(jsonify({'error': ["validation_errors"]}), 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
