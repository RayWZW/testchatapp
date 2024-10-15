# utils/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=30)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    pfp = FileField('Profile Picture', validators=[Optional()])  # Optional field for the profile picture
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
