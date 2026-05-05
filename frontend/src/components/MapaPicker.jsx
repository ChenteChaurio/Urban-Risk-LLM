import { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import ClickHandler from "./ClickHandler";
import InfoPanel from "./InfoPanel";
import { useReverseGeocode } from "../hooks/useReverseGeocode";

const CENTER_DEFAULT = [4.711, -74.0721];
const ZOOM_DEFAULT = 13;

export default function MapaPicker() {
  const [markerPos, setMarkerPos] = useState(null);
  const { geocode, result, loading, error } = useReverseGeocode();

  async function handleLocationSelect(lat, lng) {
    setMarkerPos([lat, lng]);
    await geocode(lat, lng);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
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
