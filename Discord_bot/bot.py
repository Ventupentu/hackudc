import discord
import requests
import json
from discord.ext import commands
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Obtener el token de Discord desde el .env
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Configuración del bot de Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# URL de la API de tu app (Streamlit)
API_URL = "http://localhost:8000/chat"

# Este comando hará que el bot responda con el mensaje del chatbot de la aplicación Streamlit
@bot.command(name='chat', help='Inicia una conversación con el chatbot')
async def chat(ctx, *, user_input: str):
    # Agregar el mensaje del usuario a la conversación
    payload = {
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    # Enviar la solicitud a la API de la aplicación Streamlit
    response = requests.post(API_URL, json=payload)

    if response.ok:
        data = response.json()
        assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
    else:
        assistant_response = "Hubo un error al procesar tu mensaje."

    # Responder al usuario en Discord con la respuesta del chatbot
    await ctx.send(assistant_response)

#Comando para guardar una entrada en el diario
@bot.command(name='diario', help='Escribe sobre tu día en el diario emocional')
async def diario(ctx, *, texto: str):
    # Enviar el texto del diario a la API
    response = requests.post(API_URL, json={"texto": texto})
    
    if response.ok:
        data = response.json()
        await ctx.send(f"Entrada guardada en tu diario:\n{data['registro']}")
    else:
        await ctx.send("Hubo un error al guardar la entrada. Intenta nuevamente.")

# Inicia el bot con el token de tu aplicación de Discord
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

# Ejecutar el bot con el token cargado desde el .env
bot.run(DISCORD_TOKEN)
