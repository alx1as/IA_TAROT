function PreguntaUsuario({ pregunta, setPregunta, onSubmit, loading }) {
    return (
      <div className="form">
        <label>HACÉ TU PREGUNTA:</label>
        <input
          type="text"
          value={pregunta}
          onChange={(e) => setPregunta(e.target.value)}
        />
        <button onClick={onSubmit} disabled={loading || !pregunta.trim()}>
          {loading ? 'Tirando...' : 'TIRAR CARTAS'}
        </button>
      </div>
    );
  }
  
  export default PreguntaUsuario;
  