// src/pages/Objetivo.js
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/Objetivo.css';

function Objetivo({ userCredentials }) {
  const { username, password } = userCredentials;
  const [objetivos, setObjetivos] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchObjetivos = async () => {
    try {
      const response = await api.get('/Objetivo', {
        params: { username, password }
      });
      if (response.data && response.data.objetivo && response.data.objetivo.objetivos) {
        setObjetivos(response.data.objetivo.objetivos);
      }
    } catch (error) {
      console.error("Error al obtener los objetivos:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchObjetivos();
  }, [username, password]);

  if (loading) {
    return <div>Obteniendo objetivos...</div>;
  }

  return (
    <div className="objetivo-container">
      <h2>Objetivos Personalizados</h2>
      {objetivos.length > 0 ? (
        <ul>
          {objetivos.map((obj, index) => (
            <li key={index}>{obj}</li>
          ))}
        </ul>
      ) : (
        <p>No se han generado objetivos personalizados.</p>
      )}
    </div>
  );
}

export default Objetivo;
