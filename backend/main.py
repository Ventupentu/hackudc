from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv
import text2emotion as te
import re
import json
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

load_dotenv()

from database import Database

app = FastAPI()

# Configuración de CORS (ajusta en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

# -------------------------------
# Modelos Pydantic
# -------------------------------
class Message(BaseModel):
    role: str
    content: str

class Conversation(BaseModel):
    messages: list[Message]
    username: str

class UserAuth(BaseModel):
    username: str
    password: str

class DiaryEntry(BaseModel):
    username: str
    password: str
    entry: str
    fecha: str = None  # Si no se proporciona, se usa la fecha actual
    editar: bool = False

# -------------------------------
# Función para llamar a la API de Mistral
# -------------------------------
def call_mistral_rag(conversation_messages: list[dict]) -> str:
    from mistralai import Mistral
    api_key = os.environ.get("MISTRAL_API_KEY")
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    chat_response = client.chat.complete(
        model=model,
        messages=conversation_messages
    )
    return chat_response.choices[0].message.content

# -------------------------------
# Utilidad para convertir entradas del diario a texto estructurado
# -------------------------------
def list_of_dicts_to_entries_text(entries: list) -> str:
    text_entries = ""
    for entry in entries:
        date = entry["date"]
        text = entry["entry"]
        emotions = entry["emotions"]
        text_entries += f"Fecha: {date}\nEntrada: {text}\nEmociones:\n"
        for emo, value in emotions.items():
            text_entries += f"- {emo}: {value}\n"
        text_entries += "\n"
    return text_entries

# -------------------------------
# Función para calcular Big Five
# -------------------------------
def calculate_big_five(username: str) -> dict:
    """
    Calcula los valores Big Five a partir de las entradas del diario.
    Envía un prompt a la API para que analice las entradas y devuelva
    los rasgos de personalidad Big Five en formato JSON.
    """
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        return {
            "Openness": 0,
            "Conscientiousness": 0,
            "Extraversion": 0,
            "Agreeableness": 0,
            "Neuroticism": 0
        }
    
    entries_text = list_of_dicts_to_entries_text(diary_entries)
    
    prompt = f"""
Analiza las siguientes entradas del diario y determina los rasgos de personalidad Big Five del usuario.
Los números deben de ser del 0-100
Responde únicamente con un JSON EXACTO en el siguiente formato:
{{
  "Openness": <number>,
  "Conscientiousness": <number>,
  "Extraversion": <number>,
  "Agreeableness": <number>,
  "Neuroticism": <number>
}}
Entradas del diario:
{entries_text}
    """
    
    try:
        big_five_response = call_mistral_rag([{"role": "system", "content": prompt}])
        clean_response = re.sub(r"^```(?:json)?\s*", "", big_five_response).strip()
        clean_response = re.sub(r"\s*```$", "", clean_response)
        big_five = json.loads(clean_response)
    except Exception as e:
        print("Error parsing Big Five response:", e)
        big_five = {
            "Openness": 0,
            "Conscientiousness": 0,
            "Extraversion": 0,
            "Agreeableness": 0,
            "Neuroticism": 0
        }
    
    print("Big Five values:", big_five)
    return big_five

# -------------------------------
# Endpoints
# -------------------------------

@app.get("/")
async def root():
    return {"mensaje": "Backend funcionando"}

# Registro de usuario
@app.post("/register")
async def register(user: UserAuth):
    try:
        db.register_user(user.username, user.password)
        return {"mensaje": "Usuario registrado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error en registro: " + str(e))

# Login de usuario
@app.post("/login")
async def login(user: UserAuth):
    valid = db.verify_user(user.username, user.password)
    if not valid:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"mensaje": "Login exitoso"}

# Recuperar el historial de chat (para iniciar la conversación)
@app.get("/start_chat")
async def start_chat(username: str = Query(...)):
    chat_history = db.get_chat_history(username, limit=10)
    return {"conversation": chat_history}

# Chat: Envía mensaje y obtiene respuesta del chatbot (incluyendo análisis emocional)
@app.post("/chat")
async def chat(conversation: Conversation):
    if not conversation.messages:
        raise HTTPException(status_code=400, detail="No hay mensajes en la conversación")
    username = conversation.username
    conversation_list = [msg.dict() for msg in conversation.messages]
    last_message = conversation.messages[-1]
    emociones = {}
    if last_message.role == "user":
        emociones = te.get_emotion(last_message.content)
    emocion_dominante = max(emociones, key=emociones.get, default="neutral")
    
    # Crear mensaje del sistema con información emocional
    diary_entries = db.get_diary_entries(username)
    perfil = {"Happy": 0, "Angry": 0, "Surprise": 0, "Sad": 0, "Fear": 0}
    if diary_entries:
        count = 0
        for entry in diary_entries:
            for emo in perfil:
                perfil[emo] += float(entry["emotions"].get(emo, 0))
            count += 1
        for emo in perfil:
            perfil[emo] = perfil[emo] / count if count > 0 else 0
    else:
        perfil = {"Happy": 0, "Angry": 0, "Surprise": 0, "Sad": 0, "Fear": 0}
    
    sys_msg = {
        "role": "system",
        "content": f"Eres un chatbot emocional orientado a apoyar al usuario. El usuario {username} muestra una emoción dominante de '{emocion_dominante}'. Su perfil promedio es: {perfil}"
    }
    conversation_list.insert(0, sys_msg)
    try:
        respuesta = call_mistral_rag(conversation_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al llamar a Mistral: " + str(e))
    
    chat_piece = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "human_message": last_message.content,
        "bot_message": respuesta,
        "emotions": emociones,
    }
    db.insert_chat_history(username, chat_piece)
    return {"respuesta": respuesta, "emociones": emociones}

# Obtener las entradas del diario (GET)
@app.get("/diario")
async def obtener_diario(username: str = Query(...), password: str = Query(...)):
    if not db.verify_user(username, password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    entries = db.get_diary_entries(username)
    if not entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    return {"diario": entries}

# Crear o actualizar una entrada del diario (POST)
@app.post("/diario")
async def agregar_diario(entry: DiaryEntry):
    if not db.verify_user(entry.username, entry.password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    target_date = entry.fecha if entry.fecha else datetime.now().strftime("%Y-%m-%d")
    new_emotions = te.get_emotion(entry.entry)
    diary_data = {
        "date": target_date,
        "entry": entry.entry,
        "emotions": new_emotions
    }
    db.insert_diary_entry(entry.username, diary_data)
    return {"mensaje": "Entrada actualizada en el diario", "registro": diary_data}

# Perfilado: Obtiene perfil emocional, Big Five y eneagrama
@app.get("/perfilado")
async def perfilado(username: str = Query(...), password: str = Query(...)):
    if not db.verify_user(username, password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    
    # Calcular perfil emocional promedio
    perfil_emocional = {"Happy": 0, "Angry": 0, "Surprise": 0, "Sad": 0, "Fear": 0}
    count = 0
    for entry in diary_entries:
        for emo in perfil_emocional:
            perfil_emocional[emo] += float(entry["emotions"].get(emo, 0))
        count += 1
    for emo in perfil_emocional:
        perfil_emocional[emo] = perfil_emocional[emo] / count if count > 0 else 0
    emocion_dominante = max(perfil_emocional, key=perfil_emocional.get)
    tendencia = {
        "Happy": "Tendencia a la felicidad",
        "Angry": "Tendencia a la irritabilidad",
        "Surprise": "Tendencia a la sorpresa",
        "Sad": "Tendencia a la melancolía",
        "Fear": "Tendencia al miedo"
    }.get(emocion_dominante, "Personalidad equilibrada")
    
    # Calcular Big Five
    big_five = calculate_big_five(username)
    
    # Calcular Eneagrama
    entries_text = list_of_dicts_to_entries_text(diary_entries)
    prompt = f"""
Analiza las siguientes entradas del diario y determina el eneagrama del usuario.
Responde en el siguiente formato JSON EXACTO:
{{
  "eneagrama_type": "Eneatipo <numero> (<nombre>)",
  "description": "<Descripción breve>",
  "recommendation": "<Recomendación concreta>"
}}
Datos:
{entries_text}
    """
    try:
        eneagrama_resp = call_mistral_rag([{"role": "system", "content": prompt}])
        clean_resp = re.sub(r"^```(?:json)?\s*", "", eneagrama_resp).strip()
        clean_resp = re.sub(r"\s*```$", "", clean_resp)
        eneagrama = json.loads(clean_resp)
    except Exception as e:
        print("Error parsing eneagrama:", e)
        eneagrama = {}
    
    return {"perfil": {
        "perfil_emocional": perfil_emocional,
        "tendencia": tendencia,
        "big_five": big_five,
        "eneagrama": eneagrama
    }}

# Objetivo: Genera objetivos personalizados a partir del diario
@app.get("/Objetivo")
async def objetivo(username: str = Query(...), password: str = Query(...)):
    if not db.verify_user(username, password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    entries_text = list_of_dicts_to_entries_text(diary_entries)
    prompt = f"""
Analiza los siguientes textos del diario y las emociones detectadas en ellos. A partir de ello, propone una lista de objetivos personalizados que el usuario podría plantearse para mejorar su estado emocional.
Debes responder en formato JSON EXACTO:
{{
  "objetivos": [
      "<Objetivo 1>",
      "<Objetivo 2>",
      "<Objetivo 3>",
      "<Objetivo 4>",
      "<Objetivo 5>"
  ]
}}
Datos:
{entries_text}
    """
    try:
        respuesta_obj = call_mistral_rag([{"role": "system", "content": prompt}])
        clean_resp = re.sub(r"^```(?:json)?\s*", "", respuesta_obj).strip()
        clean_resp = re.sub(r"\s*```$", "", clean_resp)
        objetivos = json.loads(clean_resp)
    except Exception as e:
        print("Error parsing objetivos:", e)
        objetivos = {"objetivos": []}
    return {"objetivo": objetivos}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
