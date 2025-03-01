import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/NavBar.css';

const NavBar = ({ loggedIn, onLogout }) => {
  return (
    <nav className="navbar">
      <ul className="navbar-list">
        {loggedIn ? (
          <>
            <li><Link to="/chat">Chatbot</Link></li>
            <li><Link to="/diario">Diario</Link></li>
            <li><Link to="/perfilado">Perfilado</Link></li>
            <li><Link to="/objetivo">Objetivo</Link></li>
            <li><button onClick={onLogout}>Cerrar sesión</button></li>
          </>
        ) : (
          <>
            <li><Link to="/login">Iniciar Sesión</Link></li>
            <li><Link to="/register">Registrarse</Link></li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default NavBar;
