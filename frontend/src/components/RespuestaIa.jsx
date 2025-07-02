import { useEffect, useState } from 'react';

function RespuestaIa({ pregunta, cartas }) {
  const [respuesta, setRespuesta] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!pregunta || cartas.length !== 3) return;

    const obtenerInterpretacion = async () => {
      setCargando(true);
      setError(null);
      setRespuesta('');

      try {
        const response = await fetch('http://localhost:5000/api/interpretar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pregunta, cartas }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || 'Error al interpretar');
        }

        const data = await response.json();
        setRespuesta(data.respuesta);
      } catch (err) {
        setError(err.message);
      } finally {
        setCargando(false);
      }
    };

    obtenerInterpretacion();
  }, [pregunta, cartas]);

  if (!pregunta || cartas.length !== 3) return null;

  return (
    <div className="interpretacion">
      <h2>Cartas obtenidas</h2>
      <div className="cartas-grid">
        {cartas.map((carta, i) => (
          <div
            key={i}
            className={`carta ${carta.invertido ? 'carta-invertida' : ''}`}
          >
            <img
              src={`/cartas/${carta.imagen}`}
              alt={carta.nombre}
              className="carta-img"
            />
            <h3>{carta.nombre}</h3>
          </div>
        ))}
      </div>

      <h2>Interpretación de la tirada</h2>
      {cargando && <p>Cargando interpretación...</p>}
      {error && <p className="error">{error}</p>}
      {respuesta && <p>{respuesta}</p>}
    </div>
  );
}

export default RespuestaIa;
