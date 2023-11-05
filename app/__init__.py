from flask import Flask, Response, send_file, request, jsonify, url_for, session,make_response
import os
from werkzeug.utils import redirect
from config import Config
from flask_mail import Mail
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir= os.path.abspath(os.path.dirname(__file__))
db=SQLAlchemy() 
mail = Mail()

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.__init__(app)
    mail.__init__(app)
    Migrate(app,db)

    with app.app_context():
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://127.0.0.1:5000")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
    
    CORS(app, resources=r'/api/*')

    from .api import api as api_blueprint
    from app import models

    app.register_blueprint(api_blueprint, url_prefix='/api')
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    return app