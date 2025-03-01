// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'  // Cambia esta URL según dónde esté desplegado tu backend
});

export default api;
