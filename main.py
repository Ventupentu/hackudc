# archivo: main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import text2emotion as te
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

import nltk

# Descarga los recursos necesarios si no están disponibles
nltk.download('punkt_tab')
nltk.download('punkt')


# Archivo para almacenar las entradas del diario emocional
DIARY_FILE = "diario.json"

# Función para integrar (simulada) la API de MISTRAL AI para RAG
def call_mistral_rag(prompt: str) -> str:
    # Aquí se utilizaría la API key de MISTRAL AI para enriquecer la respuesta.
    # En este ejemplo simulamos la respuesta.
    api_key = os.getenv("MISTRAL_API_KEY")  # Reemplaza por tu API key real
    # Supongamos que hacemos una petición a un endpoint de MISTRAL:
    # response = requests.post("https://api.mistralai.com/rag", headers={"Authorization": f"Bearer {api_key}"}, json={"prompt": prompt})
    # return response.json().get("respuesta", "")
    return f"Esta es una respuesta enriquecida basada en el análisis RAG para: '{prompt}'"

# Modelo para los mensajes de usuario
class Mensaje(BaseModel):
    texto: str

# Modelo para las entradas del diario
class DiarioEntrada(BaseModel):
    texto: str
    fecha: str = None  # Se asigna la fecha actual si no se proporciona

# Modelo para los objetivos de personalidad
class Objetivo(BaseModel):
    descripcion: str

# Función que genera una respuesta básica según las emociones detectadas
def generar_respuesta(emociones, texto):
    if emociones.get("Sad", 0) > 0.5:
        return "Lamento que te sientas triste. ¿Quieres compartir qué te preocupa?"
    elif emociones.get("Angry", 0) > 0.5:
        return "Parece que estás enfadado. ¿Quieres hablar sobre lo que te molesta?"
    elif emociones.get("Happy", 0) > 0.5:
        return "¡Me alegra que estés contento! Cuéntame más sobre tu día."
    elif emociones.get("Surprise", 0) > 0.5:
        return "Parece que algo te ha sorprendido. ¿Quieres contarme qué pasó?"
    else:
        return "Cuéntame más sobre tu día."

# Endpoint para analizar un mensaje y generar una respuesta enriquecida
@app.post("/analizar")
async def analizar_mensaje(mensaje: Mensaje):
    emociones = te.get_emotion(mensaje.texto)
    respuesta_inicial = generar_respuesta(emociones, mensaje.texto)
    # Llamada simulada a MISTRAL AI para obtener respuesta enriquecida
    respuesta_enriquecida = call_mistral_rag(mensaje.texto)
    respuesta_final = f"{respuesta_inicial}\n\nAdemás: {respuesta_enriquecida}"
    return {"emociones": emociones, "respuesta": respuesta_final}

# Endpoint para agregar una entrada al diario emocional
@app.post("/diario")
async def agregar_diario(entrada: DiarioEntrada):
    if not entrada.fecha:
        entrada.fecha = datetime.now().isoformat()
    # Analiza las emociones en la entrada
    emociones = te.get_emotion(entrada.texto)
    registro = {
        "fecha": entrada.fecha,
        "texto": entrada.texto,
        "emociones": emociones
    }
    # Carga las entradas existentes o inicializa la lista
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, "r", encoding="utf-8") as f:
            diario = json.load(f)
    else:
        diario = []
    diario.append(registro)
    # Guarda las entradas actualizadas
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(diario, f, ensure_ascii=False, indent=4)
    return {"mensaje": "Entrada agregada al diario", "registro": registro}

# Endpoint para obtener un perfil de personalidad basado en el diario
@app.get("/perfil")
async def obtener_perfil():
    if not os.path.exists(DIARY_FILE):
        raise HTTPException(status_code=404, detail="No hay entradas de diario")
    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        diario = json.load(f)
    # Perfil emocional promedio (dummy) basado en las entradas del diario
    perfil = {"Happy": 0, "Sad": 0, "Angry": 0, "Surprise": 0, "Fear": 0}
    count = len(diario)
    if count == 0:
        raise HTTPException(status_code=404, detail="No hay entradas de diario")
    for entrada in diario:
        for emo in perfil.keys():
            perfil[emo] += entrada["emociones"].get(emo, 0)
    # Calcular el promedio
    for emo in perfil:
        perfil[emo] = perfil[emo] / count
    # Lógica simple para sugerir un perfil (se puede ampliar con Eneagrama o Big Five)
    perfil_personalidad = "Personalidad equilibrada"
    if perfil["Sad"] > 0.5:
        perfil_personalidad = "Tendencia a la melancolía"
    if perfil["Angry"] > 0.5:
        perfil_personalidad = "Tendencia a la irritabilidad"
    return {"perfil_emocional": perfil, "sugerencia": perfil_personalidad}

# Endpoint para establecer objetivos de personalidad y recibir recomendaciones
@app.post("/objetivos")
async def establecer_objetivos(objetivo: Objetivo):
    desc = objetivo.descripcion.lower()
    recomendacion = ""
    if "neuroticismo" in desc:
        recomendacion = "Te recomendamos practicar técnicas de mindfulness y llevar un registro emocional diario para reducir el neuroticismo."
    elif "extraversión" in desc:
        recomendacion = "Te sugerimos participar en actividades sociales y ejercicios de comunicación para aumentar la extraversión."
    else:
        recomendacion = "Por favor, proporciona más detalles sobre tu objetivo para ofrecerte una recomendación personalizada."
    return {"objetivo": objetivo.descripcion, "recomendacion": recomendacion}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
