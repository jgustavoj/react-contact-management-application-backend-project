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
from models import db, User, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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


@app.route('/contact', methods=['POST', 'GET'])
def handle_contact():

    """
    Create contact
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        contact = Contact(full_name=body['full_name'], email=body['email'], phone=body['phone'], address=body['address'])
        db.session.add(contact)
        db.session.commit()
        return "ok", 200
    # GET request
    if request.method == 'GET':
        contact = Contact.query.all()
        contact = list(map(lambda x: x.serialize(), contact))
        return jsonify(contact), 200
    return "Invalid Method", 404

@app.route('/contact/<int:id>', methods=['PUT', 'GET'])
def handle_contact_update(id):

    """
    Update Contact

    """

    body = request.get_json() 
    #PUT request
    if request.method == 'PUT':
        contact = Contact.query.get(id)
        contact.full_name = body["full_name"]
        contact.email = body["email"]
        contact.phone = body["phone"]
        contact.address = body["address"]
        contact.id = body["id"]
        db.session.commit()
        return jsonify(contact.serialize()), 200
    #Get request
    if request.method == 'GET':
        contact = Contact.query.get(id)
        contact = list(map(lambda x: x.serialize(), contact))
        return jsonify(contact), 200
    return "Invalid Method", 404


@app.route('/contact/<int:id>', methods=['DELETE'])
def delete_item(id):

    """
    Delete Contact
    

    """
    contact = Contact.query.get(id)
    if contact is None:
        raise APIException('Contact not found', status_code=404)
    db.session.delete(contact)
    db.session.commit()
    contact = Contact.query.all()
    contact = list(map(lambda x: x.serialize(), contact))
    return jsonify(contact), 200





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

