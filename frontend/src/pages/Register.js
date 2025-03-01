// src/pages/Register.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../styles/Auth.css';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/register', { username, password });
      alert("Usuario registrado exitosamente. Ahora inicia sesión.");
      navigate('/login');
    } catch (error) {
      alert("Error en el registro. Es posible que el usuario ya exista.");
    }
  };

  return (
    <div className="auth-container">
      <h2>Registrarse</h2>
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
    </div>
  );
}

export default Register;
