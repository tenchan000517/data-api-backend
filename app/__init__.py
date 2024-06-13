# __init__.py

from flask import Flask
from flask_cors import CORS
# from .scheduler import start_scheduler

def create_app():
    app = Flask(__name__)
    CORS(app)  # CORSを有効にする

    from app.routes import main
    app.register_blueprint(main)
    
    # start_scheduler()  # スケジューラーを開始

    return app
