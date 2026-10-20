# app/__init__.py - Dijital Coban SmartLead AI
# Modul E: create_app() fabrikasi parcalari birlestirir; is mantigi icermez.
import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import config_by_name
from app.database import init_db


def create_app(config_name=None):
    app = Flask(__name__)

    # 1) Ayarlar: development / production / testing
    config_name = config_name or os.environ.get("FLASK_ENV", "production")  # varsayilan guvenli mod
    app.config.from_object(config_by_name.get(config_name, config_by_name["production"]))

    # 2) CORS: yalnizca /api/* ve yalnizca izin verilen site(ler)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
         allow_headers=["Content-Type", "X-Admin-Token"], methods=["GET", "POST", "OPTIONS"])

    # 3) Veritabani tablosu
    init_db(app)

    # 4) Rotalar
    from app.routes import api_bp, sayfa_bp
    app.register_blueprint(sayfa_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify({"durum": "ok"})

    return app
