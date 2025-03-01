// src/App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/NavBar';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import Diario from './pages/Diario';
import Perfilado from './pages/Perfilado';
import Objetivo from './pages/Objetivo';
import './styles/GlobalStyles.css'; // Estilos globales (fondo, fuentes, etc.)

function App() {
  const [loggedIn, setLoggedIn] = useState(() => localStorage.getItem('loggedIn') === 'true');
  const [userCredentials, setUserCredentials] = useState(() => {
    const creds = localStorage.getItem('userCredentials');
    return creds ? JSON.parse(creds) : { username: '', password: '' };
  });

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
      {/* Renderiza la Navbar SOLO si el usuario está logueado */}
      {loggedIn && <Navbar loggedIn={loggedIn} handleLogout={handleLogout} />}

      <Routes>
        {/* Redirigir / a /chat si logueado, o /login si no */}
        <Route path="/" element={loggedIn ? <Navigate to="/chat" /> : <Navigate to="/login" />} />

        {/* Login y Registro */}
        <Route
          path="/login"
          element={<Login setLoggedIn={setLoggedIn} setUserCredentials={setUserCredentials} />}
        />
        <Route path="/register" element={<Register />} />

        {/* Rutas protegidas: si no logueado, redirigir a /login */}
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

        {/* Ruta comodín */}
        <Route path="*" element={loggedIn ? <Navigate to="/chat" /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
