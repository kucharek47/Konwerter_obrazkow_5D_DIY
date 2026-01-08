import os
from flask import Flask, request, jsonify
from functools import wraps
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import Konwerter_obrazkow
app = Flask(__name__, static_folder=None)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baza.db'
app.config["WYNIKI_GENEROWANIA"] = os.path.join('static', 'wygenerowane')

CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)

os.makedirs(app.config["WYNIKI_GENEROWANIA"], exist_ok=True)

#NOTE baza danych
class User(db.Model): #lazy dinamic
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    rola =db.Column(db.String(20), nullable=False)

    dostep = db.relationship('Dostep', backref='user', lazy='dynamic')
    info = db.relationship('Info', backref='user', lazy='dynamic')
    posiadane = db.relationship('Posiade', backref='user', lazy='dynamic')

class Dostep(db.Model):
    __tablename__ = 'dostep'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    nazwa = db.Column(db.String(50))
    sha = db.Column(db.String(64), nullable=False)
class Posiade(db.Model):
    __tablename__ = 'posiade'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    id_koloru = db.Column(db.Integer, db.ForeignKey('diamenty.id'))
    ilosc = db.Column(db.Integer, nullable=False)
class Info(db.Model): #Zignorowac czesc stworzona do zabawy/lepszego zrozumienia baz danych
    __tablename__ = 'info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    miasto = db.Column(db.String(50))
    kod_pocztowy = db.Column(db.String(7))
    ulica = db.Column(db.String(50))
    numer_domu = db.Column(db.Integer)
    numer_lokalu = db.Column(db.Integer)

class Diamenty(db.Model):
    __tablename__ = 'diamenty'

    id = db.Column(db.Integer, primary_key=True)

    r = db.Column(db.Integer, nullable=False)
    g = db.Column(db.Integer, nullable=False)
    b = db.Column(db.Integer, nullable=False)
    oznaczenie = db.Column(db.String(2), nullable=False)
    nazwa = db.Column(db.String(50), nullable=False)
with app.app_context():
    db.create_all()
    User.add()