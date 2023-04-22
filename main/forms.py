from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
#import email_validator

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('User Type', choices=[('user', 'User'), ('worker', 'Worker')], validators=[DataRequired()])

    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('user', 'User'), ('worker', 'Worker')], validators=[DataRequired()])
    submit = SubmitField('Login')