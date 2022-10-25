import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask import Flask, request

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError,requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/')
def index():
 
  return '<h1>Hello, Welome to CoffeeShop API </h1>'
#this endpoint give you all drinks
@app.route('/drinks')
def retrieve_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks = [drink.short() for drink in drinks]
    except Exception:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
#this endpoint give you all drinks with persmzssion get 
def show_drinks(payload):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        
    except Exception:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
#this endpoint help you post new drink
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def create_new_drinks(payload):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = json.dumps(body.get("recipe", None))
    if ((new_title is None) or (new_recipe is None)):
        abort(422)
    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
    except Exception:
        drink.rollback()
        print(sys.exc_info())
        abort(422)
    return jsonify({
        "success": True,
        "drink": [drink.long()]
    }), 200

 

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
#this endpoint  =help you modify drinks
@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    body = request.get_json()
    try:
        drink.title = body.get("title", None)
        drink.recipe = json.dumps(body.get("recipe", None))
        drink.update()
    except Exception:
        drink.rollback()
        print(sys.exc_info())
        abort(422)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        
    except Exception:
        abort(422)
    
    return jsonify({
        "success": True,
        "delete": id
    }), 200
 
  

# Error Handling
'''
Example error handling for unprocessable entity
'''

#handle the 422 error
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

#handle the 404 error
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

#handle the 400 error
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, 
        "message": "bad request"
    }), 400

#handle authentication error
@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

#handle the 401  error
@app.errorhandler(401)
def unauthorized(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401

#handle the 500  error
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False, 
        "error": 500, 
        "message": "internal server error"
    }), 500
