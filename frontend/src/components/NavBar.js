// src/components/Navbar.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/NavBar.css';

function Navbar({ loggedIn, handleLogout }) {
  const navigate = useNavigate();

  const onLogout = () => {
    console.log("Logout clicked");
    handleLogout();
    navigate("/login");
  };

  return (
    <header className="navbar">
      <ul className="navbar-list">
        {loggedIn ? (
          <>
            <li><Link to="/chat">Chatbot</Link></li>
            <li><Link to="/diario">Diario</Link></li>
            <li><Link to="/perfilado">Perfilado</Link></li>
            <li><Link to="/objetivo">Objetivo</Link></li>
            <li>
              <button className="logout-button" onClick={onLogout}>
                Cerrar sesión
              </button>
            </li>
          </>
        ) : (
          <>
            <li><Link to="/login">Iniciar Sesión</Link></li>
            <li><Link to="/register">Registrarse</Link></li>
          </>
        )}
      </ul>
    </header>
  );
}

export default Navbar;
