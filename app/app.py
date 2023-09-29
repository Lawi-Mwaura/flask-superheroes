#!/usr/bin/env python3
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return 'Welcome to my Flask App'

@app.route('/heroes', methods=['GET'])
def heroes():
    heroes = []
    for hero in Hero.query.all():
        hero_dict = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name
        }
        heroes.append(hero_dict)
    response = make_response(
        jsonify(heroes),
        200
    )
    return response

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404
    hero_dict = {
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name,
        'powers': []
    }
    for power in hero.powers:
        power_dict = {
            'id': power.id,
            'name': power.name,
            'description': power.description
        }
        hero_dict['powers'].append(power_dict)   

    return jsonify(hero_dict)

@app.route('/powers', methods=['GET'])
def powers():
    powers_list = []
    for power in Power.query.all():
        power_dict = {
            'id': power.id,
            'name': power.name,
            'description': power.description
        }
        powers_list.append(power_dict)  

    response = make_response(
        jsonify(powers_list),
        200
    )
    return response

@app.route('/powers/<int:id>', methods=['GET'])
def fetch_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404
    power_dict = {
        'id': power.id,
        'name': power.name,
        'description': power.description
    }

    return jsonify(power_dict)

@app.route('/heroes/<int:id>', methods=['PATCH'])
def update_hero(id):
    data = request.get_json()
    hero = Hero.query.get(id)

    if not hero:
        return jsonify({'error': 'Hero not found'}), 404

    if 'name' in data:
        new_name = data['name']
        if not new_name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        hero.name = new_name

    if 'super_name' in data:
        new_super_name = data['super_name']
        if not new_super_name:
            return jsonify({'error': 'Super name cannot be empty'}), 400
        hero.super_name = new_super_name

    db.session.commit()

    return jsonify({'message': 'Hero updated successfully'}), 200

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)

    if power is None:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    if "description" not in data:
        return jsonify({"errors": ["description field is required"]}), 400

    new_description = data["description"]

    # Update the power's description
    power.description = new_description

    try:
        db.session.commit()
        return jsonify({"id": power.id, "name": power.name, "description": power.description})
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    if "strength" not in data or "power_id" not in data or "hero_id" not in data:
        return jsonify({"errors": ["strength, power_id, and hero_id fields are required"]}), 400

    strength = data["strength"]
    power_id = data["power_id"]
    hero_id = data["hero_id"]

    power = Power.query.get(power_id)
    hero = Hero.query.get(hero_id)

    if power is None or hero is None:
        return jsonify({"errors": ["Power or Hero not found"]}), 404

    hero_power = HeroPower(strength=strength, hero=hero, power=power)
    try:
        db.session.add(hero_power)
        db.session.commit()
        hero_data = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
        }
        response = make_response(
            jsonify(hero_data),
            200
        )
        return response   
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

if __name__ == '__main__':
    app.run(port=5555)
