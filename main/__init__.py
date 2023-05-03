import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_hcaptcha import hCaptcha

app = Flask(__name__, static_url_path="/static")

app.config['SECRET_KEY'] = 'mysecretkey' #change to os.urandom(24) from terminal

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['HCAPTCHA_SITE_KEY'] = 'd7c95aef-1b7a-47e4-a671-d5927504fa91'
app.config['HCAPTCHA_SECRET_KEY'] = 'secret_key'
app.config['HCAPTCHA_ENABLED '] = True


db = SQLAlchemy(app)
Migrate(app, db)
CORS(app)

hcaptcha = hCaptcha(app)
