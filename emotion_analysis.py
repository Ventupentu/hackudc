# emotion_analysis.py
import text2emotion as te

def analizar_emociones(texto: str) -> dict:
    """
    Analiza el texto y retorna un diccionario con la puntuación de cada emoción.
    Ejemplo de salida: {"Happy": 0.0, "Angry": 0.0, "Surprise": 0.0, "Sad": 0.6, "Fear": 0.4}
    """
    emociones = te.get_emotion(texto)
    return emociones
