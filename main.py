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
    entry: str
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
        new_text = f"{entry_for_date['text']}\n{entry.entry}"
        new_emotions = te.get_emotion(new_text)
        entry_for_date["entry"] = new_text
        entry_for_date["emotions"] = new_emotions
        entry_for_date["date"] = target_date
        updated_entry = entry_for_date
    else:
        fecha = target_date
        new_emotions = te.get_emotion(entry.entry)
        updated_entry = {"entry": entry.entry, "emotions": new_emotions, "date": fecha}
    
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
    if perfil["Happy"] > 0.5:
        perfil_personalidad = "Tendencia a la felicidad"
    if perfil["Surprise"] > 0.5:
        perfil_personalidad = "Tendencia a la sorpresa"
    if perfil["Fear"] > 0.5:
        perfil_personalidad = "Tendencia al miedo"
    return {"perfil_emocional": perfil, "sugerencia": perfil_personalidad}

# ----------------------------------------------
# Endpoint para Profiling basado en el historial del Diario
# Modelos: Big Five y Eneagrama (usando mayor peso para entradas recientes)
# ----------------------------------------------
import plotly.graph_objects as go

@app.get("/profiling")
async def obtener_profiling(username: str = Query(...), password: str = Query(...)):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT entry, password FROM user_prueba WHERE username = %s LIMIT 1", (username,))
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
        raise HTTPException(status_code=404, detail="No se encontraron entradas en el diario")
    
    from datetime import datetime
    now = datetime.now()
    weighted_emotions = {"Happy": 0.0, "Sad": 0.0, "Angry": 0.0, "Surprise": 0.0, "Fear": 0.0}
    total_weight = 0.0
    
    for entry in diary_entries:
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
        except Exception:
            continue
        days_diff = (now - ts).days
        weight = 1 / (1 + days_diff/7)
        for emo in weighted_emotions:
            weighted_emotions[emo] += entry.get("emociones", {}).get(emo, 0) * weight
        total_weight += weight
    
    if total_weight == 0:
        raise HTTPException(status_code=404, detail="No se pudieron calcular los perfiles")
    
    average_emotions = {k: v / total_weight for k, v in weighted_emotions.items()}
    
    neuroticism = (average_emotions["Sad"] + average_emotions["Fear"] + average_emotions["Angry"]) / 3
    extraversion = (average_emotions["Happy"] + average_emotions["Surprise"]) / 2
    agreeableness = average_emotions["Happy"]
    big_five = {
        "Neuroticism": round(neuroticism, 2),
        "Extraversion": round(extraversion, 2),
        "Agreeableness": round(agreeableness, 2),
        "Openness": 0.5,
        "Conscientiousness": 0.5,
    }
    
    if average_emotions["Angry"] > 0.6:
        eneagrama = "Tipo 8: El Desafiador"
    elif average_emotions["Sad"] > 0.6:
        eneagrama = "Tipo 4: El Individualista"
    elif average_emotions["Happy"] > 0.6:
        eneagrama = "Tipo 7: El Entusiasta"
    elif average_emotions["Fear"] > 0.6:
        eneagrama = "Tipo 6: El Leal"
    elif average_emotions["Surprise"] > 0.6:
        eneagrama = "Tipo 3: El Triunfador"
    elif average_emotions["Angry"] < 0.2 and average_emotions["Sad"] < 0.2 and average_emotions["Fear"] < 0.2:
        eneagrama = "Tipo 9: El Pacificador"
    elif average_emotions["Happy"] > 0.5 and average_emotions["Sad"] < 0.4 and average_emotions["Fear"] < 0.4:
        eneagrama = "Tipo 2: El Ayudador"
    elif average_emotions["Sad"] > 0.5 and average_emotions["Happy"] < 0.4:
        eneagrama = "Tipo 4: El Individualista"
    elif average_emotions["Surprise"] > 0.4 and average_emotions["Angry"] < 0.3:
        eneagrama = "Tipo 3: El Triunfador"
    else:
        eneagrama = "Tipo 5: El Investigador"
        
    # --- Generación del gráfico Radar para Big Five ---
    dimensions = list(big_five.keys())
    scores = list(big_five.values())
    # Cerrar el polígono
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
    
    # --- Generación del gráfico de Barras para emociones promedio ---
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
    
    # Convertir las figuras a JSON para enviarlas al cliente
    return {
        "big_five": big_five,
        "eneagrama": eneagrama,
        "average_emotions": average_emotions,
        "radar_chart": radar_fig.to_json(),
        "bar_chart": bar_fig.to_json()
    }

# ----------------------------------------------
# Punto de entrada de la aplicación
# ----------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
