# database_manager.py
import json
import os
from config import DATABASE_PATH

def cargar_datos() -> dict:
    """
    Carga los datos almacenados en la base de datos JSON.
    """
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(data: dict):
    """
    Guarda los datos en la base de datos JSON.
    """
    with open(DATABASE_PATH, "w") as f:
        json.dump(data, f, indent=4)
