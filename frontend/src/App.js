// src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import Diario from './pages/Diario';
import Perfilado from './pages/Perfilado';
import Objetivo from './pages/Objetivo';
import './styles/App.css';

function App() {
  // Inicializamos a partir de localStorage si existe
  const [loggedIn, setLoggedIn] = useState(() => {
    return localStorage.getItem('loggedIn') === 'true';
  });
  const [userCredentials, setUserCredentials] = useState(() => {
    const creds = localStorage.getItem('userCredentials');
    return creds ? JSON.parse(creds) : { username: '', password: '' };
  });

  // Cada vez que cambie loggedIn o userCredentials, actualizamos localStorage
  useEffect(() => {
    localStorage.setItem('loggedIn', loggedIn);
  }, [loggedIn]);

  useEffect(() => {
    localStorage.setItem('userCredentials', JSON.stringify(userCredentials));
  }, [userCredentials]);

  const handleLogout = () => {
    setLoggedIn(false);
    setUserCredentials({ username: '', password: '' });
  };

  return (
    <Router>
      <header className="navbar">
        <ul className="navbar-list">
          {loggedIn ? (
            <>
              <li><a href="/chat">Chatbot</a></li>
              <li><a href="/diario">Diario</a></li>
              <li><a href="/perfilado">Perfilado</a></li>
              <li><a href="/objetivo">Objetivo</a></li>
              <li>
                <button className="logout-button" onClick={handleLogout}>
                  Cerrar sesión
                </button>
              </li>
            </>
          ) : (
            <>
              <li><a href="/login">Iniciar Sesión</a></li>
              <li><a href="/register">Registrarse</a></li>
            </>
          )}
        </ul>
      </header>

      <Routes>
        <Route 
          path="/" 
          element={loggedIn ? <Navigate to="/chat" /> : <Navigate to="/login" />} 
        />
        <Route 
          path="/login" 
          element={<Login setLoggedIn={setLoggedIn} setUserCredentials={setUserCredentials} />} 
        />
        <Route path="/register" element={<Register />} />
        {loggedIn ? (
          <>
            <Route path="/chat" element={<Chat userCredentials={userCredentials} />} />
            <Route path="/diario" element={<Diario userCredentials={userCredentials} />} />
            <Route path="/perfilado" element={<Perfilado userCredentials={userCredentials} />} />
            <Route path="/objetivo" element={<Objetivo userCredentials={userCredentials} />} />
          </>
        ) : (
          <>
            <Route path="/chat" element={<Navigate to="/login" />} />
            <Route path="/diario" element={<Navigate to="/login" />} />
            <Route path="/perfilado" element={<Navigate to="/login" />} />
            <Route path="/objetivo" element={<Navigate to="/login" />} />
          </>
        )}
        <Route 
          path="*" 
          element={loggedIn ? <Navigate to="/chat" /> : <Navigate to="/login" />} 
        />
      </Routes>
    </Router>
  );
}

export default App;
