import discord
import os
from denode import DeNode
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DENODE_API_KEY = os.getenv("DENODE_API_KEY")

# Configurar cliente de Discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# Configurar DeNode SDK
denode_ai = DeNode(api_key=DENODE_API_KEY)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return  # Evitar responder a otros bots

    try:
        response = denode_ai.chat(input=message.content)
        await message.reply(response)
    except Exception as e:
        print(f"⚠️ Error con DeNode IA: {e}")
        await message.reply("⚠️ Hubo un error con la IA.")

client.run(TOKEN)
