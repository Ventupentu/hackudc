import streamlit as st
import requests
import datetime

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
    /* Inputs y textareas */
    input, textarea {
        border: 2px solid #ccc;
        border-radius: 4px;
        padding: 8px;
        font-size: 16px;
    }
    /* Estilos para el Chat */
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





# Inicializar variables de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "diary_text" not in st.session_state:
    st.session_state.diary_text = ""
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

URL = "http://localhost:8000"

def send_message():
    user_input = st.session_state.get("user_input", "")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        if len(st.session_state.messages) > 20:
            # Para mantener el limite de 20 mensajes en el chat (10 user, 10 assistant)
            #Eliminamos el primero de la IA y el primero del usuario
            st.session_state.messages.pop(0)
            st.session_state.messages.pop(0)
        payload = {"messages": st.session_state.messages, "username": st.session_state.username}
        response = requests.post(f"{URL}/chat", json=payload)
        if response.ok:
            data = response.json()
            assistant_response = data.get("respuesta", "No se obtuvo respuesta.")
        else:
            assistant_response = "Error al procesar tu mensaje."
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Página Home (sin autenticación)
if not st.session_state.logged_in:
    st.title("Bienvenido a EmotionAI, tu asistente emocional")
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
                    st.session_state.started_chat = False
                    st.rerun()
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
# Página de Servicios (usuario autenticado)
else:
    st.sidebar.title("Menú de Servicios")
    service_option = st.sidebar.radio("Selecciona un servicio:", ["Chatbot", "Diario", "Profiling", "Objetivo"])
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""
        st.session_state.messages = []
        st.session_state.edit_mode = False
        st.session_state.started_chat = False
        st.rerun()
    
    if service_option == "Chatbot":
        st.title("Chatbot Emocional - Guía Psicológica")
        if not st.session_state.started_chat:
            response = requests.get(f"{URL}/start_chat", params={"username": st.session_state.username})
            if response.status_code == 200:
                data = response.json()
                conversation = response.json().get("conversation", [])
                if len(conversation) > 0:
                    st.session_state.messages = conversation
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"Hola, soy tu asistente emocional. ¿En qué puedo ayudarte hoy, {st.session_state.username}?"})
                st.session_state.started_chat = True
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
                    st.rerun()
                    
    elif service_option == "Diario":
        st.title("Diario Emocional")
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
            day = entry["date"][:10]
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
                        <div class="diary-text">{entry['entry']}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
        else:
            st.info("No hay entradas para este día.")
        
        if entries:
            if st.button("Editar entrada", key="edit_button"):
                st.session_state.diary_text = entries[0]["entry"]
                st.session_state.edit_mode = True
                st.rerun()
        
        with st.form(key="diary_form", clear_on_submit=True):
            new_diary_input = st.text_area(
                "Escribe tu entrada", 
                value=st.session_state.diary_text, 
                height=150, 
                key="diary_text_input"
            )
            submitted = st.form_submit_button("Actualizar entrada")
            if submitted:
                payload = {
                    "username": st.session_state.username,
                    "password": st.session_state.password,
                    "entry": new_diary_input,
                    "fecha": selected_date_str,
                    "editar": st.session_state.edit_mode
                }
                response = requests.post(f"{URL}/diario", json=payload)
                if response.ok:
                    st.success("¡Entrada actualizada y sobreescrita!")
                    st.session_state.diary_text = ""
                    st.session_state.edit_mode = False
                    st.rerun()
                else:
                    st.error("Error al actualizar la entrada.")
    
    elif service_option == "Objetivo":
        params = {"username": st.session_state.username, "password": st.session_state.password}
        response = requests.get(f"{URL}/Objetivo", params=params)
        if response.ok:
            data = response.json()
            objetivos = data.get("objetivo", {"objetivos": []})
            st.markdown("### Objetivos de Mejora")
            if objetivos["objetivos"]:
                for objetivo in objetivos["objetivos"]:
                    st.markdown(f"<p style='font-size: 20px;'>{objetivo}</p>", unsafe_allow_html=True)

            else:
                st.info("No se han generado objetivos personalizados.")
        else:
            st.error("Error al obtener los objetivos. Verifica tus entradas en el diario o tus credenciales.")

    
    elif service_option == "Profiling":
        st.title("Perfil de Personalidad")
        params = {"username": st.session_state.username, "password": st.session_state.password}
        response = requests.get(f"{URL}/perfilado", params=params)

        if response.ok:
            data = response.json()

            perfil = data.get("perfil", {})
            eneagrama = data['perfil'].get("eneagrama", "No se obtuvo un eneagrama.")
            #st.json(perfil)
            # Mostrar perfil emocional en gráfico de barras
            perfil_emocional = perfil.get("perfil_emocional", {})
            if perfil_emocional:
                import pandas as pd
                df = pd.DataFrame({
                    "Emoción": list(perfil_emocional.keys()),
                    "Valor": list(perfil_emocional.values())
                })
                import plotly.express as px
                fig_bar = px.bar(
                    df, 
                    x="Emoción", 
                    y="Valor", 
                    title="Estadísticas Emocionales",
                    labels={"Valor": "Valor Promedio", "Emoción": "Emoción"}
                )

                # Mostrar gráfico radar de los Big Five
                big_five = perfil.get("big_five", None)
                if not big_five:
                    big_five = {
                        "Openness": 0,
                        "Conscientiousness": 0,
                        "Extraversion": 0,
                        "Agreeableness": 0,
                        "Neuroticism": 0
                    }
                import plotly.graph_objects as go
                categories = list(big_five.keys())
                values = list(big_five.values())
                # Para cerrar el gráfico radar, se repite el primer elemento
                values += values[:1]
                categories += categories[:1]
                fig_radar = go.Figure(
                    data=go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill="toself",
                        name="Big Five"
                    )
                )
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=False,
                    title="Perfil Big Five"
                )
                st.plotly_chart(fig_bar)
                st.markdown(f"<h2 style='font-size: 24px;'>{perfil['tendencia']}</h2>", unsafe_allow_html=True)

                st.plotly_chart(fig_radar)
                                
                st.markdown("### Eneagrama")
                st.markdown(f"<p style='font-size: 20px;'>{eneagrama['eneagrama_type']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 20px;'>{eneagrama['description']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 20px;'>{eneagrama['recommendation']}</p>", unsafe_allow_html=True)


                
                #st.write(eneagrama)
            else:
                st.info("No se encontraron datos en el perfil emocional.")
            
        else:
            st.error("Error al obtener el perfil. Verifica tus entradas en el diario o tus credenciales.")