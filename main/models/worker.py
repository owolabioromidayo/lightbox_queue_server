from werkzeug.security import generate_password_hash, check_password_hash
from main import app, db
import datetime, jwt

class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String) #find string length
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    admin = db.Column(db.Boolean, nullable=False, default=False)
    disabled = db.Column(db.Boolean, nullable=False, default=False)

    last_check_in = db.Column(db.DateTime, default=datetime.datetime.utcnow(), index=True)
    last_aborted_job = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    completed_jobs = db.Column(db.Integer, default=0, nullable=False)
    aborted_jobs = db.Column(db.Integer, default=0, nullable=False)
    uncompleted_jobs = db.Column(db.Integer, default=0, nullable=False)

    uptime = db.Column(db.BigInteger, default=0, nullable=False)

    last_broadcast = db.Column(db.String) #find string length

    # models = db.relationship("WorkerModel", back_populates="worker", cascade="all, delete-orphan")


    """things to add 
    jobs/models -> maybe later (store last broadcast for now)

    last logged in 

    index=True for regularly accessed things

    """
    def __repr__(self):
        return '<Worker {}>'.format(self.username)

    def __init__(self, username, password,  email, admin=False):
        self.username = username
        self.email = email #needs email verification
        self.password_hash = generate_password_hash(password)
        self.admin = admin
        self.disabled = False


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30, seconds=0),
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