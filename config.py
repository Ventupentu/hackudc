import os
from dotenv import load_dotenv

load_dotenv()

# Clave y URL de la API de MISTRAL AI (reemplaza con tus datos reales)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/generate"
MAX_TOKENS = 150

# Configuración de la base de datos (usamos un archivo JSON para el prototipo)
DATABASE_PATH = "database.json"
