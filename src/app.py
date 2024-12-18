"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite, user_favorites
#from models import Person
import requests


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route("/people", methods=["GET"])
def get_all_people():
    try:
        people = People.query.all()
        return jsonify([person.serialize() for person in people]), 200
    except Exception as err:
        return jsonify(f"Error: {err.args}")


@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_people(people_id=None):
    try:
        people = People.query.get(people_id)
        if people is None:
            return jsonify(f"User {people_id} not found"), 404
        else:
            return jsonify(people.serialize())
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500


@app.route("/planets", methods=["GET"])
def get_all_planets():
    try:
        planet = Planet.query.all()
        return jsonify([planet.serialize() for planet in planet]), 200
    except Exception as err:
        return jsonify(f"Error: {err.args}")


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id=None):
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify(f"User {planet_id} not found"), 404
        else:
            return jsonify(planet.serialize())
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500



@app.route("/population-people", methods=["GET"])
def population_people():
    try:
        response = requests.get("https://swapi.dev/api/people")
        response = response.json()["results"]
        for person in response:
            people = People(
                name=person["name"],
                height=person["height"],
                mass=person["mass"],
                hair_color=person["hair_color"],
                skin_color=person["skin_color"] ,
                eye_color=person["eye_color"],
                birth_year=person["birth_year"],
                gender=person["gender"],
                
            )
            db.session.add(people)
        db.session.commit()

        return jsonify("Los personajes se crearon exitosamente"), 200
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500 
    

@app.route("/population-planet", methods=["GET"])
def population_planet():
    try:
        response = requests.get("https://swapi.dev/api/planets")
        response = response.json()["results"]
        for planet in response:
            planet = Planet(
                name=planet["name"],
                rotation_period=planet["rotation_period"],
                orbital_period=planet["orbital_period"],
                diameter=planet["diameter"],
                climate=planet["climate"] ,
                gravity=planet["gravity"],
                terrain=planet["terrain"],
                surface_water=planet["surface_water"],
                population=planet["population"],
                
            )
            db.session.add(planet)
        db.session.commit()

        return jsonify("Los planets se crearon exitosamente"), 200
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500 


@app.route("/users", methods=["GET"])
def get_all_users():
    try:
        users = User.query.all()
        return jsonify([user.serialize() for user in users]), 200
    except Exception as err:
        return jsonify(f"Error: {err}")


@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    try:
        body = request.json

        user = User()
        user = user.query.get(body["user_id"])

        return jsonify(user.serialize()),200
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500
    

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorites_planet(planet_id=None):
    try:
        body = request.json 
        user_id = body.get("user_id") 
        
        if not user_id: 
            return jsonify({"message": "user_id is required"}), 400 
        
        user = User.query.get(user_id) 
        planet = Planet.query.get(planet_id) 
        
        if not user or not planet: 
            return jsonify({"message": "User or Planet not found"}), 404 
        
        favorite = Favorite(nature="PLANET", nature_id=planet_id, user_id=user_id) 
        
        db.session.add(favorite) 
        db.session.commit() 
        
        # Añadir la relación en la tabla de asociación 
        user.favorites.append(favorite) 
        db.session.commit() 

        return jsonify({"message": "Planet save success"}), 201
    
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500
    

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorites_prople(people_id=None):
    try:
         
        body = request.json 
        user_id = body.get("user_id") 
        
        if not user_id: 
            return jsonify({"message": "user_id is required"}), 400 
        
        user = User.query.get(user_id) 
        people = People.query.get(people_id) 
        
        if not user or not people: 
            return jsonify({"message": "User or People not found"}), 404 
        
        favorite = Favorite(nature="PEOPLE", nature_id=people_id, user_id=user_id) 
        
        db.session.add(favorite) 
        db.session.commit() 
        
        # Añadir la relación en la tabla de asociación 
        user.favorites.append(favorite) 
        db.session.commit() 
        return jsonify({"message": "People save successfully"}), 201


    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500
    

@app.route("/favorite/<string:planet_nature>/<int:planet_id>", methods=["DELETE"])
def delete_planet_on_fav(planet_id=None, planet_nature=None):
    try:
        
        favorite = Favorite.query.filter_by(nature=planet_nature.upper(), nature_id=planet_id).first()

        if favorite is None:
            return jsonify({"message":f"Favorite {planet_nature} with id {planet_id} not found"}), 404 
        else:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify("trabajando por usted"), 204

    except Exception as err:
        return jsonify({"message":f"Error: {err.args}"})


@app.route("/favorite/<string:people_nature>/<int:people_id>", methods=["DELETE"])
def delete_people_on_fav(people_id=None, people_nature=None):
    try:
        favorite = Favorite.query.filter_by(nature=people_nature.upper(), nature_id=people_id).first()
        # print(list(map(lambda item: item.serialize(), favorite))[0])
        if favorite is None:
            return jsonify({"message":f"Favorite {people_nature} with id {people_id} not found"}), 404 
        else:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify("trabajando por usted"), 204

    except Exception as err:
        return jsonify({"message":f"Error: {err.args}"})


@app.route("/prueba")
def prueba():
    try:
        # asoci = user_favorites.query.all()
        print(user_favorites)
        return jsonify("probando algo"), 201
    except Exception as err:
        return jsonify(err.args), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
