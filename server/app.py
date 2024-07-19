#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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

@app.route('/restaurants',methods=['GET'])
def restaurants():
    restaurants=[]
    for restaurant in Restaurant.query.all():
        restaurant_dict={
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
        }
        restaurants.append(restaurant_dict)
    response=make_response(
        restaurants,
                200
        )
    return response
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    else:
        rest_dict =restaurant.to_dict()
        response = make_response(
            jsonify(rest_dict),
            200
        )
    return response

@app.route('/restaurants/<int:id>', methods = ['GET', 'DELETE'])
def delete_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if request.method == "GET":
        restaurant_dict = restaurant.to_dict()
        response = make_response(restaurant_dict, 204)
        return response
    elif request.method =='DELETE':
        db.session.delete(restaurant)
        db.session.commit()

        response_body ={
            "delete_successful":  True,
            "message": "Restaurant deleted"
        }
        response = make_response(response_body, 204)
        return response
         
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas =[]
    for pizza in Pizza.query.all():
        pizza_dict={
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
        pizzas.append(pizza_dict)
        response = make_response(
            jsonify(pizzas),
                200
        )
    return response
    
@app.route('/restaurant_pizzas', methods = ['GET','POST'])
def post_to_restaurant_pizza():
    if request.method == 'GET':
        restaurant_pizzas = []
        if restaurant_pizzas is None:
            return jsonify({"error": "Restaurant_pizza not found"}), 404

        for rest_pizz in RestaurantPizza.query.all():
            rest_pizza_dict = rest_pizz.to_dict()
            restaurant_pizzas.append(rest_pizza_dict)
        response = make_response(
            restaurant_pizzas,200
        ) 
        return response
    elif request.method == "POST":
        try:
            new_restaurant_pizza = RestaurantPizza(
                price = request.get_json()['price'],
                pizza_id = request.get_json()['pizza_id'],
                restaurant_id = request.get_json()['restaurant_id']
            )
        
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            response = make_response(new_restaurant_pizza.to_dict(), 201, {"Content-Type":"application/json"})
            return response
        
        except ValueError:
            message = {"errors":[f"validation errors"]}
            response= make_response(message, 400)
            return response
if __name__ == "__main__":
    app.run(port=5555, debug=True)