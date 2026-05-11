import { useState, useEffect } from "react";

const field = (label, children) => (
  <div style={{ marginBottom: 14 }}>
    <label style={{ display: "block", fontSize: 12, color: "#94a3b8", marginBottom: 4 }}>{label}</label>
    {children}
  </div>
);

const inp = {
  width: "100%", background: "#1e293b", border: "1px solid #334155",
  borderRadius: 8, color: "#f1f5f9", padding: "8px 12px", fontSize: 14,
  boxSizing: "border-box",
};

export default function PredictForm({ onSubmit, loading, selectedLocation }) {
  const [form, setForm] = useState({
    intersection_name: "",
    latitude: null,
    longitude: null,
    accidents_last_12m: 0,
    severity_local_mean: 0,
    accident_rate: 0,
    locality_acc_count: 0,
    model_override: "",
  });

  useEffect(() => {
    if (selectedLocation) {
      setForm(f => ({
        ...f,
        intersection_name: selectedLocation.displayName || "Seleccionado desde mapa",
        latitude: selectedLocation.latitude,
        longitude: selectedLocation.longitude,
      }));
    }
  }, [selectedLocation]);

  // Rellenar únicamente 'accidents_last_12m' si el backend lo proporciona.
  useEffect(() => {
    if (selectedLocation && selectedLocation.features && typeof selectedLocation.features.accidents_last_12m !== 'undefined') {
      const cnt = selectedLocation.features.accidents_last_12m;
      setForm(f => ({ ...f, accidents_last_12m: Number(cnt) }));
    }
  }, [selectedLocation]);

  useEffect(() => {
    if (selectedLocation && selectedLocation.features) {
      setForm(f => ({
        ...f,
        severity_local_mean: Number(selectedLocation.features.severity_local_mean ?? 0),
        accident_rate: Number(selectedLocation.features.accident_rate ?? 0),
        locality_acc_count: Number(selectedLocation.features.locality_acc_count ?? 0),
      }));
    }
  }, [selectedLocation]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const now = new Date();
    onSubmit({
      intersection_name: form.intersection_name || "desde_mapa",
      latitude: form.latitude,
      longitude: form.longitude,
      hour: now.getHours(),
      day_of_week: now.getDay(),
      accidents_last_12m: Number(form.accidents_last_12m),
      severity_local_mean: Number(form.severity_local_mean),
      accident_rate: Number(form.accident_rate),
      locality_acc_count: Number(form.locality_acc_count),
      model_override: form.model_override || null,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ background: "#1e293b", borderRadius: 12, padding: 24, border: "1px solid #334155" }}>
      <h3 style={{ margin: "0 0 20px", color: "#38bdf8", fontSize: 15 }}>📍 Parámetros de Intersección</h3>

      {field("Intersección (usar mapa para seleccionar)", (
        <div>
          <input type="text" value={form.intersection_name} onChange={e => set("intersection_name", e.target.value)} placeholder="Nombre (opcional)" style={inp} />
          <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 6 }}>
            {form.latitude && form.longitude ? `Coordenadas: ${form.latitude.toFixed(6)}, ${form.longitude.toFixed(6)}` : "Seleccione una ubicación en el mapa"}
          </div>
        </div>
      ))}

      <div style={{ marginBottom: 14 }}>
        <label style={{ display: "block", fontSize: 12, color: "#94a3b8", marginBottom: 4 }}>
          Hora y dia (automatico)
        </label>
        <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8, color: "#f1f5f9", padding: "8px 12px", fontSize: 14 }}>
          {new Date().toLocaleString("es-CO", { hour: "2-digit", minute: "2-digit", weekday: "short" })}
        </div>
      </div>

      {selectedLocation?.features?.accidents_last_12m !== undefined && (
        <div style={{ marginBottom: 14 }}>
          <label style={{ display: "block", fontSize: 12, color: "#94a3b8", marginBottom: 4 }}>
            Accidentes últimos 12 meses (histórico)
          </label>
          <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8, color: "#f1f5f9", padding: "8px 12px", fontSize: 14 }}>
            {form.accidents_last_12m}
          </div>
        </div>
      )}
      

      {field("Modelo (opcional)", (
        <select value={form.model_override} onChange={e => set("model_override", e.target.value)} style={inp}>
          <option value="">Default del tenant</option>
          <option value="xgb">XGBoost</option>
          <option value="rf">Random Forest</option>
          <option value="dnn">Red Neuronal</option>
        </select>
      ))}

      <button type="submit" disabled={loading} style={{
        width: "100%", padding: "12px", marginTop: 8,
        background: loading ? "#334155" : "#0284c7",
        color: "#fff", border: "none", borderRadius: 8,
        fontSize: 15, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
        transition: "background 0.2s",
      }}>
        {loading ? "⏳ Analizando..." : "🔍 Predecir Riesgo"}
      </button>
    </form>
  );
}
