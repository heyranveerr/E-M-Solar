from app import create_app
from models.project import SolarProject
from extensions import db

app = create_app()
with app.app_context():
    new_project = SolarProject(
        name='Test Project from Script',
        status='Active'
    )
    db.session.add(new_project)
    db.session.commit()
    print("Project added successfully")
