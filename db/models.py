from app.app import db 
from sqlalchemy.sql import func


class Prescription(db.Model):
    __tablename__ = 'prescription' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medicine_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(150),nullable=False)
    instructions = db.Column(db.String(250),nullable=False)
    createdAt=db.Column(db.DateTime(timezone=True), default=func.now())
    doctor=db.Column(db.String(150),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='prescriptions')


class User(db.Model):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150),nullable=False)
    last_name = db.Column(db.String(150),nullable=False)
    age = db.Column(db.Integer)
    prescriptions = db.relationship("Prescription", back_populates='user')