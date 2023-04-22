from flask import Blueprint, render_template, request
from flask_mail import Mail, Message

from main import app, db
from main.models.user import User
from main.models.worker import Worker

from main.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__, url_prefix="/auth")


# app.config['MAIL_SERVER']='<your_email_provider_smtp_server>'
# app.config['MAIL_PORT'] = <your_email_provider_smtp_port>
# app.config['MAIL_USERNAME'] = '<your_email_address>'
# app.config['MAIL_PASSWORD'] = '<your_email_password>'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

# mail = Mail(app)




@bp.route('/api/login', methods=['GET', 'POST'])
def user_login():
    _json = None
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        _json = request.json
        user = User.query.filter_by(username=_json["username"]).first() #check if this fails
        if user:
            if user.check_password(_json["password"]):
                return user.encode_auth_token()
            else:
                return {
                    "success": False,
                    "error": "Incorrect login details"
                }
        else:
            return {
                "success": False,
                "error": "Incorrect login details"
            }
    else:
        return {
            "success": False,
            "error": "Content-Type not supported"
        }


@bp.route('/api/register', methods=['GET', 'POST'])
def user_register():

    _json = None
    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        _json = request.json
        try:
            user = User(username=_json["username"], password=_json["password"], email=_json["email"]) #check if this fails
            db.session.add(user)
            db.session.commit()

            return user.encode_auth_token()
        except:
            #user exists
            return {
                "success": False,
                "error": "User exists or not all details were passed "
            }

    else:
        return {
            "success": False,
            "error": "Content-Type not supported"
        }

@bp.route('/register', methods=['GET', "POST"])
def user_register_view():
    form = RegistrationForm()

    if form.validate_on_submit():
            if form.data["user_type"] == "user":
                try: 
                    user = User(username=form.data["username"], password= form.data["password"], email= form.data["email"]) #check if this fails
                    db.session.add(user)
                    db.session.commit()
                    return f"Here's your Token: {user.encode_auth_token()}"
                except:
                    return "User exists or incorrect details"
            else:
                try:
                    worker = Worker(username=form.data["username"], password= form.data["password"], email= form.data["email"]) #check if this fails
                    db.session.add(worker)
                    db.session.commit()
                    return f"Here's your Token: {worker.encode_auth_token()}"
                except:
                    return "User exists or incorrect details"


    return render_template('auth/register.html', title='Sign In', form=form)


@bp.route('/login', methods=['GET', "POST"])
def login_view():
    form = LoginForm()

    if form.validate_on_submit():
        if form.data["user_type"] == "user":
            user = User.query.filter_by(username=form.data["username"]).first() #check if this fails
            if user:
                if user.check_password(form.data["password"]):
                    return f"Here's your Token: {user.encode_auth_token()}"
                else:
                    return "Invalid details"
            else:
                return "Invalid details"
        else:
            worker= Worker.query.filter_by(username=form.data["username"]).first() #check if this fails
            if worker:
                if worker.check_password(form.data["password"]):
                    return f"Here's your Token: {worker.encode_auth_token()}"
                else:
                    return "Invalid details"
            else:
                return "Invalid details"

    return render_template('auth/login.html', title='Login', form=form)
