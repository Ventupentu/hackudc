# diary_manager.py
import json
import os
from config import DATABASE_PATH

def guardar_entrada(user_id: str, entrada: dict):
    """
    Guarda una entrada del diario emocional para el usuario.
    """
    data = {}
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            data = json.load(f)
    
    if user_id not in data:
        data[user_id] = []
    
    data[user_id].append(entrada)
    
    with open(DATABASE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def obtener_entradas(user_id: str) -> list:
    """
    Recupera todas las entradas del diario emocional para el usuario.
    """
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            data = json.load(f)
        return data.get(user_id, [])
    return []
