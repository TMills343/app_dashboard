from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
import hmac
import logging
import os

app = Flask(__name__)
# Secret key setup via environment variable
secret_from_env = os.getenv('SECRET_KEY')
if not secret_from_env:
    logging.warning("SECRET_KEY environment variable is not set. Generating a temporary key for this runtime.")
    # Generate a per-runtime secret to avoid using a hardcoded default
    # Note: Sessions become invalid on restart unless SECRET_KEY is provided via ENV
    secret_from_env = os.urandom(32).hex()
app.secret_key = secret_from_env

# Logging setup
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB setup via environment variable (e.g., provided by Portainer)
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    logging.warning("MONGO_URI environment variable is not set. MongoClient may fail to connect.")

client = MongoClient(mongo_uri)  # Connection string expected from ENV
db = client["app_dashboard"]
collection = db["app_details"]


@app.route("/")
def home():
    # Dashboard title configurable via env var; fallback keeps existing default
    title = os.getenv('DASHBOARD_TITLE', 'App Dashboard')
    return render_template("index.html", dashboard_title=title)


@app.route("/get_apps", methods=["GET"])
def get_apps():
    # Fetch apps data from MongoDB
    apps = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
    return jsonify(apps)


def _check_admin_password(provided: str) -> (bool, str):
    """Validate provided admin password against ENV ADMIN_PASSWORD using constant-time compare.

    Returns (ok, error_message). If ADMIN_PASSWORD env is missing, returns (False, reason).
    """
    expected = os.getenv('ADMIN_PASSWORD')
    if expected is None or expected == "":
        logger.warning("ADMIN_PASSWORD environment variable is not set; admin operations are disabled.")
        return False, "Admin operations are disabled: ADMIN_PASSWORD not configured on server"
    if provided is None:
        return False, "Missing admin password"
    try:
        match = hmac.compare_digest(str(provided), str(expected))
    except Exception:
        match = False
    if not match:
        return False, "Unauthorized"
    return True, ""


@app.route("/add_new_app", methods=["POST"])
def add_new_app():
    # Get JSON data from the POST request
    app_data = request.get_json(silent=True) or {}

    # Server-side admin auth
    ok, reason = _check_admin_password(app_data.pop("admin_password", None))
    if not ok:
        status = 503 if reason.startswith("Admin operations are disabled") else 401
        return {"success": False, "error": reason}, status

    # Check if the required fields are present
    if not all(key in app_data and app_data[key] for key in ("name", "url", "icon", "description")):
        return {"success": False, "error": "Missing required fields"}, 400

    # Insert data into MongoDB
    collection.insert_one(app_data)

    # Respond with success message
    return {"success": True, "message": "App added successfully"}, 200


@app.route("/delete_app", methods=["POST"])
def delete_app():
    """Delete an app by a unique identifier (name used here)."""
    try:
        data = request.get_json(force=True)
    except Exception:
        return {"success": False, "error": "Invalid JSON"}, 400

    # Server-side admin auth
    ok, reason = _check_admin_password((data or {}).get("admin_password"))
    if not ok:
        status = 503 if reason.startswith("Admin operations are disabled") else 401
        return {"success": False, "error": reason}, status

    name = (data or {}).get("name")
    if not name:
        return {"success": False, "error": "Missing 'name' field"}, 400

    result = collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return {"success": False, "error": "App not found"}, 404

    return {"success": True, "message": "App deleted successfully"}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2390)
