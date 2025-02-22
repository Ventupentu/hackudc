# archivo: app.py
import streamlit as st
import requests
import datetime

# Inyectar CSS personalizado para imitar la interfaz de ChatGPT y mejorar la sección del Diario
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
    /* Estilos para el Chat (similar a ChatGPT) */
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
    /* Estilos para el Diario */
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

URL="https://hackudc.onrender.com"

# Inicializar variables de sesión
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
        st.session_state.messages.append({"role": "user", "content": user_input})
        payload = {"messages": st.session_state.messages}
        response = requests.post(f"{URL}/chat", json=payload)
        if response.ok:
            data = response.json()
            assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
        else:
            assistant_response = "Error al procesar tu mensaje."
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Página Home: si el usuario NO está autenticado
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
                response = requests.post(f"{URL}/login", json={"username": username, "password": password})
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
                response = requests.post(f"{URL}/register", json={"username": username, "password": password})
                if response.ok:
                    st.success("Usuario registrado exitosamente. Ahora inicia sesión.")
                else:
                    st.error("Error en el registro. Es posible que el usuario ya exista.")

# Página de Servicios: si el usuario está autenticado
else:
    st.sidebar.title("Menú de Servicios")
    service_option = st.sidebar.radio("Selecciona un servicio:", ["Chatbot", "Diario", "Profiling", "Objetivo"])
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.messages = []
        st.experimental_rerun()
    
    if service_option == "Chatbot":
        st.title("Chatbot Emocional - Guía Psicológica")
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
        input_container = st.container()
        with input_container:
            with st.form(key="chat_form", clear_on_submit=True):
                st.text_input("Ingresa tu mensaje", key="user_input", placeholder="Escribe aquí tu mensaje...")
                submitted = st.form_submit_button("Enviar")
                if submitted:
                    send_message()
                    st.experimental_rerun()
    
    elif service_option == "Diario":
        st.title("Diario Emocional")
        st.write(f"Usuario: **{st.session_state.username}**")
        params = {"username": st.session_state.username, "password": st.session_state.password}
        response = requests.get(f"{URL}/diario", params=params)
        diary_entries = []
        if response.ok:
            data = response.json()
            diary_entries = data.get("diario", [])
        else:
            st.error("Error al obtener las entradas del diario.")
        
        diary_by_date = {}
        for entry in diary_entries:
            day = entry["timestamp"][:10]
            diary_by_date.setdefault(day, []).append(entry)
        
        st.subheader("Selecciona la fecha")
        selected_date = st.date_input("Fecha", value=datetime.date.today())
        selected_date_str = selected_date.strftime("%Y-%m-%d")
        
        st.markdown(f"<div class='diary-header'>Entradas para el día {selected_date_str}:</div>", unsafe_allow_html=True)
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
            response = requests.post(f"{URL}/diario", json=payload)
            if response.ok:
                st.success("¡Entrada actualizada!")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar la entrada.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif service_option == "Profiling":
        st.title("Perfil de Personalidad")
        # Solicitar datos del endpoint de profiling
        params = {"username": st.session_state.username, "password": st.session_state.password}
        response = requests.get(f"{URL}/profiling", params=params)
        if response.ok:
            data = response.json()
            big_five = data.get("big_five", {})
            eneagrama = data.get("eneagrama", "No disponible")
            average_emotions = data.get("average_emotions", {})
            
            st.subheader("Modelo Big Five")
            for dimension, score in big_five.items():
                st.write(f"**{dimension}:** {score}")
            
            # Gráfico de Radar para Big Five usando Plotly
            import plotly.graph_objects as go
            dimensions = list(big_five.keys())
            scores = list(big_five.values())
            dimensions += [dimensions[0]]
            scores += [scores[0]]
            radar_fig = go.Figure(
                data=[
                    go.Scatterpolar(r=scores, theta=dimensions, fill='toself', name='Big Five')
                ],
                layout=go.Layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 1])
                    ),
                    showlegend=False,
                    title="Perfil Big Five"
                )
            )
            st.plotly_chart(radar_fig)
            
            st.subheader("Clasificación Eneagrama")
            st.write(eneagrama)
            
            st.subheader("Emociones Promedio (ponderadas por recencia)")
            for emo, value in average_emotions.items():
                st.write(f"**{emo}:** {round(value, 2)}")
            
            # Gráfico de Barras para las emociones promedio
            emotions_fig = go.Figure(
                data=[
                    go.Bar(x=list(average_emotions.keys()), y=[round(v, 2) for v in average_emotions.values()])
                ],
                layout=go.Layout(
                    title="Emociones Promedio",
                    xaxis_title="Emoción",
                    yaxis_title="Valor",
                    yaxis=dict(range=[0,1])
                )
            )
            st.plotly_chart(emotions_fig)
        else:
            st.error("Error al obtener el perfil. Asegúrate de tener entradas en el diario.")
    
    elif service_option == "Objetivo":
        st.title("Objetivos Personales")
        st.info("Sección en construcción. ¡Próximamente!")
