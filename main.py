# main.py
from fastapi import FastAPI, Request
from emotion_analysis import analizar_emociones
from context_manager import recuperar_contexto
from chat_generator import generar_respuesta
from diary_manager import guardar_entrada, obtener_entradas
from personality_profiling import analizar_personalidad
from objective_generator import generar_objetivos
from utils import obtener_fecha_actual

app = FastAPI()

@app.post("/chat/")
async def chat_endpoint(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("message", "")
    user_id = data.get("user_id", "default")
    
    # 1. Analizar las emociones del mensaje del usuario.
    emociones = analizar_emociones(mensaje_usuario)
    
    # 2. Recuperar el contexto histórico del usuario (diario y conversaciones previas).
    contexto = recuperar_contexto(user_id)
    
    # 3. Generar la respuesta utilizando la API de MISTRAL AI con RAG.
    respuesta = generar_respuesta(mensaje_usuario, contexto)
    
    # 4. Guardar la entrada del diario emocional.
    entrada = {
        "fecha": obtener_fecha_actual(),
        "texto": mensaje_usuario,
        "emociones": emociones
    }
    guardar_entrada(user_id, entrada)
    
    # 5. Analizar el perfil de personalidad a partir de las entradas del diario.
    entradas = obtener_entradas(user_id)
    perfil = analizar_personalidad(entradas)
    
    # 6. Generar objetivos personalizados basados en el perfil y las emociones actuales.
    objetivos = generar_objetivos(perfil, emociones)
    
    return {
        "response": respuesta,
        "emotions": emociones,
        "profile": perfil,
        "objectives": objetivos
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
