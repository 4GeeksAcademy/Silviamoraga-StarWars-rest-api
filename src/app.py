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
from models import db, User, Planets, Characters, FavoritePlanets, FavoriteCharacters
#from models import Person

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
def get_users():
    #query similar a un SELECT * FROM User;
    all_users = User.query.all()
    #all_users es un array de objetos que tiene que ser serializado, porque no podemos devolver objetos
    all_users_serialize = []
    #serializar es convertir objetos a diccionarios
    for user in all_users:
        all_users_serialize.append(user.serialize())
        #cogerá cada usuario registrado y lo incluirá en el array vacío, que es un array de diccionarios
    if not all_users:
        return jsonify({'msg': 'No se encuentran usuarios'}), 404
    return jsonify({
        'msg': 'Todos los usuarios', 
        'data': all_users_serialize}), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    single_user = User.query.get(user_id) 
    #traemos la info completa SIEMPRE desde la PK
    if not single_user:
        return jsonify({'msg': f'El usuario con id {user_id} no existe'}), 400
    return jsonify({'msg': 'Este es el usuario que buscas', 
                    'data': single_user.serialize()}), 200

@app.route('/user', methods=['POST'])
def add_user():
    body = request.get_json(silent=True)
    if 'name' not in body or 'user_name' not in body or 'email' not in body or 'password' not in body or body is None:
        return jsonify({'msg': 'Nombre, username, email y password son requeridos'}), 400
    new_user = User()
    new_user.name = body['name']
    new_user.user_name = body['user_name']
    new_user.email = body['email']
    new_user.password= body['password']
    new_user.is_active = True
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'Nuevo usuario creado', 'data': new_user.serialize()}), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': f'El usuario con id {user_id} no ha sido encontrado'}),404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'msg': f'El usuario con id {user_id} ha sido eliminado'}), 200

@app.route('/user/<int:user_id>', methods=['PUT'])
def put_user(user_id):
    body = request.get_json(silent=True)
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': f'El usuario con id {user_id} no ha sido encontrado'}), 404
    if 'user_name' in body:
        user.user_name = body['user_name']
    if 'name' in body:
        user.name = body['name']
    if 'email' in body:
        user.email = body['email']
    if 'password' in body:
        user.password = body['password']
    if 'is_active' in body:
        user.is_active = body['is_active']
    db.session.commit()
    return jsonify({'msg': f'El usuario con id {user_id} ha sido modificado'}), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planets.query.all()
    all_planets_serialize = []
    for planet in all_planets:
        all_planets_serialize.append(planet.serialize())
    if not all_planets:
        return jsonify({'msg': 'No se encuentran planetas'}), 404
    return jsonify({'msg': 'Todos los planetas', 
                    'data': all_planets_serialize}), 200

@app.route('/planets/<int:id>', methods=['GET'])
def get_planet(id):
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({'msg': f'El planeta con id {id} no ha sido encontrado'}), 404
    population_serialize = []
    for person in planet.population:
        population_serialize.append(person.serialize())
    return jsonify({'msg': 'Este es el planeta que estás buscando', 
                    'data': planet.serialize(), 
                    'population': population_serialize}), 200

@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json(silent=True)
    if 'name' not in body or 'diameter' not in body:
        return jsonify({'msg': 'Nombre y diámetro son requeridos'}), 400
    new_planet = Planets()
    #se instancia Planets para guardar un nuevo planeta
    new_planet.name = body['name']
    new_planet.diameter = body['diameter']
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({'msg': 'Nuevo planeta creado', 'data': new_planet.serialize()}), 200
    #se serializa para mandar el diccionario
    
@app.route('/planets/<int:id>', methods=['PUT'])
def put_planet(id):
    body = request.get_json(silent=True)
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({'msg': f'El planeta con id {id} no ha sido encontrado'}), 404
    if 'name' in body:
        planet.name = body['name']
    if 'diameter' in body:
        planet.diameter = body['diameter']
    db.session.commit()
    return jsonify({'msg': f'El planeta con id {id} ha sido modificado'}), 200

@app.route('/planets/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({'msg': f'El planeta con id {id} no ha sido encontrado'}),404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': f'El planeta con id {id} ha sido eliminado'}), 200

@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = Characters.query.all()
    all_characters_serialize = []
    for character in all_characters:
        all_characters_serialize.append(character.serialize())
    if not all_characters:
        return jsonify({'msg': 'No se encuentran personajes'}), 404
    return jsonify({'msg': 'Todos los personajes', 
                    'data': all_characters_serialize}), 200

@app.route('/characters/<int:id>', methods=['GET'])
def get_character(id):
    character = Characters.query.get(id)
    if not character:
        return jsonify({'msg': f'El personaje con id {id} no ha sido encontrado'}), 404
    return jsonify({'msg': 'Este es el personaje que estás buscando', 
                    'data': character.serialize(),}), 200

@app.route('/characters', methods=['POST'])
def add_character():
    body = request.get_json(silent=True)
    if 'name' not in body:
        return jsonify({'msg': 'Nombre es requerido'}), 400
    new_character = Characters()
    new_character.name = body['name']
    db.session.add(new_character)
    db.session.commit()
    return jsonify({'msg': 'Nuevo personaje creado', 
                    'data': new_character.serialize()}), 200

@app.route('/characters/<int:id>', methods=['PUT'])
def put_character(id):
    body = request.get_json(silent=True)
    character = Characters.query.get(id)
    if not character:
        return jsonify({'msg': f'El personaje con id {id} no ha sido encontrado'}), 404
    if 'name' in body:
        character.name = body['name']
    db.session.commit()
    return jsonify({'msg': f'El personaje con id {id} ha sido modificado'}), 200

@app.route('/characters/<int:id>', methods=['DELETE'])
def delete_character(id):
    character = Characters.query.get(id)
    if not character:
        return jsonify({'msg': f'El personaje con id {id} no ha sido encontrado'}),404
    db.session.delete(character)
    db.session.commit()
    return jsonify({'msg': f'El personaje con id {id} ha sido eliminado'}), 200

@app.route('/user/<int:id_user>/favorites', methods=['GET'])
def get_favorites(id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({'msg': f'Usuario con id {id_user} no encontrado'}), 404
    #                                                  column_name = parametro recibido
    # con el .all() hacemos que no nos devuleva un query, si no un array
    favorite_planets = FavoritePlanets.query.filter_by(user_id = id_user).all()
    favorite_characters = FavoriteCharacters.query.filter_by(user_id = id_user).all()
    
    if favorite_planets is None and favorite_characters is None:
        return jsonify({'msg': f'El usuario con id {id_user} no tiene favoritos'}), 404
    
    favorite_planets_serialize = []
    for favorite in favorite_planets:
        favorite_planets_serialize.append(favorite.planet_relationship.serialize())
        #con planet_relationship voy al objeto con todas sus propiedades ya serializadas en Models.py
    #cada favorito se incluye en el array ya serializado y en el data se muestra todo el array

    favorite_characters_serialize = []
    for favorite in favorite_characters:
        favorite_characters_serialize.append(favorite.character_relationship.serialize())

    return jsonify({'msg': f'Estos son los favoritos del usuario con id {id_user}', 
                    'data': {'favorite_planets': favorite_planets_serialize,
                            'favorite_characters': favorite_characters_serialize,
                            'user_data': user.serialize()}}), 200

@app.route('/favorites/planets/<int:planet_id>/<int:id_user>', methods=['POST'])
def add_favorite_planet(planet_id, id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({'msg': f'Usuario con id {id_user} no encontrado'}), 404
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'msg': f'Planeta con id {planet_id} no encontrado'}), 404
    existing_favorite = FavoritePlanets.query.filter_by(user_id=id_user, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({'msg': 'El planeta ya está en los favoritos del usuario'}), 400
    new_favorite = FavoritePlanets()
    new_favorite.user_id = id_user
    new_favorite.planet_id = planet_id
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': 'Nuevo planeta añadido', 
                    'data': new_favorite.serialize()}), 200

@app.route('/favorites/characters/<int:character_id>/<int:id_user>', methods=['POST'])
def add_favorite_character(character_id, id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({'msg': f'Usuario con id {id_user} no encontrado'}), 404
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({'msg': f'Personaje con id {character_id} no encontrado'}), 404
    existing_favorite = FavoriteCharacters.query.filter_by(user_id=id_user, character_id=character_id).first()
    if existing_favorite:
        return jsonify({'msg': 'El personaje ya está en los favoritos del usuario'}), 400
    new_favorite = FavoriteCharacters()
    new_favorite.user_id = id_user
    new_favorite.character_id = character_id
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': 'Nuevo personaje añadido', 
                    'data': new_favorite.serialize()}), 200

@app.route('/favorites/planets/<int:planet_id>/<int:id_user>', methods=['DELETE'])
def delete_favorite_planet(planet_id, id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({'msg': f'El usuario con id {id_user} no existe'}), 404
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({'msg': f'El planeta con id {planet_id} no existe'}), 404
    favorite_planet = FavoritePlanets.query.filter_by(user_id = id_user, planet_id = planet_id).first()
    #first para un único registro de planetas
    if favorite_planet is None:
        return jsonify({'msg': f'El planeta con id {planet_id} no está en los favoritos del usuario {id_user}'}),404
    db.session.delete(favorite_planet)
    db.session.commit()
    return jsonify({'msg': f'El planeta con id {planet_id} ha sido eliminado de los favoritos del usuario {id_user}'}), 200

@app.route('/favorites/characters/<int:character_id>/<int:id_user>', methods=['DELETE'])
def delete_favorite_character(character_id, id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({'msg': f'Usuario con id {id_user} no encontrado'}), 404
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({'msg': f'El personaje con id {character_id} no existe'}), 404
    favorite_character = FavoriteCharacters.query.filter_by(user_id = id_user, character_id = character_id).first()
    if favorite_character is None:
        return jsonify({'msg': f'El personaje con id {character_id} no está en los favoritos del usuario {id_user}'}),404
    db.session.delete(favorite_character)
    db.session.commit()
    return jsonify({'msg': f'El personaje con id {character_id} ha sido eliminado de los favoritos del usuario {id_user}'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

