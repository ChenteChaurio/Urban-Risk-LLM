import { useState } from "react";
import PredictForm from "./components/PredictForm";
import ResultPanel from "./components/ResultPanel";
import MetricsPanel from "./components/MetricsPanel";
import LogsPanel from "./components/LogsPanel";
import MapaPicker from "./components/MapaPicker";

const TABS = ["Predicción", "Métricas", "Trazabilidad"];

export default function App() {
  const [activeTab, setActiveTab] = useState("Predicción");
  const [result, setResult] = useState(null);
  const [explanation, setExpl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tenant, setTenant] = useState("bogota");

  const API = import.meta.env.VITE_API_URL || "http://localhost:8080/api";

  const handlePredict = async (formData) => {
    setLoading(true);
    setResult(null);
    setExpl(null);
    try {
      const res = await fetch(`${API}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-tenant-id": tenant },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      setResult(data);

      // Auto-explicar
      const explRes = await fetch(`${API}/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-tenant-id": tenant },
        body: JSON.stringify({
          intersection_name:  data.intersection_name,
          risk_label:         data.risk_label,
          congestion_index:   formData.congestion_index,
          accidents_last_12m: formData.accidents_last_12m,
          climate_condition:  formData.climate_condition,
          top_k: 3,
        }),
      });
      const explData = await explRes.json();
      setExpl(explData);
    } catch (e) {
      alert("Error conectando con el backend: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#f1f5f9", fontFamily: "Inter, sans-serif" }}>
      {/* Header */}
      <header style={{ background: "#1e293b", borderBottom: "1px solid #334155", padding: "16px 32px", display: "flex", alignItems: "center", gap: 20 }}>
        <div style={{ fontSize: 22, fontWeight: 700, color: "#38bdf8" }}>🏙️ Urban Risk Platform</div>
        <div style={{ flex: 1 }} />
        <label style={{ fontSize: 13, color: "#94a3b8" }}>Tenant:</label>
        <select
          value={tenant}
          onChange={e => setTenant(e.target.value)}
          style={{ background: "#334155", color: "#f1f5f9", border: "none", borderRadius: 8, padding: "6px 12px", fontSize: 13 }}
        >
          <option value="bogota">Secretaría Distrital de Movilidad - Bogotá</option>
          <option value="metro_agency">Agencia Metropolitana</option>
        </select>
      </header>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 2, padding: "16px 32px 0", borderBottom: "1px solid #334155" }}>
        {TABS.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            style={{
              padding: "10px 24px", borderRadius: "8px 8px 0 0", border: "none",
              background: activeTab === tab ? "#1e293b" : "transparent",
              color: activeTab === tab ? "#38bdf8" : "#64748b",
              fontWeight: activeTab === tab ? 700 : 400,
              cursor: "pointer", fontSize: 14,
              borderBottom: activeTab === tab ? "2px solid #38bdf8" : "2px solid transparent",
            }}>
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <main style={{ padding: "32px", maxWidth: 1200, margin: "0 auto" }}>
        {activeTab === "Predicción" && (
          <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 24 }}>
            <div>
              <PredictForm onSubmit={handlePredict} loading={loading} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <MapaPicker />
              <ResultPanel result={result} explanation={explanation} loading={loading} />
            </div>
          </div>
        )}
        {activeTab === "Métricas" && <MetricsPanel api={API} />}
        {activeTab === "Trazabilidad" && <LogsPanel api={API} tenant={tenant} />}
      </main>
    </div>
  );
}
