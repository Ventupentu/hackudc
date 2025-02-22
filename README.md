# EmotionAI - HackUDC Project

![EmotionAI Logo](#) *(Considera añadir un logo o imagen representativa)*

## Overview

EmotionAI is an innovative project developed during HackUDC that leverages Mistral AI to detect emotions from user input and provide empathetic responses. It combines advanced Natural Language Processing (NLP) techniques with Retrieval-Augmented Generation (RAG) to deliver personalized interactions. Additionally, it includes a personal diary feature to help users track their emotional state over time.

## Key Features

- **Emotion Detection:** Utilizes Mistral AI to identify emotions such as happiness, sadness, anger, and more.
- **Empathetic Interaction:** Provides context-aware, empathetic responses to user inputs.
- **Emotion Diary:** Allows users to log and review their emotional state over time.
- **Personality Profiling:** Analyzes diary entries to generate insights into the user's personality traits using the Big Five model and Enneagram.
- **Interactive Visualizations:** Displays emotional trends and personality profiles using dynamic charts.
- **Improvements for the users** Helps the user seek its ideal form.
## Tech Stack

- **Backend:** Python, FastAPI, MySQL  
- **Frontend:** Streamlit  
- **AI Models:** Mistral AI, NLTK, Text2Emotion  
- **Visualization:** Plotly  
- **Authentication:** Custom user authentication with password hashing  

## Installation

### Prerequisites

- Python 3.10+
- MySQL Server
- Mistral AI API Key

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/santipvz/hackudc.git  
   cd hackudc  
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt  
   ```

3. **Set up the database:**
   - Create a MySQL database and update the connection details in `access_bd.py`.
   - Run the necessary migrations to set up the tables, hosted in alwaysdata.

4. **Configure the environment:**
   - Create a `.env` file in the root directory and add your Mistral AI API key:
     ```plaintext
     MISTRAL_API_KEY=your_api_key_here  
     ```
   - Alongside the necessary variables for the DB

5. **Run the backend server:**
   ```bash
   python main.py  
   ```

6. **Launch the Streamlit frontend:**
   ```bash
   streamlit run app.py  
   ```

## Usage

### Chatbot

- Interact with the EmotionAI chatbot to receive empathetic responses based on your emotional state.
- The chatbot analyzes your input using Mistral AI and adjusts its tone accordingly.

### Emotion Diary

- Log your daily emotions and thoughts.
- View historical entries and track emotional trends over time.

### Personality Profiling

- Get insights into your personality traits using the Big Five model and Enneagram.
- Explore interactive visualizations of your emotional patterns.

## API Endpoints

### Backend (FastAPI)

- **POST /chat:** Chat with the EmotionAI bot.
- **POST /register:** Register a new user.
- **POST /login:** Authenticate a user.
- **POST /diario:** Add or update a diary entry.
- **GET /diario:** Retrieve diary entries for a user.
- **GET /profiling:** Generate personality profiling based on diary entries.

## Future Enhancements

- **Voice Input:** Add support for voice-based interactions.
- **Mobile App:** Develop a cross-platform mobile application.
- **Advanced Analytics:** Incorporate machine learning models for deeper emotional insights.
- **Gamification:** Introduce gamified elements to encourage consistent diary usage.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## Additional Notes

- Consider adding a **Contributors** section to acknowledge team members.


