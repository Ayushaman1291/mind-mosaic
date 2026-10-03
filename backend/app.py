from flask import Flask, jsonify
from flask_cors import CORS

import config
from routes.auth import auth_bp
from routes.registration import registration_bp
from routes.reminders import reminders_bp
from routes.games import games_bp
from routes.photos import photos_bp
from routes.dashboard import dashboard_bp


def create_app():
    # static_folder="static" + static_url_path="/static" means files saved
    # to static/uploads/ by storage/mock_storage.py are servable at
    # http://127.0.0.1:5000/static/uploads/<filename> automatically.
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    CORS(app)  # wide open for hackathon; tighten origins later if there's time

    app.register_blueprint(auth_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(photos_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "mindmosaic-backend",
            "db_backend": "mock" if config.USE_MOCK_DB else "supabase",
        })

    return app


app = create_app()

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
