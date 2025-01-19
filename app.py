from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
import logging
import os

app = Flask(__name__)
app.secret_key = 'hgajdskfh654654'

# Logging setup
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)  # Replace with your MongoDB connection string
db = client["app_dashboard"]
collection = db["app_details"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_apps", methods=["GET"])
def get_apps():
    # Fetch apps data from MongoDB
    apps = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
    return jsonify(apps)


@app.route("/add_new_app", methods=["POST"])
def add_new_app():
    # Get JSON data from the POST request
    app_data = request.get_json()

    # Check if the required fields are present
    if not all(key in app_data for key in ("name", "url", "icon", "description")):
        return {"success": False, "error": "Missing required fields"}, 400

    # Insert data into MongoDB
    collection.insert_one(app_data)

    # Respond with success message
    return {"success": True, "message": "App added successfully"}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2390)
