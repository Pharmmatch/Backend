from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config.Config')  # Load the config from the Config class in config.py

print(app.config['SQLALCHEMY_DATABASE_URI'])  # Print to verify the URI

db = SQLAlchemy(app)

from app import routes