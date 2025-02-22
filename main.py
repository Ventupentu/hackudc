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

from passlib.context import CryptContext

load_dotenv()  # Carga las variables de entorno

app = FastAPI()

# Configuración del contexto para hash de contraseñas (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Descarga recursos de NLTK (si aún no se han descargado)
nltk.download('punkt_tab')
nltk.download('punkt')

# ----------------------------------------------
# Función para obtener conexión a la base de datos MySQL
# ----------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
         host=os.environ["DB_HOST"],
         database=os.environ["DB_NAME"],
         user=os.environ["DB_USER"],
         password=os.environ["DB_PASSWORD"]
    )

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

class DiaryEntry(BaseModel):
    username: str
    password: str
    texto: str

# ----------------------------------------------
# Endpoint de Chat (usando la API oficial de Mistralai)
# ----------------------------------------------
def call_mistral_rag(conversation_messages: list[dict]) -> str:
    """
    Llama a la API de Mistralai utilizando la librería oficial.
    Según la documentación:
    
        from mistralai import Mistral
        api_key = os.environ["MISTRAL_API_KEY"]
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)
        chat_response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": "Pregunta..."}]
        )
        print(chat_response.choices[0].message.content)
    
    Se retorna el contenido de la respuesta.
    """
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
    
    # Convertir el historial de mensajes a lista de diccionarios
    conversation_list = [msg.dict() for msg in conversation.messages]
    
    # Opcional: analizar emociones del último mensaje del usuario
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
    conn = get_db_connection()
    cursor = conn.cursor()
    # Verificar si el usuario ya existe
    cursor.execute("SELECT COUNT(*) FROM user_prueba WHERE username = %s", (user.username,))
    (count,) = cursor.fetchone()
    if count > 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    # Asignar timestamp actual y un entry vacío (almacenado como arreglo JSON)
    current_time = datetime.now().isoformat()
    empty_entry = "[]"  # Un arreglo JSON vacío
    # Hashear la contraseña
    hashed_password = pwd_context.hash(user.password)
    cursor.execute(
        "INSERT INTO user_prueba (username, password, date, entry) VALUES (%s, %s, %s, %s)",
        (user.username, hashed_password, current_time, empty_entry)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Usuario registrado exitosamente"}

# ----------------------------------------------
# Endpoint de Login (verifica contraseña hasheada)
# ----------------------------------------------
@app.post("/login")
async def login(user: UserAuth):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM user_prueba WHERE username = %s LIMIT 1", (user.username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    stored_password = result[0]
    if not pwd_context.verify(user.password, stored_password):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"mensaje": "Login exitoso"}

# ----------------------------------------------
# Endpoint para agregar una entrada al Diario (actualiza la misma fila)
# ----------------------------------------------
@app.post("/diario")
async def agregar_diario(entry: DiaryEntry):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Verificar credenciales y obtener la entrada actual del usuario
    cursor.execute("SELECT password, entry FROM user_prueba WHERE username = %s LIMIT 1", (entry.username,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    stored_password = result[0]
    if not pwd_context.verify(entry.password, stored_password):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    existing_entry = result[1]  # Esta columna contiene el arreglo JSON de entradas
    try:
        diary_list = json.loads(existing_entry) if existing_entry and existing_entry.strip() != "" else []
    except Exception:
        diary_list = []
    # Crear la nueva entrada del diario
    fecha = datetime.now().isoformat()
    emociones = te.get_emotion(entry.texto)
    new_diary_entry = {
        "texto": entry.texto,
        "emociones": emociones,
        "timestamp": fecha
    }
    # Agregar la nueva entrada al arreglo existente
    diary_list.append(new_diary_entry)
    new_diary_json = json.dumps(diary_list, ensure_ascii=False)
    # Actualizar la fila del usuario con el nuevo arreglo JSON y actualizar la fecha (opcional)
    cursor.execute("UPDATE user_prueba SET date = %s, entry = %s WHERE username = %s", (fecha, new_diary_json, entry.username))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Entrada agregada al diario", "registro": new_diary_entry}

# ----------------------------------------------
# Endpoint para obtener las entradas del Diario para un usuario
# ----------------------------------------------
@app.get("/diario")
async def obtener_diario(username: str = Query(...), password: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Verificar credenciales consultando la contraseña hasheada
    cursor.execute("SELECT password, entry FROM user_prueba WHERE username = %s LIMIT 1", (username,))
    result = cursor.fetchone()
    if not result or not pwd_context.verify(password, result["password"]):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    diary_json = result["entry"]
    cursor.close()
    conn.close()
    try:
        diary_entries = json.loads(diary_json) if diary_json and diary_json.strip() != "" else []
    except Exception:
        diary_entries = []
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas de diario")
    return {"diario": diary_entries}

# ----------------------------------------------
# Endpoint para obtener tendencias emocionales (Perfil)
# ----------------------------------------------
@app.get("/perfil")
async def obtener_perfil():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT entry FROM user_prueba WHERE entry <> ''")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="No se encontraron entradas de diario")
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
