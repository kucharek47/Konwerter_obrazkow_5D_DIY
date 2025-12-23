import json

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import Konwerter_obrazkow

slownik_kartki = {
    "A0": [841,1189],
    "A1": [594,841],
    "A2": [420,594],
    "A3": [297,420],
    "A4": [210,297],
    "A5": [148,219],
}
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

@app.route('/')
def hello_world():
    return 'Hello World!'
#note: API
@app.route('/api/zmiana_obrazka', methods=["POST"])
def api_zmiana_obrazka():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    size_name = request.form.get('rozmiar_kartki', 'A4')

    file = request.files['image']
    file_bytes = np.frombuffer(file.read(), np.uint8)
    cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if cv_image is None:
        return jsonify({'error': 'Failed to decode image'}), 400
    try:
        w, h = slownik_kartki[size_name[:2]] if len(size_name) == 3 and size_name[2] == "R" else slownik_kartki[size_name[:2]][::-1]
        konwerter = Konwerter_obrazkow.Konwerter(cv_image, w, h)
        print(konwerter.potrzebne_masz())
        return jsonify({'message': 'Plik przetworzony pomyślnie', 'lok': konwerter.path(), "potrzebne":konwerter.potrzebne_masz()})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
@app.route("/api/dodanie_diamentu", methods=["POST"])
def api_dodanie_diament():
    slownik_zapytania = request.get_json()
    with json.load(open('slownik_posiadanych_kolorow.json')) as f:
        if f[slownik_zapytania["id"]]:
            f[slownik_zapytania["id"]]["ilosc"] += slownik_zapytania["ilosc"]
        else:
            f[slownik_zapytania["id"]] = {
                "nazwa": slownik_zapytania["nazwa"],
                "rgb": slownik_zapytania["rgb"],
                "oznaczenie": slownik_zapytania["oznaczenie"],
                "ilosc": slownik_zapytania["ilosc"],
            }
    json.dump(f, open('slownik_posiadanych_kolorow.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
@app.route("/api/edycja_diamentu", methods=["POST"])
def api_edycja_diament():
    slownik_zapytania = request.get_json()
    with json.load(open('slownik_posiadanych_kolorow.json')) as f:
        f[slownik_zapytania["id"]] = {
            "nazwa": slownik_zapytania["nazwa"],
            "rgb": slownik_zapytania["rgb"],
            "oznaczenie": slownik_zapytania["oznaczenie"],
            "ilosc": slownik_zapytania["ilosc"],
        }
    json.dump(f, open('slownik_posiadanych_kolorow.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
@app.route("/api/odczyt_diamentu", methods=["GET"])
def api_odczyt_diament():
    slownik = json.load(open('slownik_posiadanych_kolorow.json',encoding='utf-8'))
    lista = []
    for x in slownik:
        slownik_tmp = {}
        slownik_tmp |= slownik[x]
        lista.append(slownik_tmp)
    return jsonify(lista)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=42310, debug=True)
