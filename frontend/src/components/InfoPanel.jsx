export default function InfoPanel({ result, loading, error }) {
  if (!result && !loading && !error) return null;

  return (
    <div style={{ padding: "1rem", border: "1px solid #e2e8f0", borderRadius: "8px" }}>
      {loading && <p>Buscando direccion...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {result && (
        <>
          <p><strong>Direccion:</strong> {result.displayName}</p>
          <p><strong>Calle:</strong> {result.address.road ?? "-"}</p>
          <p><strong>Barrio:</strong> {result.address.neighbourhood ?? result.address.suburb ?? "-"}</p>
          <p><strong>Ciudad:</strong> {result.address.city ?? result.address.town ?? "-"}</p>
          <p><strong>Pais:</strong> {result.address.country ?? "-"}</p>
          <p style={{ color: "#718096", fontSize: "0.85rem" }}>
            Coordenadas: {result.lat.toFixed(5)}, {result.lng.toFixed(5)}
          </p>
        </>
      )}
    </div>
  );
}
