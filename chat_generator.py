# chat_generator.py
import requests
import json
from config import MISTRAL_API_KEY, MISTRAL_API_URL, MAX_TOKENS

def generar_respuesta(mensaje: str, contexto: str) -> str:
    """
    Combina el mensaje y el contexto para generar una respuesta utilizando la API de MISTRAL AI.
    """
    prompt_completo = f"{contexto}\nUsuario: {mensaje}\nChatbot:"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt_completo,
        "max_tokens": MAX_TOKENS
    }
    
    response = requests.post(MISTRAL_API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        resultado = response.json()
        return resultado.get("generated_text", "Lo siento, ocurrió un error al generar la respuesta.")
    else:
        return "Lo siento, no puedo procesar tu solicitud en este momento."
