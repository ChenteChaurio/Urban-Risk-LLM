import { useState } from "react";

const INTERSECTIONS = [
  { name: "Cra 7 con Calle 26", lat: 4.6097, lng: -74.0817 },
  { name: "Calle 100 con Autopista Norte", lat: 4.6869, lng: -74.0444 },
  { name: "Av. Eldorado con Cra 30", lat: 4.6476, lng: -74.1024 },
  { name: "Cra 15 con Calle 72", lat: 4.6599, lng: -74.0569 },
  { name: "Calle 80 con Av. Boyacá", lat: 4.6986, lng: -74.1107 },
  { name: "Av. Caracas con Calle 53", lat: 4.6427, lng: -74.0737 },
  { name: "Cra 11 con Calle 93", lat: 4.6769, lng: -74.0503 },
  { name: "Av. Suba con Cra 91", lat: 4.7241, lng: -74.0912 },
];

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

export default function PredictForm({ onSubmit, loading }) {
  const now = new Date();
  const [form, setForm] = useState({
    intersection_idx: 0,
    hour: now.getHours(),
    day_of_week: now.getDay(),
    vehicle_flow: 850,
    congestion_index: 0.6,
    accidents_last_12m: 8,
    climate_condition: 0,
    intersection_type: 0,
    model_override: "",
  });

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = (e) => {
    e.preventDefault();
    const inter = INTERSECTIONS[form.intersection_idx];
    onSubmit({
      intersection_name: inter.name,
      latitude: inter.lat,
      longitude: inter.lng,
      hour: Number(form.hour),
      day_of_week: Number(form.day_of_week),
      vehicle_flow: Number(form.vehicle_flow),
      congestion_index: Number(form.congestion_index),
      accidents_last_12m: Number(form.accidents_last_12m),
      climate_condition: Number(form.climate_condition),
      intersection_type: Number(form.intersection_type),
      model_override: form.model_override || null,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ background: "#1e293b", borderRadius: 12, padding: 24, border: "1px solid #334155" }}>
      <h3 style={{ margin: "0 0 20px", color: "#38bdf8", fontSize: 15 }}>📍 Parámetros de Intersección</h3>

      {field("Intersección", (
        <select value={form.intersection_idx} onChange={e => set("intersection_idx", e.target.value)} style={inp}>
          {INTERSECTIONS.map((i, idx) => <option key={idx} value={idx}>{i.name}</option>)}
        </select>
      ))}

      {field("Hora del día (0–23)", (
        <input type="number" min={0} max={23} value={form.hour}
          onChange={e => set("hour", e.target.value)} style={inp} />
      ))}

      {field("Día de la semana (0=Lun … 6=Dom)", (
        <input type="number" min={0} max={6} value={form.day_of_week}
          onChange={e => set("day_of_week", e.target.value)} style={inp} />
      ))}

      {field("Flujo vehicular (veh/h)", (
        <input type="number" min={0} max={5000} value={form.vehicle_flow}
          onChange={e => set("vehicle_flow", e.target.value)} style={inp} />
      ))}

      {field(`Índice de congestión (${form.congestion_index})`, (
        <input type="range" min={0} max={1} step={0.01} value={form.congestion_index}
          onChange={e => set("congestion_index", e.target.value)}
          style={{ width: "100%", accentColor: "#38bdf8" }} />
      ))}

      {field("Accidentes últimos 12 meses", (
        <input type="number" min={0} max={100} value={form.accidents_last_12m}
          onChange={e => set("accidents_last_12m", e.target.value)} style={inp} />
      ))}

      {field("Condición climática", (
        <select value={form.climate_condition} onChange={e => set("climate_condition", e.target.value)} style={inp}>
          <option value={0}>☀️ Seco</option>
          <option value={1}>🌧️ Lluvia moderada</option>
          <option value={2}>⛈️ Tormenta</option>
        </select>
      ))}

      {field("Tipo de intersección", (
        <select value={form.intersection_type} onChange={e => set("intersection_type", e.target.value)} style={inp}>
          <option value={0}>🚦 Semaforizada</option>
          <option value={1}>🔄 Rotonda</option>
          <option value={2}>⚠️ Sin control semafórico</option>
        </select>
      ))}

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
