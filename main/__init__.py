import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_hcaptcha import hCaptcha
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_url_path="/static")

app.config['SECRET_KEY'] = 'mysecretkey' #change to os.urandom(24) from terminal

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['HCAPTCHA_SITE_KEY'] = 'd7c95aef-1b7a-47e4-a671-d5927504fa91'
app.config['HCAPTCHA_SECRET_KEY'] = 'secret_key'
app.config['HCAPTCHA_ENABLED '] = True


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ['EMAIL']
app.config['MAIL_PASSWORD'] = os.environ['PASSKEY']
app.config['MAIL_DEFAULT_SENDER'] = os.environ['EMAIL']

mail = Mail(app)

db = SQLAlchemy(app)
Migrate(app, db)
CORS(app)

hcaptcha = hCaptcha(app)
