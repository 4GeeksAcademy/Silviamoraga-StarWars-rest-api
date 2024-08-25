from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FavoritePlanets(db.Model):
    __tablename__='favorite_planets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='planets_favorites')
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planet_relationship = db.relationship('Planets', back_populates='favorite_by')

    def __repr__(self):
        return f'Al usuario {self.user_id} le gusta el planeta {self.planet_id}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'planet_id': self.planet_id
        }
    
class FavoriteCharacters(db.Model):
    __tablename__='favorite_characters'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='characters_favorites')
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character_relationship = db.relationship('Characters', back_populates='favorite_by')

    def __repr__(self):
        return f'Al usuario {self.user_id} le gusta el personaje {self.character_id}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'character_id': self.character_id
        }

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    planets_favorites = db.relationship('FavoritePlanets', back_populates='user_relationship')
    characters_favorites = db.relationship('FavoriteCharacters', back_populates='user_relationship')

    def __repr__(self):
        return f'User con nombre {self.name}, y email {self.email}'
    #texto que nos enseñamos para decirnos a qué usuario nos referimos

    def serialize(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active
            # do not serialize the password, its a security breach
        }
    
class Planets(db.Model):
    __tablename__='planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    population = db.relationship('Characters', back_populates='planet_relationship')
    favorite_by = db.relationship('FavoritePlanets', back_populates='planet_relationship')

    def __repr__(self):
        return f'Planet: {self.name}'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'diameter': self.diameter
        }
    
class Characters(db.Model):
    __tablename__='characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    #asigna un planeta al personaje y los relaciona. Cuando quiera la info del personaje traerá el planeta y toda su info(esto lo hace el serialize)
    planet_relationship = db.relationship('Planets', back_populates='population')
    favorite_by = db.relationship('FavoriteCharacters', back_populates='character_relationship')

    def __repr__(self):
        return f'Character: {self.name}'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }