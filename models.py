from db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'))
    profile_image = db.Column(db.String(200), default='default.jpg')
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # 30, 90, 365
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON string of features
    max_classes_per_week = db.Column(db.Integer)
    guest_passes = db.Column(db.Integer, default=0)
    access_24_7 = db.Column(db.Boolean, default=False)
    includes_training = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    users = db.relationship('User', backref='membership', lazy=True)

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # HIIT, Yoga, Strength, etc.
    duration = db.Column(db.Integer)  # in minutes
    difficulty = db.Column(db.String(20))  # Beginner, Intermediate, Advanced
    max_capacity = db.Column(db.Integer, default=20)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    image_url = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    
    schedules = db.relationship('ClassSchedule', backref='class_info', lazy=True)

class Trainer(db.Model):
    __tablename__ = 'trainers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(200))
    bio = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    image_url = db.Column(db.String(200))
    social_media = db.Column(db.Text)  # JSON for social links
    is_active = db.Column(db.Boolean, default=True)
    
    classes = db.relationship('Class', backref='trainer', lazy=True)

class ClassSchedule(db.Model):
    __tablename__ = 'class_schedules'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day_of_week = db.Column(db.Integer)  # 0-6 (Monday-Sunday)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))
    current_bookings = db.Column(db.Integer, default=0)
    
    bookings = db.relationship('Booking', backref='schedule', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('class_schedules.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    class_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, attended
    check_in_time = db.Column(db.DateTime)

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='completed')
    transaction_id = db.Column(db.String(100), unique=True)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'))

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    condition = db.Column(db.String(20))  # New, Good, Needs Maintenance
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    location = db.Column(db.String(100))

class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20))
    duration_weeks = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    exercises = db.Column(db.Text)  # JSON of exercises

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    achievement_type = db.Column(db.String(50))
    description = db.Column(db.String(200))
    date_earned = db.Column(db.DateTime, default=datetime.utcnow)
    badge_image = db.Column(db.String(200))