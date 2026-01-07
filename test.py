
from sqlalchemy import create_engine

engine = create_engine("sqlite:///baza_diamentow.db", echo=True)