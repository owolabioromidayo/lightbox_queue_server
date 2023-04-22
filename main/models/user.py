from werkzeug.security import generate_password_hash, check_password_hash
from main import app, db
import datetime, jwt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String) #find string length
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    admin = db.Column(db.Boolean, nullable=False, default=False)
    disabled = db.Column(db.Boolean, nullable=False, default=False)
    trust_score = db.Column(db.Integer)

    """
        things to add
            last logged in 
    """

    #learn more about relationships
    # contacts = db.relationship('Contact', backref='user', lazy='dynamic')
    # bank_loans = db.relationship('BankLoan', backref='user', lazy='dynamic')
    # user_loans = db.relationship('UserLoan', backref='user', lazy='dynamic')
    # transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    # subscriptions = db.relationship('Subscription', backref='users', lazy='dynamic') #look more into this


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __init__(self, username, password,  email, admin=False):
        self.username = username
        self.email = email #needs email verification
        self.password_hash = generate_password_hash(password)
        self.admin = admin
        self.disabled = False 
        self.trust_score = 1000 #starts from 1000 and decreases/increases based on actions


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'id': self.id 
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e


    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            return payload['id']
        except jwt.ExpiredSignatureError:
            raise ValueError('Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token. Please log in again.')
        except Exception as e:
            raise ValueError(str(e))