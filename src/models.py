from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()


user_favorites = db.Table( 
    'user_favorites', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True), 
    db.Column('favorite_id', db.Integer, db.ForeignKey('favorite.id'), primary_key=True) )


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)

    favorites = db.relationship('Favorite', secondary=user_favorites, back_populates='users')


    def serialize(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email":self.fullname,
            "favorites": list(map(lambda item: item.serialize(), self.favorites))
        }



class People(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    height=db.Column(db.String(80)) 
    mass=db.Column(db.String(80)) 
    hair_color=db.Column(db.String(80))
    skin_color=db.Column(db.String(80)) 
    eye_color=db.Column(db.String(80)) 
    birth_year=db.Column(db.String(80)) 
    gender=db.Column(db.String(80)) 


    def serialize(self):
        return {
            "id": self.id,
            "name" : self.name,
            "height":self.height,
            "mass":self.mass,
            "hair_color":self.hair_color,
            "skin_color":self.skin_color,
            "eye_color":self.eye_color,
            "birth_year":self.birth_year,
            "gender":self.gender
        }
    

class Planet(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    rotation_period=db.Column(db.String(80))
    orbital_period=db.Column(db.String(80))
    diameter=db.Column(db.String(80))
    climate=db.Column(db.String(80))
    gravity=db.Column(db.String(80))
    terrain=db.Column(db.String(80))
    surface_water=db.Column(db.String(80))
    population=db.Column(db.String(80))


    def serialize(self):
        return {
            "id": self.id ,
            "name": self.name,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "diameter": self.diameter,
            "climate": self.climate,
            "gravity": self.gravity,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "population": self.population
        }


class Nature(Enum):
    PEOPLE = "people"
    PLANET = "planet"


class Favorite(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nature = db.Column(db.Enum(Nature), nullable=False)
    nature_id = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    users = db.relationship('User', secondary=user_favorites, back_populates='favorites')

    def serialize(self):
        return {
            "id": self.id,
            "nature": self.nature.value,
            "nature_id": self.nature_id,
            "user_id": self.nature_id,
          
            
        }

    


