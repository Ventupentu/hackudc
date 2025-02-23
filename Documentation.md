# Documentación Extendida del Proyecto: LLM de Emociones

Este proyecto es una aplicación web desarrollada para una hackathon que utiliza un modelo de lenguaje (LLM) para analizar y responder a las emociones de los usuarios. La aplicación permite a los usuarios interactuar con un chatbot emocional, llevar un diario emocional, obtener un perfil de personalidad basado en sus emociones y establecer objetivos personales. A continuación, se presenta una documentación más extensa que abarca más puntos del proyecto.

## Estructura del Proyecto

El proyecto está dividido en dos componentes principales:

- **Frontend:** Desarrollado con **Streamlit**, proporciona una interfaz gráfica para que los usuarios interactúen con la aplicación.
- **Backend:** Desarrollado con **FastAPI**, maneja la lógica del negocio, la interacción con la base de datos y la comunicación con el modelo de lenguaje (LLM).

### Frontend (Streamlit)

El frontend está construido con Streamlit, una biblioteca de Python que permite crear aplicaciones web interactivas de manera rápida y sencilla. La interfaz incluye:

- **Página de Inicio:** Permite a los usuarios registrarse o iniciar sesión.
- **Chatbot Emocional:** Un chatbot que responde a las emociones del usuario.
- **Diario Emocional:** Un diario donde los usuarios pueden registrar sus emociones y pensamientos.
- **Perfil de Personalidad:** Un análisis basado en las emociones registradas en el diario.
- **Objetivos Personales:** Sugerencias de objetivos basados en las entradas del diario.
- **Personas similares:** Muestra personas que puedan tener un eneagrama similar al tuyo

Además contamos con que Streamlit tiene "Streamlit Commity Coud", donde puedes enlazar un repositorio de github y ejecuar el frontend en la nube de forma sencilla.

### Backend (FastAPI)

El backend está desarrollado con FastAPI, un framework moderno y rápido para construir APIs con Python. El backend maneja:

- **Autenticación:** Registro y login de usuarios.
- **Chat:** Comunicación con el modelo de lenguaje (LLM) para generar respuestas emocionales.
- **Diario:** Almacenamiento y recuperación de entradas del diario.
- **Profiling:** Análisis de emociones y generación de perfiles de personalidad.
- **Objetivos:** Generación de objetivos basados en las entradas del diario.

El backend tambien lo ejecutamos en la nube gracias al servicio de "Render", que es gratis, aunque no es muy eficiente ni estable, a este le tuvimos que pasar las dependencias junto con las variables de entorno.
## Uso


## La base de datos

El objetivo de la clase es encargarse de hacer las sentencias SQL a la base de datos, se encargará tanto de incorporar datos a la base, como de extraerlos y llevarlos al formato indicado para la aplicación.

## Instalación y Ejecución en Local

### Requisitos

- Python 3.10 o superior.
- Bibliotecas de Python: `streamlit`, `fastapi`, `uvicorn`, `requests`, `nltk`, `text2emotion`, `mysql-connector-python`, `bcrypt`, `plotly`.

### Instalación

Clona el repositorio del proyecto:

```bash
git clone https://github.com/santipvz/hackudc.git
cd hackudc
```

Crea un entorno virtual e instala las dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
pip install -r requirements.txt
```

Configura la base de datos:

1. Asegúrate de tener MySQL en algún servidor (en nuestro caso alwaysdata) o instalada localmente 
2. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables, para la base de datos, para la api key del LLM y para la url local y en la web:

```env
MISTRAL_API_KEY="your_api_key"
DB_HOST="your_host"
DB_NAME="your_name"
DB_USER="your_user"
DB_PASSWORD="your_password"
# URL="url_1"
URL="url_2"
```

## Uso de la Aplicación

### Encender en local:
Para lanzar el main.py: u
```bash
uvicorn main:emotionai --reload
```

Para lanzar el emotionai.py:

```bash
streamlit run emotionai.py
```
Entrar al localhost del emotionai.py para probar el chatbot

### Usar online

Entrar al siguiente enlace: https://emotionai-chat.streamlit.app/

### Registro e Inicio de Sesión

1. En la página de inicio, selecciona "Registrarse" para crear una nueva cuenta o "Iniciar Sesión" si ya tienes una.
2. Introduce tu nombre de usuario y contraseña, ten en cuenta que los usuarios no se van a poder repetir, ya que se almacenan en una base de datos mysql alojada en alwaysdata.

### Chatbot Emocional

1. Selecciona "Chatbot" en el menú de servicios.
2. Escribe tus mensajes en el cuadro de texto y el chatbot responderá basándose en tus emociones, este tendrña contexto de tu nombre de ususario y las anteriores 10 interacciones contigo, guardandose el chat aunque cierres la sesion, gracias a la base de datos.

### Diario Emocional

1. Selecciona "Diario" en el menú de servicios.
2. Escribe tus pensamientos y emociones en el diario.
3. Puedes editar entradas anteriores.

### Perfil de Personalidad

1. Selecciona "Profiling" en el menú de servicios.
2. La aplicación generará un perfil de personalidad basado en tus emociones registradas, teniendo en cuenta tu eneagrama, y de las big five emotions.

### Objetivos Personales

1. Selecciona "Objetivo" en el menú de servicios.
2. La aplicación te sugerirá objetivos basados en tus entradas del diario.

## Estructura del Código

### `emotionai.py`

Este archivo contiene el código del frontend desarrollado con Streamlit. Incluye la interfaz gráfica y la lógica para interactuar con el backend, junto con las pestañas que sean necesarias. Viene con dos urls, una para ejecutarla en local y otra para ejecutarla desplegada en la web
# URL="http://localhost:8000"
URL="https://emotionai-chat.streamlit.app/"


### `main.py`

Este archivo contiene el código del backend desarrollado con FastAPI. Incluye los endpoints para manejar la autenticación, el chat, el diario, el profiling y los objetivos. Es la base para poder enviar los mensajes y la existencia de la web.

### `access_bd.py`

Este archivo contiene la clase `AccessBD` que maneja la interacción con la base de datos MySQL, que en el caso de esta implementación, la alojamos en alwaysdata. Incluye métodos para registrar usuarios, insertar y recuperar entradas del diario, y manejar el historial del chat.

## Detalles Técnicos

### Autenticación

La autenticación se maneja mediante el uso de `bcrypt` para hashear las contraseñas y almacenarlas de manera segura en la base de datos. Los usuarios pueden registrarse e iniciar sesión, y sus credenciales se verifican contra la base de datos.

### Chatbot Emocional

El chatbot utiliza el modelo de lenguaje **Mistral** para generar respuestas basadas en las emociones detectadas en los mensajes del usuario. Las emociones se detectan utilizando la biblioteca `text2emotion`, que analiza el texto y devuelve un diccionario con las emociones detectadas.

### Diario Emocional

El diario permite a los usuarios registrar sus pensamientos y emociones. Cada entrada del diario se almacena en la base de datos junto con las emociones detectadas. Los usuarios pueden editar entradas anteriores y ver sus entradas agrupadas por fecha.

### Perfil de Personalidad

El perfil de personalidad se genera basándose en las emociones registradas en el diario. Se utiliza el modelo **Big Five** para analizar las emociones y generar un perfil de personalidad. Además, se utiliza el **eneagrama** para clasificar al usuario en un tipo de personalidad específico.

### Objetivos Personales

Los objetivos personales se generan basándose en las entradas del diario. El modelo de lenguaje analiza las entradas y sugiere objetivos de mejora basados en las emociones y pensamientos registrados, tomando en cuenta contexto anterior y memoria. Combinandolo con la existencia del diario, para tener aún mas mejores.

## Contribuciones

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añade nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo LICENSE para más detalles.

## Contacto

Si tienes alguna pregunta o sugerencia, no dudes en contactarnos en el repositorio https://github.com/Ventupentu/hackudc

