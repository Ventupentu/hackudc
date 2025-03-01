// src/pages/Diario.js
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/Diario.css';

function Diario({ userCredentials }) {
  const { username, password } = userCredentials;

  // Fecha seleccionada (por defecto, hoy)
  const [selectedDate, setSelectedDate] = useState(() => {
    const today = new Date().toISOString().split("T")[0];
    return today;
  });
  
  // Texto de la entrada
  const [diaryEntry, setDiaryEntry] = useState('');
  
  // Mensajes de estado (éxito o error) para mostrar en la interfaz
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Carga la entrada existente (si la hay) al cambiar la fecha
  useEffect(() => {
    const fetchEntry = async () => {
      try {
        const response = await api.get('/diario', {
          params: {
            username,
            password
          }
        });
        // 'response.data.diario' contiene todas las entradas, buscamos la de la fecha seleccionada
        if (response.data && response.data.diario) {
          const entryForDate = response.data.diario.find(e => e.date === selectedDate);
          if (entryForDate) {
            setDiaryEntry(entryForDate.entry);
          } else {
            setDiaryEntry('');
          }
        }
      } catch (error) {
        console.error("Error al obtener entradas del diario:", error);
      }
    };
    fetchEntry();
  }, [selectedDate, username, password]);

  // Manejo de envío (crear o actualizar entrada)
  const handleSubmit = async () => {
    try {
      // Si ya hay texto, se crea/actualiza la entrada
      const payload = {
        username,
        password,
        entry: diaryEntry,
        fecha: selectedDate,
        editar: true // o false si deseas crear de cero; 
                     // en este ejemplo asumimos que se puede editar si ya existe
      };
      const response = await api.post('/diario', payload);
      if (response.data && response.data.mensaje) {
        setSuccessMessage('Entrada actualizada correctamente.');
        setErrorMessage('');
      }
    } catch (error) {
      setErrorMessage('Error al actualizar la entrada.');
      setSuccessMessage('');
    }
  };

  return (
    <div className="diary-page">
      <h2>Diario Emocional</h2>

      {/* Mensajes de éxito o error en la interfaz */}
      {successMessage && <p className="success-message">{successMessage}</p>}
      {errorMessage && <p className="error-message">{errorMessage}</p>}

      <div className="diary-container">
        <div className="date-selector">
          <label htmlFor="dateInput">Selecciona la fecha:</label>
          <input
            type="date"
            id="dateInput"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>

        <textarea
          className="diary-textarea"
          placeholder="Escribe tu entrada..."
          value={diaryEntry}
          onChange={(e) => setDiaryEntry(e.target.value)}
          rows={8}
        />

        <button className="diary-submit-button" onClick={handleSubmit}>
          {diaryEntry ? 'Actualizar entrada' : 'Crear entrada'}
        </button>
      </div>
    </div>
  );
}

export default Diario;
