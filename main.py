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

# Se agrega el campo opcional "fecha" (formato "YYYY-MM-DD") y "editar" para distinguir la acción.
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

@app.post("/chat")
async def chat(conversation: Conversation):
    if not conversation.messages:
        raise HTTPException(status_code=400, detail="No hay mensajes en la conversación")

    # Convertir mensajes a diccionarios
    conversation_list = [msg.dict() for msg in conversation.messages]

    # Analizar emociones del último mensaje del usuario
    last_message = conversation.messages[-1]
    emociones = {}
    if last_message.role == "user":
        emociones = te.get_emotion(last_message.content)

    # Determinar la emoción dominante
    emocion_dominante = max(emociones, key=emociones.get, default="neutral")

    # Crear un perfil emocional simple
    perfil = perfilar()
    print(f"Perfil emocional: {perfil}")

    # Crear un mensaje adicional para orientar a la IA
    mensaje_emocional = {
        "role": "system",
        "content": f"El usuario parece estar sintiendo '{emocion_dominante}'. Ajusta tu respuesta para ser apropiada a esta emoción. Ten en cuenta esta característica del usuario: '{perfil}'."
    }

    print(mensaje_emocional["content"])

    # Insertar el mensaje de emoción al historial
    conversation_list.insert(0, mensaje_emocional)

    # Llamar a la API de Mistral con el historial actualizado
    respuesta = call_mistral_rag(conversation_list)

    return {"respuesta": respuesta, "emociones": emociones}

def perfilar():
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
    if perfil["Happy"] > 0.5:
        perfil_personalidad = "Tendencia a la felicidad"
    if perfil["Surprise"] > 0.5:
        perfil_personalidad = "Tendencia a la sorpresa"
    if perfil["Fear"] > 0.5:
        perfil_personalidad = "Tendencia al miedo"
    return {"perfil_emocional": perfil, "sugerencia": perfil_personalidad}

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
    
    # Usar la fecha proporcionada o, si es None, la fecha actual
    target_date = entry.fecha if entry.fecha is not None else datetime.now().strftime("%Y-%m-%d")
    entry_for_date = db.get_diary_entry(entry.username, target_date)

    if entry.editar:
        if entry_for_date is None:
            raise HTTPException(status_code=400, detail="No existe una entrada previa para editar en esta fecha")
        # Modo edición: sobrescribir la entrada existente
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
# Endpoint para Profiling basado en el historial del Diario
# ----------------------------------------------
import plotly.graph_objects as go

@app.get("/profiling")
async def obtener_profiling(username: str = Query(...), password: str = Query(...)):
    diary_entries = db.get_diary_entries(username)
    if not diary_entries:
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    
    now = datetime.now()
    weighted_emotions = {"Happy": 0.0, "Sad": 0.0, "Angry": 0.0, "Surprise": 0.0, "Fear": 0.0}
    total_weight = 0.0
    
    for entry in diary_entries:
        try:
            ts = datetime.fromisoformat(entry["date"])
        except Exception:
            continue
        days_diff = (now - ts).days
        weight = 1 / (1 + days_diff/7)
        for emo in weighted_emotions:
            weighted_emotions[emo] += entry.get("emotions", {}).get(emo, 0) * weight
        total_weight += weight
    
    if total_weight == 0:
        raise HTTPException(status_code=404, detail="No se pudieron calcular los perfiles")
    
    average_emotions = {k: v / total_weight for k, v in weighted_emotions.items()}

    emotion_weights = {
        "Sad": 0.3,
        "Fear": 0.3,
        "Angry": 0.4,
        "Happy": 0.3,
        "Surprise": 0.4
    }
    
    neuroticism = (average_emotions["Sad"] * emotion_weights["Sad"] + 
                     average_emotions["Fear"] * emotion_weights["Fear"] + 
                     average_emotions["Angry"] * emotion_weights["Angry"]) / (emotion_weights["Sad"] + emotion_weights["Fear"] + emotion_weights["Angry"])

    extraversion = (average_emotions["Happy"] * emotion_weights["Happy"] + 
                    average_emotions["Surprise"] * emotion_weights["Surprise"]) / (emotion_weights["Happy"] + emotion_weights["Surprise"])

    agreeableness = (average_emotions["Happy"] * 0.5 + (1 - average_emotions["Angry"]) * 0.5)

    openness = min(1.0, (average_emotions["Surprise"] + average_emotions["Happy"]) / 2)
    conscientiousness = max(0.2, 1 - (average_emotions["Angry"] + average_emotions["Fear"]) / 2)

    big_five = {
        "Neuroticism": round(neuroticism, 2),
        "Extraversion": round(extraversion, 2),
        "Agreeableness": round(agreeableness, 2),
        "Openness": round(openness, 2),
        "Conscientiousness": round(conscientiousness, 2),
    }
    
    def list_of_dicts_to_entries_text(entries: list) -> str:
        text_entries = ""
        for entry in entries:
            date = entry["date"]
            text = entry["entry"]
            emotions = entry.get("emotions", {})
            
            text_entries += f"Fecha: {date}\n"
            text_entries += f"Entrada: {text}\n"
            text_entries += "Emociones:\n"
            for emotion, value in emotions.items():
                text_entries += f"- {emotion}: {value}\n"
            text_entries += "\n"
        return text_entries

    entries_text = list_of_dicts_to_entries_text(diary_entries)

    eneagrama = call_mistral_rag([{
        "role": "system",
        "content": f"Determina el tipo de eneagrama basado en las siguientes emociones y textos del diario:\n{entries_text}"
    }])

    dimensions = list(big_five.keys())
    scores = list(big_five.values())
    dimensions.append(dimensions[0])
    scores.append(scores[0])
    
    radar_fig = go.Figure(
        data=[
            go.Scatterpolar(r=scores, theta=dimensions, fill='toself', name='Big Five')
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            showlegend=False,
            title="Perfil Big Five"
        )
    )
    
    bar_fig = go.Figure(
        data=[
            go.Bar(x=list(average_emotions.keys()), y=[round(v, 2) for v in average_emotions.values()])
        ],
        layout=go.Layout(
            title="Emociones Promedio",
            xaxis_title="Emoción",
            yaxis_title="Valor",
            yaxis=dict(range=[0,1])
        )
    )
    
    return {
        "big_five": big_five,
        "eneagrama": eneagrama,
        "average_emotions": average_emotions,
        "radar_chart": radar_fig.to_json(),
        "bar_chart": bar_fig.to_json()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
