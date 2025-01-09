from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import base64
import os
from werkzeug.utils import secure_file
import csv
import sys
sys.path.append(r"./image-processing")

from image_processing import process_image
app = Flask(__

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Configure the upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

CORS(app)
db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define a model for your data
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    value = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {"id": self.id, "

with app.app_context():
    db.create_all()

address_csv_file = 'housedata.csv'
address_price_mapping = {}
#######################################################################
########################################################################
# --- New code to load address-price data from CSV ---
if os.path.exists(address_csv_file):
    with open(address_csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Adjust these column 
            street = row.get("street", "").strip()
            city   = row.get("city", "").strip()
            state  = row.get("state", "").strip()
            zipcode= row.get("zipcode", "").strip()

            # Build a normalized key in a consistent format.
            key = f"{street}, {city}, {state} {zipcode}"
            address_price_mapping[key] = row['price']
else:
    print("CSV file for addresses not found:", address_csv_file)


# Home endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "success", "message": "Welcome to the REST API with a Database"})

# Endpoint to handle GET (all records) and POST (create new record)
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        all_data = Data.query.all()
        return jsonify({"status": "success", "data": [item.to_dict() for item in all_data]})
   
    elif request.method == 'POST':
        req_data = request.get_json()
        # Expecting a JSON payload with '
        if not req_data or '
            return jsonify({"status": "fail", "message": "Please provide both '
       
        # Check if the 
        if Data.query.filter_by(
            return jsonify({"status": "fail", "message": "
       
        new_record = Data(
        db.session.add(new_record)
        db.session.commit()
        return jsonify({"status": "success", "message": "Record created", "data": new_record.to_dict()}), 201

# Endpoint to handle GET, PUT, DELETE for a single record based on 
@app.route('/api/data/<string:key>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_data(key):
    record = Data.query.filter_by(
   
    if request.method == 'GET':
        if record:
            return jsonify({"status": "success", "data": record.to_dict()})
        else:
            return jsonify({"status": "fail", "message": "

    elif request.method == 'PUT':
        if not record:
            return jsonify({"status": "fail", "message": "
        req_data = request.get_json()
        if not req_data or 'value' not in req_data:
            return jsonify({"status": "fail", "message": "Please provide a new 'value' to update"}), 400
        record.value = req_data['value']
        db.session.commit()
        return jsonify({"status": "success", "message": "Record updated", "data": record.to_dict()})
   
    elif request.method == 'DELETE':
        if not record:
            return jsonify({"status": "fail", "message": "
        db.session.delete(record)
        db.session.commit()
        return jsonify({"status": "success", "message": "Record deleted"})






































        

# Endpoint to handle a list of base64 image uploads
@app.route('/api/upload', methods=['POST'])
def process_image_upload():
    req_data = request.get_json()
    if not req_data or '
        return jsonify({"status": "fail", "message": "Missing '
        print("1")

    image_list = req_data['value']
    if not isinstance(image_list, list) or len(image_list) == 0:
        return jsonify({"status": "fail", "message": "'value' must be a non-empty list of base64-encoded images"}), 400
        print("2")

    detected_items_all = []
    # Process all images in the list
    for base64_image in image_list:
        print("3")
        try:
            detected_items = process_image(base64_image, req_data['
            detected_items_all.extend(detected_items)

        except Exception as e:
            return jsonify({"status": "fail", "message": str(e)}), 400

    return jsonify({"status": "success", "detected_items": detected_items_all}), 200

#Endpoint to handle an input address to retrieve price
@app.route('/api/address', methods=['POST'])
def get_address_price():
    req_data = request.get_json()
    if not req_data or 'address' not in req_data:
        return jsonify({"status": "fail", "message": "Missing 'address' parameter"}), 400

    user_address = req_data['address'].strip()
    price = address_price_mapping.get(user_address)
    if price:
        return jsonify({"status": "success", "address": req_data['address'], "price": price}), 200
    else:
        return jsonify({"status": "fail", "message": "Address not found"}), 404


if __
    app.run(host='0.0.0.0', port=8000, debug=True)