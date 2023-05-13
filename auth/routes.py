from flask import Blueprint, render_template, request
from flask_mail import Mail, Message

from main import app, db, mail
from main.models.user import User
from main.models.worker import Worker

from main.forms import LoginForm, RegistrationForm


bp = Blueprint('auth', __name__, url_prefix="/auth")


def send_email(to, subject, body):
    message = Message(subject, recipients=[to])
    message.body = body
    mail.send(message)


@bp.route('/register', methods=['GET', "POST"])
def user_register_view():
    form = RegistrationForm()

    if form.validate_on_submit():
            # print(form.data)
            if form.data["user_type"] == "user":
                try: 
                    user = User(username=form.data["username"], password= form.data["password"], email= form.data["email"]) #check if this fails
                    db.session.add(user)
                    db.session.commit()
                    send_email(form.data["email"],"Welcome to LightBox!" , f"Here's your Token: {user.encode_auth_token()}")
                    return f"Your Token has been sent to your email."
                except:
                    return "User exists or incorrect details"
            else:
                try:
                    worker = Worker(username=form.data["username"], password= form.data["password"], email= form.data["email"]) #check if this fails
                    db.session.add(worker)
                    db.session.commit()
                    send_email(form.data["email"],"Welcome to LightBox!" , f"Here's your Token: {worker.encode_auth_token()}")
                    return f"Your Token has been sent to your email."
                except:
                    return "Worker exists or incorrect details"

            return "Captcha !" 
           


    return render_template('auth/register.html', title='Sign In', form=form)


@bp.route('/login', methods=['GET', "POST"])
def login_view():
    form = LoginForm()

    if form.validate_on_submit():
        if form.data["user_type"] == "user":
            user = User.query.filter_by(username=form.data["username"]).first() #check if this fails
            if user:
                if user.check_password(form.data["password"]):
                    send_email(user.email,"Updated Token!" , f"Here's your Token: {user.encode_auth_token()}")
                    return f"Your Token has been sent to your email."
                else:
                    return "Invalid details"
            else:
                return "Invalid details"
        else:
            worker= Worker.query.filter_by(username=form.data["username"]).first() #check if this fails
            if worker:
                if worker.check_password(form.data["password"]):
                    send_email(worker.email,"Updated Token!" , f"Here's your Token: {worker.encode_auth_token()}")
                    return f"Your Token has been sent to your email."
                else:
                    return "Invalid details"
            else:
                return "Invalid details"

    return render_template('auth/login.html', title='Login', form=form)
