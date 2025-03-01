// src/pages/Objetivo.js
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/Objetivo.css';

function Objetivo({ userCredentials }) {
  const { username, password } = userCredentials;
  const [objetivos, setObjetivos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchObjetivos = async () => {
      try {
        const response = await api.get('/Objetivo', {
          params: { username, password }
        });
        if (response.data && response.data.objetivo) {
          setObjetivos(response.data.objetivo.objetivos || []);
        }
      } catch (err) {
        console.error("Error al obtener los objetivos:", err);
        setError('No se han podido cargar los objetivos.');
      } finally {
        setLoading(false);
      }
    };
    fetchObjetivos();
  }, [username, password]);

  if (loading) {
    return (
      <div className="objetivo-page">
        <h2 className="objetivo-title">Cargando objetivos...</h2>
      </div>
    );
  }

  return (
    <div className="objetivo-page">
      <div className="objetivo-container">
        <h2 className="objetivo-title">Objetivos Personalizados</h2>
        {error && <p className="error-message">{error}</p>}
        {!error && objetivos.length > 0 ? (
          <ul className="objetivo-list">
            {objetivos.map((obj, index) => (
              <li key={index} className="objetivo-item">{obj}</li>
            ))}
          </ul>
        ) : (
          <p>No se han generado objetivos personalizados.</p>
        )}
      </div>
    </div>
  );
}

export default Objetivo;
