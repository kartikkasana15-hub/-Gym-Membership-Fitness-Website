from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
from flask_migrate import Migrate
from forms import RegistrationForm, LoginForm, ClassForm
from db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)
migrate = Migrate(app, db)

from models import User, Membership, Class, Trainer, ClassSchedule, Booking, Payment, ContactMessage
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    classes = Class.query.limit(4).all()
    trainers = Trainer.query.limit(3).all()
    memberships = Membership.query.filter_by(is_active=True).all()
    return render_template('index.html', 
                         classes=classes, 
                         trainers=trainers, 
                         memberships=memberships,
                         now=datetime.now())

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            date_of_birth=form.date_of_birth.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's upcoming bookings
    upcoming_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status='confirmed'
    ).filter(
        Booking.class_date >= datetime.now().date()
    ).order_by(Booking.class_date).limit(5).all()
    
    # Get payment history
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(
        Payment.payment_date.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', 
                         bookings=upcoming_bookings,
                         payments=payments)

@app.route('/classes')
def classes():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    
    query = Class.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    classes = query.all()
    categories = db.session.query(Class.category).distinct().all()
    
    return render_template('classes.html', 
                         classes=classes,
                         categories=[c[0] for c in categories])

@app.route('/class/<int:class_id>')
def class_detail(class_id):
    class_obj = Class.query.get_or_404(class_id)
    schedules = ClassSchedule.query.filter_by(class_id=class_id).all()
    return render_template('class_detail.html', 
                         class_obj=class_obj,
                         schedules=schedules)

@app.route('/book-class/<int:schedule_id>', methods=['POST'])
@login_required
def book_class(schedule_id):
    schedule = ClassSchedule.query.get_or_404(schedule_id)
    class_date = request.form.get('class_date')
    
    # Check if already booked
    existing = Booking.query.filter_by(
        user_id=current_user.id,
        schedule_id=schedule_id,
        class_date=datetime.strptime(class_date, '%Y-%m-%d').date()
    ).first()
    
    if existing:
        flash('You already have a booking for this class on that date.', 'warning')
        return redirect(url_for('classes'))
    
    # Check capacity
    if schedule.current_bookings >= schedule.class_info.max_capacity:
        flash('This class is full.', 'danger')
        return redirect(url_for('classes'))
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        schedule_id=schedule_id,
        class_date=datetime.strptime(class_date, '%Y-%m-%d').date()
    )
    
    schedule.current_bookings += 1
    
    db.session.add(booking)
    db.session.commit()
    
    flash('Class booked successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('dashboard'))
    
    booking.status = 'cancelled'
    schedule = ClassSchedule.query.get(booking.schedule_id)
    schedule.current_bookings -= 1
    
    db.session.commit()
    
    flash('Booking cancelled.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/membership')
def membership():
    memberships = Membership.query.filter_by(is_active=True).all()
    return render_template('membership.html', memberships=memberships)

@app.route('/purchase-membership/<int:membership_id>', methods=['POST'])
@login_required
def purchase_membership(membership_id):
    membership = Membership.query.get_or_404(membership_id)
    
    # Process payment (simplified - in production use Stripe/PayPal)
    from uuid import uuid4
    
    payment = Payment(
        user_id=current_user.id,
        amount=membership.price,
        payment_method='credit_card',
        transaction_id=str(uuid4()),
        membership_id=membership_id
    )
    
    current_user.membership_id = membership_id
    
    db.session.add(payment)
    db.session.commit()
    
    flash(f'Successfully purchased {membership.name} membership!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = ContactMessage(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash('Thank you for your message. We\'ll get back to you soon!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/about')
def about():
    trainers = Trainer.query.limit(4).all()
    return render_template('about.html', trainers=trainers)

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_classes = Class.query.count()
    total_bookings = Booking.query.count()
    recent_messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).limit(5).all()
    
    return render_template('admin/admin_dashboard.html',
                         total_users=total_users,
                         total_classes=total_classes,
                         total_bookings=total_bookings,
                         recent_messages=recent_messages)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/classes')
@login_required
@admin_required
def admin_classes():
    classes = Class.query.all()
    return render_template('admin/classes.html', classes=classes)

@app.route('/admin/class/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_class():
    form = ClassForm()
    form.trainer_id.choices = [(t.id, f"{t.name}") for t in Trainer.query.all()]
    
    if form.validate_on_submit():
        new_class = Class(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            duration=form.duration.data,
            difficulty=form.difficulty.data,
            max_capacity=form.max_capacity.data,
            trainer_id=form.trainer_id.data
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        flash('Class added successfully!', 'success')
        return redirect(url_for('admin_classes'))
    
    return render_template('admin/add_class.html', form=form, trainers=Trainer.query.all())

# API Routes for AJAX requests
@app.route('/api/check-availability/<int:schedule_id>')
def check_availability(schedule_id):
    schedule = ClassSchedule.query.get_or_404(schedule_id)
    return jsonify({
        'available': schedule.current_bookings < schedule.class_info.max_capacity,
        'current_bookings': schedule.current_bookings,
        'max_capacity': schedule.class_info.max_capacity
    })

@app.route('/api/user-stats')
@login_required
def user_stats():
    total_bookings = Booking.query.filter_by(user_id=current_user.id).count()
    upcoming_classes = Booking.query.filter_by(
        user_id=current_user.id,
        status='confirmed'
    ).filter(
        Booking.class_date >= datetime.now().date()
    ).count()
    
    return jsonify({
        'total_bookings': total_bookings,
        'upcoming_classes': upcoming_classes,
        'member_since': current_user.join_date.strftime('%B %Y')
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@gym.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Add sample memberships if none exist
        if Membership.query.count() == 0:
            memberships = [
                Membership(
                    name='Basic',
                    price=29.99,
                    duration_days=30,
                    description='Perfect for beginners',
                    features='Gym access, Locker room, 1 guest pass/month',
                    max_classes_per_week=3,
                    guest_passes=1,
                    access_24_7=False,
                    includes_training=False
                ),
                Membership(
                    name='Premium',
                    price=59.99,
                    duration_days=30,
                    description='Most popular choice',
                    features='24/7 access, All classes, 1 PT session/week',
                    max_classes_per_week=10,
                    guest_passes=2,
                    access_24_7=True,
                    includes_training=True
                ),
                Membership(
                    name='Elite',
                    price=89.99,
                    duration_days=30,
                    description='Ultimate fitness experience',
                    features='Unlimited classes, 2 PT sessions/week, Nutrition guide',
                    max_classes_per_week=20,
                    guest_passes=4,
                    access_24_7=True,
                    includes_training=True
                )
            ]
            db.session.add_all(memberships)
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)