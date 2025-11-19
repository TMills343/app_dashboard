App Dashboard
=================

A lightweight Flask + MongoDB web app to keep all your self‑hosted (or external) applications accessible in one place. It renders a simple, tile‑based dashboard backed by MongoDB. You can add or remove app tiles from the UI with a simple admin password.

Why this is valuable
- Centralize access: Keep all of your applications accessible in one place.
- Streamline efficiency: Reduce time spent hunting for URLs, bookmarks, and service ports.
- Team friendly: Share a single dashboard so everyone knows where to go.
- Minimal footprint: Small codebase, easy to deploy with Docker/Portainer.


Overview
- Backend: Flask
- Database: MongoDB (single DB and collection)
- Frontend: Vanilla HTML/CSS/JS
- Auth model: Server‑side admin password validation for add/delete operations


Environment variables
Set these on your host, in Portainer, or via docker‑compose.

- MONGO_URI (required)
  - MongoDB connection string.
  - Example: mongodb://user:pass@mongo:27017/app_dashboard
- ADMIN_PASSWORD (required)
  - Password required for admin operations (adding or deleting apps). Not exposed to clients.
- SECRET_KEY (strongly recommended)
  - Flask secret key used for session signing. If omitted, the app generates a temporary key per runtime and logs a warning. Sessions will reset on restart.


MongoDB setup
- Database name used by the app: app_dashboard
- Collection name used by the app: app_details

Schema
Documents in app_details are simple flat objects with these required fields:
- name: string (used as a unique identifier for deletion)
- url: string (the link opened when a tile is clicked)
- icon: string (URL/path to an icon image shown in the tile)
- description: string (short description shown under the title)

Example document
{
  "name": "Sonarr",
  "url": "http://sonarr.local:8989",
  "icon": "/static/images/sonarr.png",
  "description": "TV series management"
}

Initial seeding (optional)
- You can insert documents manually using your MongoDB client, mongosh, or GUI tools (Compass).
- The app does not require indexes beyond MongoDB defaults, but if you want to avoid duplicates by name, consider adding a unique index on name:
  - In mongosh: db.app_details.createIndex({ name: 1 }, { unique: true })


Endpoints (for reference)
- GET / — Renders index.html
- GET /get_apps — Returns all app documents (fields: name, url, icon, description; _id excluded)
- POST /add_new_app — Body JSON: { name, url, icon, description, admin_password }
- POST /delete_app — Body JSON: { name, admin_password }


How to run locally (without Docker)
Prereqs: Python 3.10+ and a reachable MongoDB.
1) Install dependencies:
   - pip install -r requirements.txt
2) Set environment variables in your shell:
   - On PowerShell (Windows):
     $env:MONGO_URI = "mongodb://user:pass@localhost:27017/app_dashboard"
     $env:ADMIN_PASSWORD = "changeme"
     $env:SECRET_KEY = "a-long-random-string"
   - On macOS/Linux (bash):
     export MONGO_URI="mongodb://user:pass@localhost:27017/app_dashboard"
     export ADMIN_PASSWORD="changeme"
     export SECRET_KEY="a-long-random-string"
3) Start the app:
   - python app.py
4) Open your browser to:
   - http://localhost:2390


Run with Docker
The repository includes Dockerfile and docker-compose.yml examples.

Docker build and run (single container):
1) Build image:
   - docker build -t app_dashboard:latest .
2) Run container (example):
   - docker run -d \
       -p 2390:2390 \
       -e MONGO_URI="mongodb://user:pass@mongo:27017/app_dashboard" \
       -e ADMIN_PASSWORD="changeme" \
       -e SECRET_KEY="a-long-random-string" \
       --name app_dashboard app_dashboard:latest

docker-compose
An example docker-compose.yml is included. Typical usage:
1) Edit docker-compose.yml and set environment variables as needed.
2) Start:
   - docker compose up -d
3) Stop:
   - docker compose down

Portainer deployment
- Create a new stack or container in Portainer.
- Set environment variables:
  - MONGO_URI=mongodb://user:pass@mongo:27017/app_dashboard
  - ADMIN_PASSWORD=your-admin-password
  - SECRET_KEY=your-very-long-random-secret
- Publish port 2390 to your host.
- Ensure the MongoDB service is reachable from the app container (same network or accessible address).


How to use the app
1) Viewing apps
   - Navigate to the dashboard URL to see all existing tiles.
2) Adding a new app
   - Click the “Add New Application” tile/button.
   - Fill in: Name, URL, Icon (URL/path), Description, and enter the admin password.
   - Submit. The server validates the password; on success, a new tile appears immediately.
3) Deleting an app
   - Click the minus (−) button on the tile you want to remove.
   - Enter the admin password when prompted. The server validates before deletion.
   - On success, the tile disappears.


Dependencies
- Flask
- PyMongo
See requirements.txt for pinned versions.


Security notes (important)
- Server‑side authorization: Admin operations (/add_new_app and /delete_app) require the correct admin_password in the request body. The server verifies this against ADMIN_PASSWORD using a constant‑time comparison. ADMIN_PASSWORD is never exposed to the client via any endpoint.
- Reverse proxy auth: For stronger security, consider protecting the app behind your reverse proxy with Basic Auth or SSO, and enable HTTPS.
- SECRET_KEY: Always set a long, random SECRET_KEY for consistent sessions across restarts.


Troubleshooting
- The page loads but no tiles appear
  - Check that MONGO_URI is set and reachable from the container/host.
  - Verify the collection app_details has documents.
- Cannot add or delete apps
  - Ensure ADMIN_PASSWORD is set on the server/container and matches what you provide in the UI.
  - 401 Unauthorized usually means the admin password is wrong; 503 indicates ADMIN_PASSWORD is not configured server‑side.
  - Open browser devtools network tab to see any 4xx/5xx errors.
- Mongo connection errors at startup
  - Confirm MONGO_URI is correct and MongoDB accepts connections from your app environment.
- Icons not showing
  - Ensure the icon field contains a valid URL or a path to a file under static/ (e.g., /static/images/your-icon.png).


FAQ
Q: Can I change the database/collection names?
A: Yes, but you must modify app.py where db and collection are initialized.

Q: Can I host icons locally?
A: Yes. Place them in static/images and reference as /static/images/your-icon.png.

Q: Why not store the password server‑side only?
A: You should for production. This project keeps it simple for small/home deployments but includes notes on how to harden.


License
This project is provided as‑is; add a license if you plan to distribute.
