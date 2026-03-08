from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, DateField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class ClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('HIIT', 'HIIT'), ('Yoga', 'Yoga'), ('Strength', 'Strength'),
        ('Cardio', 'Cardio'), ('Dance', 'Dance'), ('Other', 'Other')
    ])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired()])
    difficulty = SelectField('Difficulty', choices=[
        ('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')
    ])
    max_capacity = IntegerField('Max Capacity', default=20)
    trainer_id = SelectField('Trainer', coerce=int)

class MembershipForm(FlaskForm):
    name = StringField('Membership Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    duration_days = IntegerField('Duration (days)', validators=[DataRequired()])
    description = TextAreaField('Description')
    max_classes_per_week = IntegerField('Max Classes/Week')
    guest_passes = IntegerField('Guest Passes', default=0)
    access_24_7 = BooleanField('24/7 Access')
    includes_training = BooleanField('Includes Personal Training')