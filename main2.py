# archivo: main.py
import os
import nltk
import text2emotion as te
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

load_dotenv()  # Carga las variables de entorno, incluyendo MISTRAL_API_KEY

app = FastAPI()

# Descarga recursos NLTK (si aún no se han descargado)
nltk.download('punkt_tab')
nltk.download('punkt')

# ===============================================
# Configuración para el Diario
# ===============================================
DIARY_FILE = "diario.json"

# ===============================================
# Modelos de datos para el Chat y el Diario
# ===============================================
class Message(BaseModel):
    role: str  # "user", "assistant" o "system"
    content: str

class Conversation(BaseModel):
    messages: list[Message]

class DiarioEntrada(BaseModel):
    texto: str
    fecha: str = None  # Se asigna la fecha actual si no se provee

# ===============================================
# Función para llamar a Mistralai (Chat) – según la doc oficial
# ===============================================
def call_mistral_rag(conversation_messages: list[dict]) -> str:
    from mistralai import Mistral  # Según la documentación oficial
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    
    chat_response = client.chat.complete(
        model=model,
        messages=conversation_messages
    )
    return chat_response.choices[0].message.content

# ===============================================
# Endpoint de Chat (conversación completa)
# ===============================================
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
    perfil = obtener_perfil()
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


# ===============================================
# Endpoint para agregar una entrada al Diario Emocional
# ===============================================
@app.post("/diario")
async def agregar_diario(entrada: DiarioEntrada):
    if not entrada.fecha:
        entrada.fecha = datetime.now().isoformat()
    emociones = te.get_emotion(entrada.texto)
    registro = {
        "fecha": entrada.fecha,
        "texto": entrada.texto,
        "emociones": emociones
    }
    # Cargar entradas existentes o inicializar la lista
    if os.path.exists(DIARY_FILE):
        with open(DIARY_FILE, "r", encoding="utf-8") as f:
            diario = json.load(f)
    else:
        diario = []
    diario.append(registro)
    # Guardar el diario actualizado
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(diario, f, ensure_ascii=False, indent=4)
    return {"mensaje": "Entrada agregada al diario", "registro": registro}

# ===============================================
# Endpoint para obtener tendencias emocionales (Perfil)
# ===============================================
@app.get("/perfil")
async def obtener_perfil():
    if not os.path.exists(DIARY_FILE):
        raise HTTPException(status_code=404, detail="No hay entradas de diario")
    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        diario = json.load(f)
    # Inicializar acumuladores para cada emoción
    perfil = {"Happy": 0, "Sad": 0, "Angry": 0, "Surprise": 0, "Fear": 0}
    count = len(diario)
    if count == 0:
        raise HTTPException(status_code=404, detail="No hay entradas de diario")
    for entrada in diario:
        for emo in perfil.keys():
            perfil[emo] += entrada["emociones"].get(emo, 0)
    # Calcular promedio
    for emo in perfil:
        perfil[emo] = perfil[emo] / count
    # Sugerencia simple basada en promedios (puedes mejorarla)
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
    return  perfil_personalidad

# ===============================================
# Punto de entrada
# ===============================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
