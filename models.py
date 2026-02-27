from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    trips = db.relationship("Trip", backref="author", lazy=True)


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    story = db.Column(db.Text, nullable=False)

    country = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)

    # Геопозиция
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)

    # Фото
    image_url = db.Column(db.String(500), default="")

    # Стоимость
    budget = db.Column(db.Integer, default=0)

    # Оценки 1..5
    safety = db.Column(db.Integer, default=3)
    transport = db.Column(db.Integer, default=3)
    crowd = db.Column(db.Integer, default=3)
    nature = db.Column(db.Integer, default=3)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)