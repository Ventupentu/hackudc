# archivo: app.py
import streamlit as st
import requests
import datetime

# Inyectar CSS personalizado para mejorar la interfaz general y la sección del Diario
st.markdown(
    """
    <style>
    /* Fondo general y tipografía */
    body {
        background-color: #F7F7F8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Barra lateral estilizada */
    .css-1d391kg { 
        background: linear-gradient(135deg, #2c3e50, #4ca1af);
        color: white;
    }
    /* Botones */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    /* Inputs y textareas */
    input, textarea {
        border: 2px solid #ccc;
        border-radius: 4px;
        padding: 8px;
        font-size: 16px;
    }
    /* Estilos para el Chat (no modificado) */
    .chat-container {
        margin: 20px 0;
    }
    .chat-message {
        display: flex;
        margin-bottom: 15px;
        width: 100%;
    }
    .chat-message.user {
        justify-content: flex-end;
    }
    .chat-message.assistant {
        justify-content: flex-start;
    }
    .chat-bubble {
        max-width: 70%;
        padding: 12px 18px;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.5;
    }
    .chat-message.user .chat-bubble {
        background-color: #DCF8C6;
        color: #000;
    }
    .chat-message.assistant .chat-bubble {
        background-color: #FFFFFF;
        color: #000;
    }
    /* Nuevos estilos para el Diario */
    .diary-container {
        margin-top: 20px;
    }
    .diary-header {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        margin-bottom: 15px;
    }
    .diary-entry {
        background-color: #FFFFFF;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .diary-date {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .diary-text {
        font-size: 16px;
        color: #555;
    }
    .diary-update-btn {
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Inicializar variables de sesión si aún no existen
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

def send_message():
    user_input = st.session_state.get("user_input", "")
    if user_input:
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})
        payload = {"messages": st.session_state.messages}
        response = requests.post("http://localhost:8000/chat", json=payload)
        if response.ok:
            data = response.json()
            assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
        else:
            assistant_response = "Error al procesar tu mensaje."
        # Agregar respuesta del chatbot
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Página Home: Se muestra si el usuario NO está autenticado
if not st.session_state.logged_in:
    st.title("Bienvenido a Tu Espacio Emocional")
    st.write("Regístrate o inicia sesión para acceder a nuestros servicios personalizados.")
    
    auth_option = st.radio("Selecciona una opción:", ["Iniciar Sesión", "Registrarse"])
    
    if auth_option == "Iniciar Sesión":
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Escribe tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Escribe tu contraseña")
            submitted = st.form_submit_button("Iniciar Sesión")
            if submitted:
                response = requests.post("http://localhost:8000/login", json={"username": username, "password": password})
                if response.ok:
                    st.success("¡Login exitoso!")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.password = password
                    st.experimental_rerun()
                else:
                    st.error("Credenciales inválidas o error en el login.")
                    
    elif auth_option == "Registrarse":
        with st.form("register_form"):
            username = st.text_input("Elige un usuario", placeholder="Usuario deseado")
            password = st.text_input("Elige una contraseña", type="password", placeholder="Contraseña deseada")
            submitted = st.form_submit_button("Registrarse")
            if submitted:
                response = requests.post("http://localhost:8000/register", json={"username": username, "password": password})
                if response.ok:
                    st.success("Usuario registrado exitosamente. Ahora inicia sesión.")
                else:
                    st.error("Error en el registro. Es posible que el usuario ya exista.")

# Página de Servicios: Se muestra cuando el usuario está autenticado
else:
    st.sidebar.title("Menú de Servicios")
    service_option = st.sidebar.radio("Selecciona un servicio:", ["Chatbot", "Diario", "Profiling", "Objetivo"])
    
    # Botón para cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.messages = []
        st.experimental_rerun()
    
    if service_option == "Chatbot":
        st.title("Chatbot Emocional - Guía Psicológica")
        
        # Contenedor para la conversación
        conversation_container = st.container()
        with conversation_container:
            st.markdown("### Conversación")
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                        <div class="chat-container chat-message user">
                            <div class="chat-bubble">
                                <strong>Tú:</strong> {msg['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="chat-container chat-message assistant">
                            <div class="chat-bubble">
                                <strong>Chatbot:</strong> {msg['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
        
        # Caja de texto fija en la parte inferior para continuar la conversación
        input_container = st.container()
        with input_container:
            with st.form(key="chat_form", clear_on_submit=True):
                st.text_input("Ingresa tu mensaje", key="user_input", placeholder="Escribe aquí tu mensaje...")
                submitted = st.form_submit_button("Enviar")
                if submitted:
                    send_message()
                    st.experimental_rerun()  # Actualiza la pantalla para mostrar el nuevo mensaje
    
    elif service_option == "Diario":
        st.title("Diario Emocional")
        st.write(f"Usuario: **{st.session_state.username}**")
        
        # Obtener las entradas del diario desde el backend
        params = {"username": st.session_state.username, "password": st.session_state.password}
        response = requests.get("http://localhost:8000/diario", params=params)
        diary_entries = []
        if response.ok:
            data = response.json()
            diary_entries = data.get("diario", [])
        else:
            st.error("Error al obtener las entradas del diario.")
        
        # Organizar las entradas por fecha (clave: "YYYY-MM-DD")
        diary_by_date = {}
        for entry in diary_entries:
            day = entry["timestamp"][:10]
            diary_by_date.setdefault(day, []).append(entry)
        
        st.subheader("Selecciona la fecha")
        selected_date = st.date_input("Fecha", value=datetime.date.today())
        selected_date_str = selected_date.strftime("%Y-%m-%d")
        
        # Mostrar el encabezado con la fecha seleccionada
        st.markdown(f"<div class='diary-header'>Entradas para el día {selected_date_str}:</div>", unsafe_allow_html=True)
        
        # Mostrar las entradas existentes con estilo de card
        entries = diary_by_date.get(selected_date_str, [])
        if entries:
            for entry in entries:
                st.markdown(
                    f"""
                    <div class="diary-entry">
                        <div class="diary-text">{entry['texto']}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
        else:
            st.info("No hay entradas para este día.")
        
        # Contenedor para la edición/creación de entrada
        st.markdown("<div class='diary-container'>", unsafe_allow_html=True)
        current_entry = ""
        if selected_date_str in diary_by_date:
            current_entry = diary_by_date[selected_date_str][0]["texto"]
        
        diary_text = st.text_area("Crear o editar la entrada", value=current_entry, height=150)
        
        if st.button("Actualizar entrada", key="update_diary", help="Guarda o actualiza tu entrada en el diario"):
            payload = {
                "username": st.session_state.username,
                "password": st.session_state.password,
                "texto": diary_text,
                "fecha": selected_date_str
            }
            response = requests.post("http://localhost:8000/diario", json=payload)
            if response.ok:
                st.success("¡Entrada actualizada!")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar la entrada.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif service_option == "Profiling":
        st.title("Perfil Emocional")
        st.info("Sección en construcción. ¡Próximamente!")
    
    elif service_option == "Objetivo":
        st.title("Objetivos Personales")
        st.info("Sección en construcción. ¡Próximamente!")
