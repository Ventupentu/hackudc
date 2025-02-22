# archivo: app.py
import streamlit as st
import requests

st.title("Chatbot Emocional Integrado")

# --- Sección 1: Chatbot Conversacional ---
st.header("Chatbot Conversacional")
user_input = st.text_input("Escribe tu mensaje:")
if st.button("Enviar mensaje"):
    response = requests.post("http://localhost:8000/analizar", json={"texto": user_input})
    if response.ok:
        data = response.json()
        st.write("Emociones detectadas:", data["emociones"])
        st.write("Respuesta del chatbot:", data["respuesta"])
    else:
        st.error("Error al conectar con el servidor de análisis.")

# --- Sección 2: Diario Emocional ---
st.header("Diario Emocional")
diario_texto = st.text_area("Escribe tu entrada del diario:")
if st.button("Agregar al diario"):
    response = requests.post("http://localhost:8000/diario", json={"texto": diario_texto})
    if response.ok:
        data = response.json()
        st.success("Entrada agregada al diario.")
        st.json(data["registro"])
    else:
        st.error("Error al agregar la entrada al diario.")

# --- Sección 3: Perfil de Personalidad ---
st.header("Perfil de Personalidad")
if st.button("Obtener perfil"):
    response = requests.get("http://localhost:8000/perfil")
    if response.ok:
        data = response.json()
        st.write("Perfil emocional promedio:")
        st.json(data["perfil_emocional"])
        st.write("Sugerencia:", data["sugerencia"])
    else:
        st.error("Error al obtener el perfil. Asegúrate de tener entradas en el diario.")

# --- Sección 4: Objetivos de Personalidad ---
st.header("Objetivos de Personalidad")
objetivo_input = st.text_input("Describe tu objetivo de personalidad:")
if st.button("Establecer objetivo"):
    response = requests.post("http://localhost:8000/objetivos", json={"descripcion": objetivo_input})
    if response.ok:
        data = response.json()
        st.write("Objetivo:", data["objetivo"])
        st.write("Recomendación:", data["recomendacion"])
    else:
        st.error("Error al establecer el objetivo.")
