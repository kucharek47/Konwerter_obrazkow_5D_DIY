import os
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
import Konwerter_obrazkow

silnik_sqlalchemy = create_engine('sqlite:///diy.db', echo=False)

Base = declarative_base()

class dane(Base):
    __tablename__ = 'dane'
    id = Column(Integer, primary_key=True)
    sha = Column(String(64))



GENERATED_DIR = os.path.join('static', 'wygenerowane')

if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR, exist_ok=True)

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/*": {"origins": "*"}})

