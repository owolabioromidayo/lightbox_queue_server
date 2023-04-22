"""
what do we have? 

User
WOrker / GPUClient
Generic Sap Sucking User

how are we modelling rewards, bad actions (must be per transsaction)
keeping all action logs of user 
    ->Transaction Model
        -> from, to, type, compute required, completed?, flagged as nefarious?

having trust and leech models 
(all models will be incremental and transaction based )

keeping track of models stored by user  

blacklisting normal users and GPU nodes

getting user and worker stats
"""


from main import db
import datetime


class BankLoan(db.Model):
    __tablename__ = 'bank_loans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

    def __init__(self, user, amount, interest_rate , start_date=datetime.datetime.now(), end_date=None):
        self.user_id = user_id
        self.amount = amount
        self.interest_rate = interest_rate
        self.start_date = start_date
        self.end_date = end_date
        self.active = True

class UserLoan(db.Model):
    __tablename__ = 'user_loans'

    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    loaner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    term = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

    def __init__(self, borrower_id, loaner_id, amount, interest_rate, start_date=datetime.datetime.now(), end_date=None):
        self.borrower_id = borrower_id
        self.loaner_id = loaner_id
        self.amount = amount
        self.interest_rate = interest_rate
        self.term = term
        self.start_date = start_date
        self.end_date = end_date
        self.active = True

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    users = db.relationship('User', backref='subscriptions', lazy='dynamic') #not verified
    name = db.Column(db.String(64))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    interval = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    action = db.Column(db.String(64))
    status = db.Column(db.String(64))

    def __init__(self, creator_id, name, start_date=datetime.datetime.now(), end_date=None, amount=0.0, interval=30, status='active', action='savings'):
        self.creator_id = creator_id 
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval 
        self.amount = amount
        self.status = status
        self.action = action

        #add the user as the first person in this many-many relationship


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    sender_id= db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Float)
    description = db.Column(db.String(128))
    category = db.Column(db.String(64))

    def __init__(self, sender_id, receiver_id, amount, description="None", category="Unspecified", date=datetime.datetime.now()):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.amount = amount
        self.description = description
        self.category = category
        self.date = date


class Contact(db.Model): #contact mapping table
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    luser_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ruser_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(64))

    def __init__(self, luser_id, ruser_id, name, status="pending"):
        self.luser_id = luser_id
        self.ruser_id = ruser_id
        self.status = status