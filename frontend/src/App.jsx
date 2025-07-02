// Frontend React (modularizado)
import { useState } from 'react';
import './App.css';
import PreguntaUsuario from "./components/PreguntaUsuario"
import RespuestaIa from './components/RespuestaIa';

function App() {
  const [pregunta, setPregunta] = useState('');
  const [cartas, setCartas] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTirada = async () => {
    if (!pregunta.trim()) return;
    setLoading(true);
    setError(null);
    setCartas([]);

    try {
      const response = await fetch('/api/tirada', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ pregunta })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Error al tirar las cartas');
      }

      const data = await response.json();
      setCartas(data.cartas);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>TAROT IA</h1>
      <PreguntaUsuario
        pregunta={pregunta}
        setPregunta={setPregunta}
        onSubmit={handleTirada}
        loading={loading}
      />
      {error && <p className="error">{error}</p>}
      <RespuestaIa pregunta={pregunta} cartas={cartas} />

    </div>
  );
}

export default App;
