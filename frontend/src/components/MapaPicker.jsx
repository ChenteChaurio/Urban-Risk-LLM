import { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import ClickHandler from "./ClickHandler";
import InfoPanel from "./InfoPanel";
import { useReverseGeocode } from "../hooks/useReverseGeocode";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080/api";

const CENTER_DEFAULT = [4.711, -74.0721];
const ZOOM_DEFAULT = 13;

const HOTSPOTS = [
  { label: "Av. del Sur x Cl 63 S", lat: 4.597, lon: -74.179 },
  { label: "Av. Boyaca x Cl 60 S", lat: 4.562, lon: -74.139 },
  { label: "Kr 80 x Cl 2", lat: 4.632, lon: -74.154 },
  { label: "Av. de las Americas x Kr 72", lat: 4.631, lon: -74.138 },
  { label: "Av. Ciudad de Cali x Cl 26", lat: 4.679, lon: -74.120 },
  { label: "Av. Boyaca x Cl 12", lat: 4.645, lon: -74.132 },
  { label: "Cl 80 x Kr 72", lat: 4.696, lon: -74.090 },
  { label: "Cl 13 x Kr 72", lat: 4.649, lon: -74.127 },
  { label: "Kr 30 x Cl 26", lat: 4.627, lon: -74.081 },
  { label: "Av. del Sur x Cl 59 S", lat: 4.597, lon: -74.177 },
];

export default function MapaPicker({ onPick }) {
  const [markerPos, setMarkerPos] = useState(null);
  const { geocode, result, loading, error } = useReverseGeocode();

  async function handleLocationSelect(lat, lng) {
    setMarkerPos([lat, lng]);
    const res = await geocode(lat, lng);
    // Solicitar features al backend (solo lo que existe en el histórico)
    try {
      const body = { latitude: lat, longitude: lng };
      const r = await fetch(`${API_BASE.replace(/\/api$/, '')}/features`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
      if (r.ok) {
        const features = await r.json();
        if (onPick) onPick({ latitude: lat, longitude: lng, displayName: res?.displayName, features });
        return;
      }
    } catch (e) {
      // fallthrough: enviar solo coords
    }

    if (onPick) onPick({ latitude: lat, longitude: lng, displayName: res?.displayName });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 12, padding: 12 }}>
        <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>
          Puntos con mas reportes (demo rapida)
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {HOTSPOTS.map(h => (
            <button
              key={h.label}
              onClick={() => handleLocationSelect(h.lat, h.lon)}
              style={{
                padding: "6px 10px",
                borderRadius: 8,
                border: "1px solid #334155",
                background: "#1e293b",
                color: "#e2e8f0",
                fontSize: 12,
                cursor: "pointer",
              }}
            >
              {h.label}
            </button>
          ))}
        </div>
      </div>
      <MapContainer
        center={CENTER_DEFAULT}
        zoom={ZOOM_DEFAULT}
        style={{ height: "450px", width: "100%", borderRadius: "8px" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <ClickHandler onLocationSelect={handleLocationSelect} />
        {markerPos && (
          <Marker position={markerPos}>
            <Popup>{result?.displayName ?? "Cargando..."}</Popup>
          </Marker>
        )}
      </MapContainer>

      <InfoPanel result={result} loading={loading} error={error} />
    </div>
  );
}
