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
if "messages" not in st.session_state:
    st.session_state.messages = []

# Si el usuario NO está autenticado, mostramos la página "Home" (registro y login)
if not st.session_state.logged_in:
    st.title("Home")
    st.write("Por favor, regístrate o inicia sesión para acceder a los servicios.")
    
    auth_option = st.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])
    
    if auth_option == "Iniciar Sesión":
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar Sesión")
            if submitted:
                response = requests.post(
                    "http://localhost:8000/login", 
                    json={"username": username, "password": password}
                )
                if response.ok:
                    st.success("Login exitoso")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.password = password
                    st.rerun()
                    

                else:
                    st.error("Credenciales inválidas o error en el login.")
                    
    elif auth_option == "Registrarse":
        with st.form("register_form"):
            username = st.text_input("Elige un usuario")
            password = st.text_input("Elige una contraseña", type="password")
            submitted = st.form_submit_button("Registrarse")
            if submitted:
                response = requests.post(
                    "http://localhost:8000/register", 
                    json={"username": username, "password": password}
                )
                if response.ok:
                    st.success("Usuario registrado exitosamente. Ahora inicia sesión.")
                else:
                    st.error("Error en el registro. Puede que el usuario ya exista.")
                    
# Si el usuario está autenticado, se muestran los servicios en un menú lateral
else:
    st.sidebar.title("Servicios")
    service_option = st.sidebar.radio("Selecciona un servicio:", ["Chatbot", "Diario", "Profiling", "Objetivo"])
    
    # Botón para cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.messages = []
        st.rerun()

    
    if service_option == "Chatbot":
        st.title("Chatbot Emocional - Guía Psicológica")
        
        def send_message():
            user_input = st.session_state.user_input
            if user_input:
                # Agregar mensaje del usuario al historial
                st.session_state.messages.append({"role": "user", "content": user_input})
                # Enviar el historial completo al endpoint /chat
                payload = {"messages": st.session_state.messages}
                response = requests.post("http://localhost:8000/chat", json=payload)
                if response.ok:
                    data = response.json()
                    assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
                else:
                    assistant_response = "Error al procesar tu mensaje."
                # Agregar respuesta del chatbot al historial
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        with st.form(key="chat_form", clear_on_submit=True):
            st.text_input("Ingresa tu mensaje", key="user_input")
            submitted = st.form_submit_button("Enviar")
            if submitted:
                send_message()
                
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**Tú:** {msg['content']}")
            else:
                st.markdown(f"**Chatbot:** {msg['content']}")
    
    elif service_option == "Diario":
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
    
    elif service_option == "Profiling":
        st.write("Sección de Profiling - (Por implementar)")
    
    elif service_option == "Objetivo":
        st.write("Sección de Objetivos - (Por implementar)")
