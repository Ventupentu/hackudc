# utils.py
from datetime import datetime

def obtener_fecha_actual() -> str:
    """
    Retorna la fecha y hora actual en formato legible.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
