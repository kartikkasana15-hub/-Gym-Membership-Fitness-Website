from app import app, db, User, Membership, Class, Trainer, ClassSchedule
from datetime import time

with app.app_context():
    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@ironcore.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

    # Create memberships
    if not Membership.query.first():
        memberships = [
            Membership(
                name='Basic',
                price=29.99,
                duration_days=30,
                description='Perfect for casual gym goers',
                max_classes_per_week=3,
                access_24_7=True
            ),
            Membership(
                name='Premium',
                price=49.99,
                duration_days=30,
                description='For serious fitness enthusiasts',
                max_classes_per_week=10,
                access_24_7=True,
                includes_training=True
            ),
            Membership(
                name='VIP',
                price=79.99,
                duration_days=30,
                description='Unlimited access with personal training',
                max_classes_per_week=999,
                access_24_7=True,
                includes_training=True,
                guest_passes=5
            )
        ]
        for membership in memberships:
            db.session.add(membership)

    # Create trainers
    if not Trainer.query.first():
        trainers = [
            Trainer(
                name='John Smith',
                specialty='Strength Training',
                bio='Certified personal trainer with 8 years of experience',
                experience_years=8
            ),
            Trainer(
                name='Sarah Johnson',
                specialty='Yoga & Pilates',
                bio='Yoga instructor and wellness coach',
                experience_years=6
            ),
            Trainer(
                name='Mike Davis',
                specialty='HIIT & Cardio',
                bio='Former athlete turned fitness coach',
                experience_years=10
            )
        ]
        for trainer in trainers:
            db.session.add(trainer)

    # Create classes
    if not Class.query.first():
        classes = [
            Class(
                name='Morning HIIT',
                description='High-intensity interval training to boost your metabolism',
                category='HIIT',
                duration=45,
                difficulty='Intermediate',
                max_capacity=15,
                trainer_id=3
            ),
            Class(
                name='Power Yoga',
                description='Build strength and flexibility with dynamic yoga flows',
                category='Yoga',
                duration=60,
                difficulty='Beginner',
                max_capacity=20,
                trainer_id=2
            ),
            Class(
                name='Strength & Conditioning',
                description='Full-body workout focusing on building muscle and endurance',
                category='Strength',
                duration=50,
                difficulty='Advanced',
                max_capacity=12,
                trainer_id=1
            ),
            Class(
                name='Cardio Blast',
                description='Fun cardio workout to improve heart health',
                category='Cardio',
                duration=40,
                difficulty='Beginner',
                max_capacity=25,
                trainer_id=3
            )
        ]
        for class_obj in classes:
            db.session.add(class_obj)

    # Create class schedules
    if not ClassSchedule.query.first():
        schedules = [
            ClassSchedule(
                class_id=1,
                day_of_week=1,  # Monday
                start_time=time(7, 0),
                end_time=time(7, 45),
                room='Studio A'
            ),
            ClassSchedule(
                class_id=2,
                day_of_week=2,  # Tuesday
                start_time=time(18, 0),
                end_time=time(19, 0),
                room='Studio B'
            ),
            ClassSchedule(
                class_id=3,
                day_of_week=3,  # Wednesday
                start_time=time(19, 0),
                end_time=time(19, 50),
                room='Gym Floor'
            ),
            ClassSchedule(
                class_id=4,
                day_of_week=4,  # Thursday
                start_time=time(17, 30),
                end_time=time(18, 10),
                room='Studio A'
            )
        ]
        for schedule in schedules:
            db.session.add(schedule)

    db.session.commit()
    print("Sample data added successfully!")