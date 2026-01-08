import datetime
import os
from flask import Flask, request, jsonify
from functools import wraps
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import Konwerter_obrazkow

plik_do_zapisu_odwiedzajacych = open("odwiedzajacy","a",encoding="utf-8")

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
#NOTE wymagania
def wymagane_sha(f):
    @wraps(f)
    def sha(*args, **kwargs):
        sha_cookie = request.cookies.get('sha_user')

        if not sha_cookie:
            return jsonify({"error": "Brak autoryzacji (brak ciasteczka)"}), 401

        dostep_j = Dostep.query.filter_by(sha=sha_cookie).first()

        if not dostep_j:
            return jsonify({"error": "Brak autoryzacji (nieznany uzytkownik)"}), 401
        id_user = dostep_j.user_id

        return f(id_user=id_user, *args, **kwargs)

    return sha

#NOTE api
@app.route('/api/test_sha', methods=['POST'])
def api_test_sha():
    sha = request.json.get('sha',False)
    if sha:
        dostep = Dostep.query.filter_by(sha=sha).first()
        if dostep:
            plik_do_zapisu_odwiedzajacych.write(f"{dostep.nazwa} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "brak sha w bazie"}), 401
    else:
        return jsonify({"error":"brak sha"}), 401


@app.route("/api/pobranie_kolorow_posiadanych", methods=['GET'])
@wymagane_sha
def api_pobranie_kolorow_posiadanych(id_user):
    dane = Posiade.query.filter_by(user_id=id_user).all()
    slownik = {}
    for x in dane:
        slownik[x.id_koloru] =  {
            "ilosc": x.ilosc
        }
    kolor = Diamenty.query.filter(Diamenty.id.in_(list(slownik.keys()))).all()
    for x in kolor:
        slownik[x.id_koloru]["nazwa"] = x.nazwa
        slownik[x.id_koloru]["oznaczenie"] = x.oznaczenie
        slownik[x.id_koloru]["rgb"] = [x.r,x.g,x.b]

    return jsonify(slownik), 200
@app.route('/api/pobranie_kolorow', methods=['POST'])
@wymagane_sha
def api_pobranie_kolorow(id_user):
    diamenty = Diamenty.query.all()
    lista = []
    for x in diamenty:
        lista.append({
            "id": x.id,
            "rgb": [x.r, x.g, x.b],
            "nazwa": x.nazwa,
            "oznaczenie": x.oznaczenie,
        })
    return jsonify(lista), 200