// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://emotion-ai-front.onrender.com'  // Cambia esta URL según dónde esté desplegado tu backend
});

export default api;
