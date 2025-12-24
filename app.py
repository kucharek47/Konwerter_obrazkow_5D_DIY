import json
import os
import sys
import threading
import time
import shutil
import tkinter as tk
from tkinter import filedialog
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import webview
import Konwerter_obrazkow


if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = BASE_DIR
    return os.path.join(base_path, relative_path)


GENERATED_DIR = os.path.join(BASE_DIR, 'static', 'wygenerowane')
JSON_PATH = os.path.join(BASE_DIR, 'slownik_posiadanych_kolorow.json')

if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR, exist_ok=True)

os.chdir(BASE_DIR)

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/*": {"origins": "*"}})

ANGULAR_DIST_PATH = resource_path('browser')

@app.route('/static/wygenerowane/<path:filename>')
def serve_generated_files(filename):
    return send_from_directory(GENERATED_DIR, filename)


@app.route('/')
def index():
    return send_from_directory(ANGULAR_DIST_PATH, 'index.html')


@app.route('/<path:path>')
def serve_angular_files(path):
    file_path = os.path.join(ANGULAR_DIST_PATH, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(ANGULAR_DIST_PATH, path)
    return send_from_directory(ANGULAR_DIST_PATH, 'index.html')

@app.route('/api/pobieranie/<path:filename>', methods=['GET'])
def api_pobieranie(filename):
    source_file = os.path.join(GENERATED_DIR, filename)

    if not os.path.exists(source_file):
        return jsonify({'error': 'File not found'}), 404

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        save_path = filedialog.asksaveasfilename(
            title="Zapisz wzór",
            initialfile=filename,
            defaultextension=".png",
            filetypes=[("Obraz PNG", "*.png"), ("Wszystkie pliki", "*.*")]
        )
        root.destroy()

        if save_path:
            shutil.copy2(source_file, save_path)
            return jsonify({'status': 'saved', 'path': save_path})
        else:
            return jsonify({'status': 'cancelled'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        base_size = size_name[:2]
        slownik_kartki = {
            "A0": [841, 1189], "A1": [594, 841], "A2": [420, 594],
            "A3": [297, 420], "A4": [210, 297], "A5": [148, 219],
        }

        if len(size_name) == 3 and size_name[2] == "R":
            w, h = slownik_kartki[base_size]
        else:
            w, h = slownik_kartki[base_size][::-1]

        konwerter = Konwerter_obrazkow.Konwerter(cv_image, w, h)

        path_obj = konwerter.path()
        filename = os.path.basename(path_obj)

        return jsonify({
            'message': 'Plik przetworzony pomyślnie',
            'lok': filename,
            "potrzebne": konwerter.potrzebne_masz()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/dodanie_diamentu", methods=["POST"])
def api_dodanie_diament():
    slownik_zapytania = request.get_json()
    try:
        with open(JSON_PATH, encoding='utf-8') as f_read:
            f = json.load(f_read)
    except FileNotFoundError:
        f = {}

    if slownik_zapytania["nazwa"] in f:
        f[slownik_zapytania["nazwa"]]["ilosc"] += slownik_zapytania["ilosc"]
    else:
        f[slownik_zapytania["nazwa"]] = {
            "id": slownik_zapytania["id"],
            "rgb": slownik_zapytania["rgb"],
            "oznaczenie": slownik_zapytania["oznaczenie"],
            "ilosc": slownik_zapytania["ilosc"],
        }

    with open(JSON_PATH, 'w', encoding='utf-8') as f_write:
        json.dump(f, f_write, indent=4, ensure_ascii=False)
    return jsonify({"status": "dodano pomyslnie"})


@app.route("/api/edycja_diamentu", methods=["POST"])
def api_edycja_diament():
    slownik_zapytania = request.get_json()
    try:
        with open(JSON_PATH, encoding='utf-8') as f_read:
            f = json.load(f_read)

        f[slownik_zapytania["nazwa"]] = {
            "id": slownik_zapytania["id"],
            "rgb": slownik_zapytania["rgb"],
            "oznaczenie": slownik_zapytania["oznaczenie"],
            "ilosc": slownik_zapytania["ilosc"],
        }
        with open(JSON_PATH, 'w', encoding='utf-8') as f_write:
            json.dump(f, f_write, indent=4, ensure_ascii=False)
        return jsonify({"status": "edytowano pomyslnie"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/odczyt_diamentu", methods=["GET"])
def api_odczyt_diament():
    try:
        with open(JSON_PATH, encoding='utf-8') as f:
            slownik = json.load(f)
    except FileNotFoundError:
        return jsonify([])

    lista = []
    for x in slownik:
        lista.append({"nazwa": x} | slownik[x])
    return jsonify(lista)


@app.route("/api/zapisz_obraz", methods=["POST"])
def api_zapisz_obraz():
    slownik = request.get_json()
    try:
        with open(JSON_PATH, encoding='utf-8') as f_read:
            f = json.load(f_read)

        for x in slownik:
            if x in f:
                if f[x]["ilosc"] <= slownik[x]:
                    f[x]["ilosc"] = 0
                else:
                    f[x]["ilosc"] -= slownik[x]

        with open(JSON_PATH, 'w', encoding='utf-8') as f_write:
            json.dump(f, f_write, indent=4, ensure_ascii=False)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def start_server():
    app.run(host='127.0.0.1', port=42310, debug=False, use_reloader=False)


if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    time.sleep(1)
    webview.create_window(
        title='Aplikacja Diamentowa',
        url='http://127.0.0.1:42310',
        width=1200,
        height=900,
        resizable=True
    )

    webview.start()