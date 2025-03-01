// src/pages/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Auth.css';

function Login({ setLoggedIn, setUserCredentials }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/login', { username, password });
      if (response.status === 200) {
        setLoggedIn(true);
        setUserCredentials({ username, password });
        navigate('/chat');
      }
    } catch (error) {
      setErrorMessage('Credenciales inválidas. Intenta de nuevo.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <img src="/emotionai192.svg" alt="EmotionAI Logo" className="auth-logo" />
          <h2>Bienvenido a EmotionAI</h2>
        </div>
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Iniciar Sesión</button>
        </form>
        <p className="auth-switch">
          ¿No tienes cuenta? <a href="/register">Regístrate</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
