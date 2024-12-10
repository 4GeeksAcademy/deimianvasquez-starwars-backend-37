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
from models import db, User, People, Planet, Favorite
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
        user = Favorite()
        user = user.query.all()

        print(user[0].serialize())

        return jsonify("trabajando por usted"),200
    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500
    

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorites_planet(planet_id=None):
    try:
        body = request.json

        planet = Planet.query.get(planet_id)

        if planet is None:
            return jsonify({"message":"user not found"}), 404
        else:
            fav = Favorite(nature="PLANET", nature_id=planet_id, user_id=body["user_id"])
           
            
            db.session.add(fav)
            db.session.commit()

            return jsonify("user guardado exitosamente"), 201

    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500
    

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorites_prople(people_id=None):
    try:
         
        body = request.json

        people = People.query.get(people_id)

        if people is None:
            return jsonify({"message":"user not found"}), 404
        else:
            fav = Favorite()
            fav.nature = "PEOPLE"
            fav.nature_id = people_id
            fav.user_id = body["user_id"]
            
            db.session.add(fav)
            db.session.commit()

            return jsonify("user guardado exitosamente"), 201

    except Exception as err:
        return jsonify(f"Error: {err.args}"), 500
    


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
