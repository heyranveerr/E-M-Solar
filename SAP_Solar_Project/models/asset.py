from extensions import db

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100))
    last_maintenance = db.Column(db.String(20))
    status = db.Column(db.String(50))
