from app import db

class KorDrug(db.Model):
    __tablename__ = 'kordrugs'
    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(255), nullable=False)
    ent_name = db.Column(db.String(255), nullable=False)
    efcy = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(255))
    atc_code = db.Column(db.String(255))
    ingr_string = db.Column(db.Text)