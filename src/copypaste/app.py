from flask import Flask, jsonify

from copypaste.config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    return app
