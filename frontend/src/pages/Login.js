// src/pages/Login.js

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Auth.css';

function Login({ setLoggedIn, setUserCredentials }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Llamada al endpoint /login
      await api.post('/login', { username, password });
      setLoggedIn(true);
      setUserCredentials({ username, password });
      navigate('/chat');
    } catch (error) {
      alert("Credenciales inválidas o error en el login.");
    }
  };

  return (
    <div className="auth-container">
      <h2>Iniciar Sesión</h2>
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
         <button type="submit">Ingresar</button>
      </form>
    </div>
  );
}

export default Login;
