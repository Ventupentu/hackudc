import os
import nltk
import text2emotion as te
import re
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

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
    username: str

class UserAuth(BaseModel):
    username: str
    password: str

class DiaryEntry(BaseModel):
    username: str
    password: str
    entry: str
    fecha: str = None  # Opcional; si no se proporciona, se usa la fecha actual.
    editar: bool = False  # Por defecto, no es edición.

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

def list_of_dicts_to_entries_text(entries: list) -> str:
    """Convierte la lista de entradas del diario en un texto estructurado"""
    text_entries = ""
    for entry in entries:
        date = entry["date"]
        text = entry["entry"]
        emotions = entry["emotions"]
        text_entries += f"Fecha: {date}\n"
        text_entries += f"Entrada: {text}\n"
        text_entries += "Emociones:\n"
        for emotion, value in emotions.items():
            text_entries += f"- {emotion}: {value}\n"
        text_entries += "\n"  # Línea vacía entre entradas
    return text_entries

@app.post("/chat")
async def chat(conversation: Conversation):
    if not conversation.messages:
        raise HTTPException(status_code=400, detail="No hay mensajes en la conversación")
    username = conversation.username
    # Convertir mensajes a diccionarios
    conversation_list = [msg.dict() for msg in conversation.messages]

    # Analizar emociones del último mensaje del usuario
    last_message = conversation.messages[-1]
    emociones = {}
    if last_message.role == "user":
        emociones = te.get_emotion(last_message.content)
    emocion_dominante = max(emociones, key=emociones.get, default="neutral")

    # Crear un perfil emocional simple a partir del diario
    perfil = perfilar(username)
    print(f"Perfil emocional: {perfil}")

    # Crear un mensaje adicional para orientar a la IA
    mensaje_emocional = {
        "role": "system",
        "content": f"Eres un chatbot emocional orientado a apoyar al usuario. El usuario de nombre {username} parece estar sintiendo '{emocion_dominante}' en su último mensaje. Ajusta tu respuesta para ser apropiada a esta emoción. Ten en cuenta esta característica del usuario: '{perfil}'."
    } 

    # Insertar el mensaje de emoción al historial
    conversation_list.insert(0, mensaje_emocional)

    # Llamar a la API de Mistral con el historial actualizado
    respuesta = call_mistral_rag(conversation_list)
    return {"respuesta": respuesta, "emociones": emociones}

def perfilar(username: str) -> dict:
    """Obtiene el perfil emocional del usuario a partir de su historial de diario."""
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
        
    # Usamos claves con mayúscula inicial, ya que se almacenan así en la BD
    perfil = {"Happy": 0, "Sad": 0, "Angry": 0, "Surprise": 0, "Fear": 0}
    count = 0
    for entry_data in diary_entries:
        emociones = entry_data.get("emotions", {})  # Asumir que el campo se llama "emotions"
        for emo in perfil.keys():
            perfil[emo] += float(emociones.get(emo, 0))
        count += 1

    if count == 0:
        return {"perfil_emocional": {}, "sugerencia": "No hay datos suficientes"}

    # Normalizar valores
    for emo in perfil:
        perfil[emo] /= count

    emocion_dominante = max(perfil, key=perfil.get)
    sugerencia = {
        "Happy": "Tendencia a la felicidad",
        "Sad": "Tendencia a la melancolía",
        "Angry": "Tendencia a la irritabilidad",
        "Surprise": "Tendencia a la sorpresa",
        "Fear": "Tendencia al miedo"
    }.get(emocion_dominante, "Personalidad equilibrada")

    # Usar este formato legible con una lista de diccionarios
    entries_text = list_of_dicts_to_entries_text(diary_entries)

    # Ahora pasar esta cadena al LLM
    eneagrama = call_mistral_rag([{
        "role": "system",
        "content": f"Determina el tipo de eneagrama basado en las siguientes emociones y textos del diario:\n{entries_text}. Sé escueto y preciso y lo primero que debes de decir es el tipo de eneagrama"
    }])
    print("Eneagrama:", eneagrama)

    return {"perfil_emocional": perfil, "sugerencia": sugerencia, "eneagrama": eneagrama}

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
# Endpoint para agregar o actualizar la entrada del Diario
# ----------------------------------------------
@app.post("/diario")
async def agregar_diario(entry: DiaryEntry):
    success = db.verify_user(entry.username, entry.password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    target_date = entry.fecha if entry.fecha is not None else datetime.now().strftime("%Y-%m-%d")
    entry_for_date = db.get_diary_entry(entry.username, target_date)

    if entry.editar:
        if entry_for_date is None:
            raise HTTPException(status_code=400, detail="No existe una entrada previa para editar en esta fecha")
        new_text = entry.entry
        new_emotions = te.get_emotion(new_text)
        entry_for_date["entry"] = new_text
        entry_for_date["emotions"] = new_emotions
        entry_for_date["date"] = target_date
        updated_entry = entry_for_date
    else:
        if entry_for_date is not None:
            raise HTTPException(status_code=400, detail="Ya existe una entrada para esta fecha. Usa el modo edición.")
        new_emotions = te.get_emotion(entry.entry)
        updated_entry = {"entry": entry.entry, "emotions": new_emotions, "date": target_date}
    
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
# Función para calcular los rasgos Big Five a partir de los diarios
# ----------------------------------------------
def calculate_big_five(username: str) -> dict:
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    
    # Convertir las entradas del diario a un texto estructurado
    text_context = list_of_dicts_to_entries_text(diary_entries)
    
    # Definir el prompt para extraer los rasgos de personalidad (Big Five)
    prompt = f"""
    Analyze the following diary entries and evaluate the user's personality according to the Big Five traits.

    The traits are:
    - Openness
    - Conscientiousness
    - Extraversion
    - Agreeableness
    - Neuroticism

    For each trait, provide a value between 0 and 100 (where 100 means extremely high). 
    Only respond with valid JSON in the following format:

    {{
    "Openness": <number>,
    "Conscientiousness": <number>,
    "Extraversion": <number>,
    "Agreeableness": <number>,
    "Neuroticism": <number>
    }}

    Diary Entries:
    {text_context}
    """

    
    # Llamar al modelo para obtener la evaluación
    big_five_response = call_mistral_rag([{"role": "system", "content": prompt}])
    

    # Remove markdown code fences if present
    clean_response = re.sub(r"^```(?:json)?\s*", "", big_five_response)
    clean_response = re.sub(r"\s*```$", "", clean_response)

    print("Big Five response:", clean_response)
    
    try:
        big_five = json.loads(clean_response)
    except Exception as e:
        big_five = {
            "Openness": 0,
            "Conscientiousness": 0,
            "Extraversion": 0,
            "Agreeableness": 0,
            "Neuroticism": 0
        }
        print("me hago caca")
    
    return big_five

# ----------------------------------------------
# Endpoint de Perfilado (incluye perfil emocional y Big Five)
# ----------------------------------------------
@app.get("/perfilado")
async def perfilado(username: str = Query(...), password: str = Query(...)):
    success = db.verify_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    # Obtener perfil emocional
    perfil_emocional_data = perfilar(username)
    
    # Calcular rasgos Big Five
    big_five = calculate_big_five(username)
    
    # Combinar ambos perfiles en la respuesta
    perfil_completo = {
        "perfil_emocional": perfil_emocional_data.get("perfil_emocional", {}),
        "sugerencia": perfil_emocional_data.get("sugerencia", ""),
        "big_five": big_five
    }
    
    return {"perfil": perfil_completo}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
