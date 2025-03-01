// src/pages/Perfilado.js
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Bar, Radar } from 'react-chartjs-2';
import '../styles/Perfilado.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Filler,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement
);

function Perfilado({ userCredentials }) {
  const { username, password } = userCredentials;
  const [perfil, setPerfil] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPerfilado = async () => {
      try {
        const response = await api.get('/perfilado', {
          params: { username, password }
        });
        if (response.data && response.data.perfil) {
          setPerfil(response.data.perfil);
        }
      } catch (error) {
        console.error("Error al obtener el perfil:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPerfilado();
  }, [username, password]);

  if (loading) {
    return (
      <div className="perfilado-page">
        <h2 className="perfilado-title">Cargando perfil...</h2>
      </div>
    );
  }

  if (!perfil) {
    return (
      <div className="perfilado-page">
        <h2 className="perfilado-title">No se encontró el perfil.</h2>
      </div>
    );
  }

  // Extraer datos
  const { perfil_emocional, tendencia, big_five, eneagrama } = perfil || {};

  // Datos para el gráfico de emociones (Bar)
  const emotionalData = {
    labels: perfil_emocional ? Object.keys(perfil_emocional) : [],
    datasets: [
      {
        label: 'Estadísticas Emocionales',
        data: perfil_emocional ? Object.values(perfil_emocional) : [],
        backgroundColor: 'rgba(75, 192, 192, 0.6)'
      }
    ]
  };

  const barOptions = {
    responsive: true,
    scales: {
      x: {
        ticks: { color: '#fff' },
        grid: { color: '#666' }
      },
      y: {
        ticks: { color: '#fff' },
        grid: { color: '#666' },
        beginAtZero: true,
        max: 1 // si tus emociones van de 0 a 1; ajústalo según tu rango real
      }
    },
    plugins: {
      legend: {
        labels: { color: '#fff' }
      },
      title: {
        display: true,
        text: 'Perfil Emocional',
        color: '#fff'
      }
    }
  };

  // Datos para Big Five (Radar), con fill: true para rellenar la forma
  const bigFiveData = {
    labels: big_five ? Object.keys(big_five) : [],
    datasets: [
      {
        label: 'Big Five',
        data: big_five ? Object.values(big_five) : [],
        backgroundColor: 'rgba(255, 99, 132, 0.2)', 
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
        tension: 0
      }
    ]
  };

  const radarOptions = {
    responsive: true,
    scales: {
      r: {
        min: 0,
        max: 100, // si tus Big Five van de 0 a 100
        ticks: {
          stepSize: 20,
          display: false,
          backdropColor: 'transparent'
        },
        grid: { color: '#666' },
        angleLines: { color: '#666' },
        pointLabels: {
          color: '#fff',
          font: { size: 14 }
        }
      }
    },
    plugins: {
      legend: {
        labels: { color: '#fff' }
      },
      title: {
        display: true,
        text: 'Perfil Big Five',
        color: '#fff'
      }
    }
  };

  return (
    <div className="perfilado-page">
      <h2 className="perfilado-title">Perfil de Personalidad</h2>
      
      <p className="tendencia">
        <strong>{tendencia || 'Desconocida'}</strong>
      </p>

      <div className="charts">
        <div className="chart-box">
          <Bar data={emotionalData} options={barOptions} />
        </div>
        <div className="chart-box">
          <Radar data={bigFiveData} options={radarOptions} />
        </div>
      </div>

      <div className="eneagrama-box">
        <h3>Eneagrama</h3>
        {eneagrama ? (
          <>
            <p><strong>Tipo:</strong> {eneagrama.eneagrama_type}</p>
            <br></br>
            <p><strong>Descripción:</strong> {eneagrama.description}</p>
            <br></br>
            <p><strong>Recomendación:</strong> {eneagrama.recommendation}</p>
          </>
        ) : (
          <p>No se ha calculado el eneagrama.</p>
        )}
      </div>
    </div>
  );
}

export default Perfilado;
