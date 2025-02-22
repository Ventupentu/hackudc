# archivo: main.py
import os
import nltk
import text2emotion as te
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import mysql.connector

from access_bd import AccessBD

load_dotenv()  # Carga las variables de entorno

app = FastAPI()
db = AccessBD()

# Descarga recursos de NLTK (si aún no se han descargado)
nltk.download('punkt_tab')
nltk.download('punkt')

# ----------------------------------------------
# Modelos para Chat, Autenticación y Diario
# ----------------------------------------------
class Message(BaseModel):
    role: str  # "user", "assistant", etc.
    content: str

class Conversation(BaseModel):
    messages: list[Message]

class UserAuth(BaseModel):
    username: str
    password: str

# Agregamos el campo opcional "fecha" (en formato "YYYY-MM-DD") para poder editar entradas de días anteriores.
class DiaryEntry(BaseModel):
    username: str
    password: str
    text: str
    fecha: str = None  # Opcional; si no se proporciona, se usará la fecha actual.

# ----------------------------------------------
# Endpoint de Chat (usando la API oficial de Mistralai)
# ----------------------------------------------
def call_mistral_rag(conversation_messages: list[dict]) -> str:
    from mistralai import Mistral
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    chat_response = client.chat.complete(
        model=model,
        messages=conversation_messages
    )
    return chat_response.choices[0].message.content

@app.post("/chat")
async def chat(conversation: Conversation):
    if not conversation.messages:
        raise HTTPException(status_code=400, detail="No hay mensajes en la conversación")
    conversation_list = [msg.dict() for msg in conversation.messages]
    last_message = conversation.messages[-1]
    emociones = {}
    if last_message.role == "user":
        emociones = te.get_emotion(last_message.content)
    respuesta = call_mistral_rag(conversation_list)
    return {"respuesta": respuesta, "emociones": emociones}

# ----------------------------------------------
# Endpoint de Registro
# ----------------------------------------------
@app.post("/register")
async def register(user: UserAuth):
    user_exit = db.check_user(user.username)
    if user_exit:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    db.register_user(user.username, user.password)
    return {"mensaje": "Usuario registrado exitosamente"}

# ----------------------------------------------
# Endpoint de Login (verifica contraseña hasheada)
# ----------------------------------------------
@app.post("/login")
async def login(user: UserAuth):
    success = db.verify_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"mensaje": "Login exitoso"}

# ----------------------------------------------
# Endpoint para agregar o actualizar la entrada del Diario (única entrada por día, según la fecha seleccionada)
# ----------------------------------------------
@app.post("/diario")
async def agregar_diario(entry: DiaryEntry):
    success = db.verify_user(entry.username, entry.password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    # Usar la fecha proporcionada o, si es None, la fecha actual
    target_date = entry.fecha if entry.fecha is not None else datetime.now().strftime("%Y-%m-%d")
    entry_for_date = db.get_diary_entry(entry.username, target_date)

    if entry_for_date is not None:
        # Sobrescribir la entrada con el nuevo texto (y recalcular las emociones)
        new_text = f"{entry_for_date['text']}\n{entry.text}"
        new_emotions = te.get_emotion(new_text)
        entry_for_date["text"] = new_text
        entry_for_date["emotions"] = new_emotions
        entry_for_date["date"] = target_date
        updated_entry = entry_for_date
    else:
        fecha = target_date
        new_emotions = te.get_emotion(entry.text)
        updated_entry = {"text": entry.text, "emotions": new_emotions, "date": fecha}
    
    db.insert_diary_entry(entry.username, updated_entry)
    return {"mensaje": "Entrada actualizada en el diario", "registro": updated_entry}

# ----------------------------------------------
# Endpoint para obtener la entrada del Diario para un usuario (por fecha)
# ----------------------------------------------
@app.get("/diario")
async def obtener_diario(username: str = Query(...), password: str = Query(...)):
    success = db.verify_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    diary = db.get_diary_entries(username)
    if not diary:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    return {"diario": diary}

# ----------------------------------------------
# Endpoint para obtener tendencias emocionales (Perfil)
# ----------------------------------------------
@app.get("/perfil")
async def obtener_perfil():
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT entry FROM user_prueba WHERE entry <> ''")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    perfil = {"Happy": 0, "Sad": 0, "Angry": 0, "Surprise": 0, "Fear": 0}
    count = 0
    for row in rows:
        try:
            diary_entries = json.loads(row["entry"])
            for entry_data in diary_entries:
                emociones = entry_data.get("emociones", {})
                for emo in perfil.keys():
                    perfil[emo] += emociones.get(emo, 0)
                count += 1
        except Exception:
            continue
    if count == 0:
        raise HTTPException(status_code=404, detail="No se encontraron entradas válidas")
    for emo in perfil:
        perfil[emo] = perfil[emo] / count
    perfil_personalidad = "Personalidad equilibrada"
    if perfil["Sad"] > 0.5:
        perfil_personalidad = "Tendencia a la melancolía"
    if perfil["Angry"] > 0.5:
        perfil_personalidad = "Tendencia a la irritabilidad"
    return {"perfil_emocional": perfil, "sugerencia": perfil_personalidad}

# ----------------------------------------------
# Punto de entrada de la aplicación
# ----------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)