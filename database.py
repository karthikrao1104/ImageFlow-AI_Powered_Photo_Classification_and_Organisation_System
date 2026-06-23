from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    photos = db.relationship('Photo', backref='user', lazy=True, cascade="all, delete-orphan")
    persons = db.relationship('Person', backref='user', lazy=True, cascade="all, delete-orphan")

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    faces = db.relationship('Face', backref='photo', lazy=True, cascade="all, delete-orphan")

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False, default="Unknown Person")
    share_token = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    faces = db.relationship('Face', backref='person', lazy=True, cascade="all, delete-orphan")

class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    face_filename = db.Column(db.String(255), nullable=False)
    encoding_json = db.Column(db.Text, nullable=False)
    
    def get_encoding(self):
        import numpy as np
        return np.array(json.loads(self.encoding_json))
    
    def set_encoding(self, encoding_array):
        self.encoding_json = json.dumps(encoding_array.tolist())
