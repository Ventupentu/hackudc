// src/pages/Register.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Auth.css';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/register', { username, password });
      if (response.status === 200) {
        setSuccessMessage('Usuario registrado exitosamente. Ahora inicia sesión.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }
    } catch (error) {
      setErrorMessage('Error en el registro. Tal vez el usuario ya existe.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <img src="/emotionai192.svg" alt="EmotionAI Logo" className="auth-logo" />
          <h2>Bienvenido a EmotionAI</h2>
        </div>
        {successMessage && <p className="success-message">{successMessage}</p>}
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Elige un usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Elige una contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Registrarse</button>
        </form>
        <p className="auth-switch">
          ¿Ya tienes cuenta? <a href="/login">Inicia Sesión</a>
        </p>
      </div>
    </div>
  );
}

export default Register;
