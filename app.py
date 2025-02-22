# archivo: app.py
import streamlit as st
import requests

# Inicializar variables de sesión para el login si aún no existen
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""

# Si el usuario no está autenticado, mostramos únicamente las opciones de Autenticación
if not st.session_state.logged_in:
    st.sidebar.title("Autenticación")
    auth_option = st.sidebar.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])
    
    if auth_option == "Iniciar Sesión":
        st.title("Iniciar Sesión")
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar Sesión")
            if submitted:
                response = requests.post("http://localhost:8000/login", json={"username": username, "password": password})
                if response.ok:
                    st.success("Login exitoso")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.password = password
                else:
                    st.error("Credenciales inválidas o error en el login.")
                    
    elif auth_option == "Registrarse":
        st.title("Registrarse")
        with st.form("register_form"):
            username = st.text_input("Elige un usuario")
            password = st.text_input("Elige una contraseña", type="password")
            submitted = st.form_submit_button("Registrarse")
            if submitted:
                response = requests.post("http://localhost:8000/register", json={"username": username, "password": password})
                if response.ok:
                    st.success("Usuario registrado exitosamente. Ahora inicia sesión.")
                else:
                    st.error("Error en el registro. Puede que el usuario ya exista.")

# Una vez autenticado, se muestran las demás secciones
else:
    st.sidebar.title("Menú Principal")
    page = st.sidebar.radio("Selecciona una opción:", ["Chatbot", "Diario", "Profiling", "Objetivo"])
    
    if page == "Chatbot":
        st.title("Chatbot Emocional - Guía Psicológica")
        
        # Inicializar historial de mensajes
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        def send_message():
            user_input = st.session_state.user_input
            if user_input:
                # Agregar mensaje del usuario
                st.session_state.messages.append({"role": "user", "content": user_input})
                # Enviar todo el historial al endpoint /chat
                payload = {"messages": st.session_state.messages}
                response = requests.post("http://localhost:8000/chat", json=payload)
                if response.ok:
                    data = response.json()
                    assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
                else:
                    assistant_response = "Error al procesar tu mensaje."
                # Agregar respuesta del chatbot
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
        with st.form(key="chat_form", clear_on_submit=True):
            st.text_input("Ingresa tu mensaje", key="user_input")
            submitted = st.form_submit_button("Enviar")
            if submitted:
                send_message()
                
        # Mostrar historial de conversación
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**Tú:** {msg['content']}")
            else:
                st.markdown(f"**Chatbot:** {msg['content']}")
    
    elif page == "Diario":
        st.title("Diario Emocional")
        st.write(f"Usuario: {st.session_state.username}")
        diary_text = st.text_area("Escribe sobre tu día", height=150)
        if st.button("Guardar entrada"):
            payload = {
                "username": st.session_state.username,
                "password": st.session_state.password,
                "texto": diary_text
            }
            response = requests.post("http://localhost:8000/diario", json=payload)
            if response.ok:
                st.success("Entrada guardada!")
                st.json(response.json()["registro"])
            else:
                st.error("Error al guardar la entrada.")
        if st.button("Ver entradas"):
            params = {"username": st.session_state.username, "password": st.session_state.password}
            response = requests.get("http://localhost:8000/diario", params=params)
            if response.ok:
                data = response.json()
                st.write("Entradas del Diario:")
                st.json(data["diario"])
            else:
                st.error("Error al obtener las entradas.")
    
    elif page == "Profiling":
        st.write("Sección de Profiling - (Por implementar)")
    elif page == "Objetivo":
        st.write("Sección de Objetivos - (Por implementar)")
