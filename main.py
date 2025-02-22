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

emotionai = FastAPI()

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

@emotionai.get("/start_chat")
async def start_chat(username : str = Query(...)):
    #Vamos a intentar recuperar la conversación de la base de datos
    #Tanto para que la vea el usuario como para que la IA pueda tener contexto
    #Un máximo de diez mensajes, para no saturar la API de Mistral
    # 10 del usuario, 10 de la IA
    conversation_list = db.get_chat_history(username, 10)
    return {"conversation": conversation_list}

@emotionai.post("/chat")
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

    # Crear un mensaje adicional para orientar a la IA
    mensaje_emocional = {
        "role": "system",
        "content": f"Eres un chatbot emocional orientado a apoyar al usuario. El usuario de nombre {username} parece estar sintiendo '{emocion_dominante}' en su último mensaje. Ajusta tu respuesta para ser apropiada a esta emoción. Ten en cuenta esta característica del usuario que ha mostrado a lo largo del tiempo: '{perfil}'."
    } 

    # Insertar el mensaje de emoción al historial
    conversation_list.insert(0, mensaje_emocional)

    # Llamar a la API de Mistral con el historial actualizado
    respuesta = call_mistral_rag(conversation_list)

    # Guardamos el último trozo de conversación en la base de datos
    piece_of_conversation = {
        "date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "human_message" : last_message.content,
        "bot_message" : respuesta,
        "emotions" : emociones,
    }

    db.insert_chat_history(username, piece_of_conversation)
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
        return {"perfil_emocional": {}, "tendencia": "No hay datos suficientes"}

    # Normalizar valores
    for emo in perfil:
        perfil[emo] /= count

    emocion_dominante = max(perfil, key=perfil.get)
    tendencia = {
        "Happy": "Tienes tendencia a la felicidad",
        "Sad": "Tienes tendencia a la melancolía",
        "Angry": "Tienes tendencia a la irritabilidad",
        "Surprise": "Tienes tendencia a la sorpresa",
        "Fear": "Tienes tendencia al miedo"
    }.get(emocion_dominante, "Personalidad equilibrada")

    # Usar este formato legible con una lista de diccionarios
    entries_text = list_of_dicts_to_entries_text(diary_entries)

    # Ahora pasar esta cadena al LLM
    eneagrama = call_mistral_rag([{
        "role": "system",
        "content": f"""
    Analiza las siguientes emociones y textos del diario y determina el tipo de eneagrama del usuario. Debes responder de forma elaborada, precisa y siempre siguiendo exactamente el siguiente formato JSON, sin ningún comentario adicional:
    No seas tan formal, sé más cercano y amigable con el usuario. Puedes hablar de tú a tú.
    Tipos de eneagrama:
    - 1: Perfeccionista
    - 2: Ayudador
    - 3: Triunfador
    - 4: Individualista
    - 5: Investigador
    - 6: Leal
    - 7: Entusiasta
    - 8: Protector
    - 9: Pacificador
    {{
    "eneagrama_type": "Eneatipo <numero> (<nombre>)",
    "description": "<Descripción breve del tipo>",
    "recommendation": "<Recomendación concreta basada en el análisis>"
    }}

    Utiliza los siguientes datos:
    {entries_text}
    """
    }])

    clean_response = re.sub(r"^```(?:json)?\s*", "", eneagrama).strip()
    clean_response = re.sub(r"\s*```$", "", clean_response)

    try:
        eneagrama_dict = json.loads(clean_response)
    except Exception as e:
        print("Error parsing JSON:", e)
        eneagrama_dict = {}

    return {"perfil_emocional": perfil, "tendencia": tendencia, "eneagrama": eneagrama_dict}

# ----------------------------------------------
# Endpoint de Registro
# ----------------------------------------------
@emotionai.post("/register")
async def register(user: UserAuth):
    user_exit = db.check_user(user.username)
    if user_exit:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    db.register_user(user.username, user.password)
    return {"mensaje": "Usuario registrado exitosamente"}

# ----------------------------------------------
# Endpoint de Login (verifica contraseña hasheada)
# ----------------------------------------------
@emotionai.post("/login")
async def login(user: UserAuth):
    success = db.verify_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {"mensaje": "Login exitoso"}

# ----------------------------------------------
# Endpoint para agregar o actualizar la entrada del Diario
# ----------------------------------------------
@emotionai.post("/diario")
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
@emotionai.get("/diario")
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

    
    return big_five

# ----------------------------------------------
# Endpoint de Perfilado (incluye perfil emocional y Big Five)
# ----------------------------------------------
@emotionai.get("/perfilado")
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
        "tendencia": perfil_emocional_data.get("tendencia", ""),
        "big_five": big_five,
        "eneagrama": perfil_emocional_data.get("eneagrama", "")
    }
    
    return {"perfil": perfil_completo}


@emotionai.get("/Objetivo")
async def objetivo(username: str = Query(...), password: str = Query(...)):
    # Verificar credenciales del usuario
    success = db.verify_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    
    # Obtener entradas del diario del usuario
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    
    # Convertir las entradas en un texto estructurado
    entries_text = list_of_dicts_to_entries_text(diary_entries)
    
    # Definir el prompt para generar objetivos personalizados
    prompt = f"""
    Analiza los siguientes textos del diario y las emociones detectadas en ellos. A partir de ello, propone una lista de objetivos personalizados que el usuario podría plantearse para mejorar su estado emocional.
    
    Ejemplos:
    - "Soy una persona inestable emocionalmente y quiero reducir mi neuroticismo."
    - "Soy una persona introvertida y quiero aumentar mi extraversión."
    
    Debes responder siempre en formato JSON EXACTAMENTE como se indica, sin ningún comentario adicional:
    
    {{
      "objetivos": [
          "<Objetivo 1>",
          "<Objetivo 2>",
          "...",
          "<Objetivo 5>"
      ]
    }}
    
    Utiliza la siguiente información:
    {entries_text}
    """
    
    # Llamar al modelo para obtener los objetivos
    respuesta_objetivo = call_mistral_rag([{"role": "system", "content": prompt}])
    
    # Eliminar posibles delimitadores markdown (por ejemplo, ```json ... ```)
    clean_response = re.sub(r"^```(?:json)?\s*", "", respuesta_objetivo).strip()
    clean_response = re.sub(r"\s*```$", "", clean_response)
    
    try:
        objetivos = json.loads(clean_response)
    except Exception as e:
        print("Error parsing JSON in /Objetivo:", e)
        objetivos = {"objetivos": []}
    
    return {"objetivo": objetivos}


if __name__ == "__main__":
    uvicorn.run(emotionai, host="0.0.0.0", port=8000)