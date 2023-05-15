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
from models import db, User, Planet, People, Favourite
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
def get_user():

    # obtiene todos los objetos de usuario de la base de datos
    users = User.query.all()

    # crea una lista de diccionarios con la información de cada usuario
    user_list = [element.serialize() for element in users]

    return jsonify(response_body), 200

@app.route('/users/favourites', methods=['GET'])
def get_user_favourites():
    
    user = User.query.get(current_logged_user_id)
    favourites = user.favourites
    serialized_favourites = [f.serialize() for f in favourites]

    response_body = {
        "msg": f"Aqui tienes los favoritos de {user.email}",
        "favourites": serialized_favorites
    }

    return jsonify(response_body), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    allPlanets = Planet.query.all()
    result = [element.serialize() for element in allPlanets]
    return jsonify(result), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        raise APIException('Planet not found', status_code=404)
    return jsonify(planet.serialize()), 200


@app.route('/people', methods=['GET'])
def get_people():
    allPeople = People.query.all()
    result = [element.serialize() for element in allPeople]
    return jsonify(result), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if not person:
        raise APIException('Person not found', status_code=404)

    return jsonify(person.serialize()), 200

@app.route('/planet', methods=['POST'])
def post_planet():

    # obtener los datos de la petición que están en formato JSON a un tipo de datos entendibles por pyton (a un diccionario). En principio, en esta petición, deberían enviarnos 3 campos: el nombre, la descripción del planeta y la población
    data = request.get_json()

    # creamos un nuevo objeto de tipo Planet
    planet = Planet(name=data['name'], description=data['description'], population=data['population'])

    # añadimos el planeta a la base de datos
    db.session.add(planet)
    db.session.commit()

    response_body = {"msg": "Planet inserted successfully"}
    return jsonify(response_body), 200

@app.route('/favourite/user/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favourite_planet(planet_id):
    # Capturamos la informacion del request body y accedemos a planet_ud id
 
    user = User.query.get(current_logged_user_id)

    new_favourite = Favourite(user_id=current_logged_user_id, planet_id=planet_id)
    db.session.add(new_favourite)
    db.session.commit()

    response_body = {
        "msg": "Favorito agregado correctamente", 
        "favourite": new_favourite.serialize()
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['POST'])
def post_people():

    # obtener los datos de la petición que están en formato JSON a un tipo de datos entendibles por pyton (a un diccionario). En principio, en esta petición, deberían enviarnos 3 campos: el nombre, la descripción del planeta y la población
    data = request.get_json()

    # creamos un nuevo objeto de tipo Planet
    people = People(name=data['name'], age=data['age'], description=data['description'])

    # añadimos el planeta a la base de datos
    db.session.add(people)
    db.session.commit()

    response_body = {"msg": "People inserted successfully"}
    return jsonify(response_body), 200


@app.route('/favourite/user/<int:user_id>/people/<int:people_id>', methods=['POST'])
def add_favourite_people(people_id):
    # Capturamos la informacion del request body y accedemos a planet_ud id
 
    user = User.query.get(current_logged_user_id)

    new_favourite = Favourite(user_id=current_logged_user_id, people_id=people_id)
    db.session.add(new_favourite)
    db.session.commit()

    response_body = {
        "msg": "Favorito agregado correctamente", 
        "favourite": new_favourite.serialize()
    }

    return jsonify(response_body), 200



@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    if planet_id in favorites:
        del favorites[planet_id]
        return jsonify({'message': f'Favorite planet with id {planet_id} deleted successfully'})
    else:
        return jsonify({'error': f'Favorite planet with id {planet_id} not found'}), 404

if __name__ == '__main__':
    app.run()

@app.route('/favorite/user/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    if people_id in favorites:
        del favorites[people_id]
        return jsonify({'message': f'Favorite people with id {people_id} deleted successfully'})
    else:
        return jsonify({'error': f'Favorite people with id {people_id} not found'}), 404

if __name__ == '__main__':
    app.run()



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
