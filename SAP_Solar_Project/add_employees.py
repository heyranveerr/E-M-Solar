from app import create_app
from extensions import db
from models.user import User

app = create_app()

with app.app_context():
    # Check if users already exist
    existing_user1 = User.query.filter_by(username='employee1').first()
    existing_user2 = User.query.filter_by(username='employee2').first()
    
    added_users = []
    
    # Add employee1 if not exists
    if not existing_user1:
        user1 = User(username='employee1', password='employee1')
        db.session.add(user1)
        added_users.append('employee1')
        print("✓ Added user: employee1")
    else:
        print("✗ User 'employee1' already exists")
    
    # Add employee2 if not exists
    if not existing_user2:
        user2 = User(username='employee2', password='employee2')
        db.session.add(user2)
        added_users.append('employee2')
        print("✓ Added user: employee2")
    else:
        print("✗ User 'employee2' already exists")
    
    # Commit changes
    if added_users:
        db.session.commit()
        print(f"\n✓ Successfully added {len(added_users)} user(s) to the database")
    else:
        print("\n✓ No new users to add")
    
    # Display all users
    print("\nCurrent users in database:")
    all_users = User.query.all()
    for user in all_users:
        print(f"  - {user.username}")
