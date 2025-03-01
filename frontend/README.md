# EmotionAI

Este proyecto consta de dos partes:
- **Backend**: Desarrollado en Python con FastAPI, ejecutado con uvicorn.
- **Frontend**: Aplicación React administrada con npm.

A continuación se muestran los pasos para instalar las dependencias y ejecutar el proyecto en local en un sistema Linux, usando dos terminales.

---

## Requisitos

- **Python 3.8+**
- **Node.js y npm** (se recomienda instalar la versión LTS)

---

## Instalación de Node.js y npm (en Linux)

### Usando Node Version Manager (nvm) (recomendado)

1. Instala nvm ejecutando en la terminal:

   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
   ```

    ```bash
    source ~/.nvm/nvm.sh
    ```

2. Instala la versión LTS de Node.js (esto instalará también npm):

    ```bash
    nvm install --lts
    ```

3. Verifica la instalación:

    ```bash
    node -v
    npm -v
    ```

### Alternativamente, usando el gestor de paquetes (apt)

1. Actualiza tus repositorios:

    ```bash
    sudo apt update
    ```

2. Instala Node.js y npm:

    ```bash
    sudo apt install nodejs npm
    ```

3. Verifica la instalación:

    ```bash
    node -v
    npm -v
    ```

## Configuración del Backend (FastAPI)


1. Navega a la carpeta del backend (por ejemplo, backend/):

    ```bash
    cd backend
    ```

2. Crea un entorno virtual y actívalo:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Instala las dependencias de Python (asegúrate de tener un archivo requirements.txt o instala las librerías necesarias manualmente):

    ```bash
    pip install -r requirements.txt
    ```

4. Ejecuta el servidor con uvicorn:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

Esto iniciará el backend en http://localhost:8000.

## Configuración del Frontend (React)

1. Abre otra terminal y navega a la carpeta del frontend (por ejemplo, frontend/):

    ```bash
    cd frontend
    ```

2. Instala las dependencias del frontend:

    ```bash
    npm install
    ```

3. Inicia la aplicación React:

    ```bash
    npm start
    ```

Esto lanzará el servidor de desarrollo, normalmente en [http://localhost:3000](http://localhost:3000). La aplicación React se conectará al backend a través de los endpoints definidos.

---

## Resumen de Terminales

**Terminal 1 (Backend):**
- Activar entorno virtual: `source .venv/bin/activate`
- Ejecutar: `uvicorn main:app --host 0.0.0.0 --port 8000`

**Terminal 2 (Frontend):**
- Instalar dependencias: `npm install`
- Ejecutar: `npm start`


---

Con estos pasos tendrás el proyecto instalado y funcionando en local, usando dos terminales (una para el backend y otra para el frontend). Consulta la documentación de [FastAPI](https://fastapi.tiangolo.com/) y [Create React App](https://create-react-app.dev/) para más detalles.