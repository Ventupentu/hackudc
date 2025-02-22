# archivo: main.py
import os
import nltk
import text2emotion as te

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

load_dotenv()  # Carga las variables de entorno, incluyendo MISTRAL_API_KEY

app = FastAPI()

# Descarga los recursos necesarios de NLTK (si aún no se han descargado)
nltk.download('punkt_tab')
nltk.download('punkt')

# ===============================================
# Modelos de datos para la conversación
# ===============================================
class Message(BaseModel):
    role: str  # "user", "assistant" o "system" (si se desea incluir)
    content: str

class Conversation(BaseModel):
    messages: list[Message]

# ===============================================
# Función para llamar a Mistralai utilizando la API oficial
# ===============================================
def call_mistral_rag(conversation_messages: list[dict]) -> str:
    """
    Utiliza la librería 'mistralai' para obtener una respuesta a partir del historial de mensajes.
    Se espera que conversation_messages sea una lista de diccionarios con keys 'role' y 'content'.
    """
    from mistralai import Mistral  # Importa la clase oficial según la documentación
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    
    chat_response = client.chat.complete(
        model=model,
        messages=conversation_messages
    )
    
    # Extrae y retorna el contenido de la respuesta
    return chat_response.choices[0].message.content

# ===============================================
# Endpoint principal de chat
# ===============================================
@app.post("/chat")
async def chat(conversation: Conversation):
    if not conversation.messages:
        raise HTTPException(status_code=400, detail="No hay mensajes en la conversación")
    
    # Opcional: analiza las emociones del último mensaje del usuario
    last_message = conversation.messages[-1]
    emociones = {}
    if last_message.role == "user":
        emociones = te.get_emotion(last_message.content)
        # Si deseas inyectar información emocional en la conversación, podrías agregar un mensaje "system"
        # conversation.messages.append(Message(role="system", content=f"Emotions: {emociones}"))
    
    # Convierte la lista de mensajes a una lista de diccionarios
    conversation_list = [msg.dict() for msg in conversation.messages]
    
    # Llama a Mistralai pasando la conversación completa
    respuesta = call_mistral_rag(conversation_list)
    
    return {"respuesta": respuesta, "emociones": emociones}

# ===============================================
# Punto de entrada de la aplicación
# ===============================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
