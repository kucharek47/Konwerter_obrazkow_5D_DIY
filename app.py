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
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    sha = db.Column(db.String(64), nullable=False)
    posiadane = db.relationship('Posiade', backref='user', lazy='dynamic')
class Posiade(db.Model):
    __tablename__ = 'posiade'
    id = db.Column(db.Integer, primary_key=True)
    id_koloru = db.Column(db.Integer, db.ForeignKey('diamenty.id'))
    ilosc = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diament = db.relationship('Diamenty', backref='posiade', lazy='dynamic')
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

        user = User.query.filter_by(sha=sha_cookie).first()

        if not user:
            return jsonify({"error": "Brak autoryzacji (nieznany uzytkownik)"}), 401

        return f(user_db=user, *args, **kwargs)

    return sha

#NOTE api
@app.route('/api/test_sha', methods=['POST'])
def api_test_sha():
    sha = request.json.get('sha',False)
    if sha:
        if User.query.filter_by(sha=sha).first():
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "brak sha w bazie"}), 401
    else:
        return jsonify({"error":"brak sha"}), 401


@app.route("api/pobranie_kolorow_posiadanych", methods=['GET'])
@wymagane_sha
def api_pobranie_kolorow_posiadanych(db_user):
    posiadane = db_user.posiadane.all()
    lista = []
    for x in posiadane:
        lista.append({
            "id": x.id,
            "id_koloru": x.id_koloru,
            "ilosc": x.ilosc,
            "rgb": [x.diament.r, x.diament.g, x.diament.b],
            "nazwa": x.diament.nazwa,
            "oznaczenie": x.diament.oznaczenie,
        })
    return jsonify(lista), 200
@app.route('/api/pobranie_kolorow', methods=['POST'])
@wymagane_sha
def api_pobranie_kolorow(db_user):
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