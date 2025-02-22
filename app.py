# archivo: app.py
import streamlit as st
import requests

# Menú lateral para seleccionar la sección
st.sidebar.title("Menú Principal")
page = st.sidebar.radio("Selecciona una opción:", ["Chatbot", "Diario", "Profiling", "Objetivo"])

if page == "Chatbot":
    st.title("Chatbot Emocional - Guía Psicológica")
    
    # Inicializar el historial de mensajes si aún no existe
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def send_message():
        user_input = st.session_state.user_input
        if user_input:
            # Añadir mensaje del usuario al historial
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Construir el payload con la conversación completa
            payload = {"messages": st.session_state.messages}
            # Llamar al endpoint /chat
            response = requests.post("http://localhost:8000/chat", json=payload)
            if response.ok:
                data = response.json()
                assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
            else:
                assistant_response = "Lo siento, hubo un error al procesar tu mensaje."
            # Agregar respuesta del chatbot al historial
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            # El campo se limpia automáticamente con clear_on_submit

    # Formulario para enviar mensajes
    with st.form(key="chat_form", clear_on_submit=True):
        st.text_input("Ingresa tu estado emocional o mensaje", key="user_input")
        submitted = st.form_submit_button("Enviar")
        if submitted:
            send_message()

    # Mostrar el historial de conversación
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**Tú:** {msg['content']}")
        else:
            st.markdown(f"**Chatbot:** {msg['content']}")

elif page == "Diario":
    st.write("Sección de Diario - (Por implementar)")
elif page == "Profiling":
    st.write("Sección de Profiling - (Por implementar)")
elif page == "Objetivo":
    st.write("Sección de Objetivos - (Por implementar)")
