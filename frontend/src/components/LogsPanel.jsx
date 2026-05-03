import { useEffect, useState } from "react";

const RISK_COLORS = { bajo: "#22c55e", medio: "#f59e0b", alto: "#ef4444" };

export default function LogsPanel({ api, tenant }) {
  const [logs, setLogs]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const fetchLogs = () => {
    setLoading(true);
    const url = filter === "all" ? `${api}/logs` : `${api}/logs?tenantId=${filter}`;
    fetch(url)
      .then(r => r.json())
      .then(d => { setLogs(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { fetchLogs(); }, [filter]);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
        <h2 style={{ color: "#f1f5f9", margin: 0 }}>📋 Trazabilidad de Consultas</h2>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {["all", "bogota", "metro_agency"].map(t => (
            <button key={t} onClick={() => setFilter(t)} style={{
              padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer",
              background: filter === t ? "#0284c7" : "#1e293b",
              color: filter === t ? "#fff" : "#64748b", fontSize: 12,
            }}>
              {t === "all" ? "Todos" : t}
            </button>
          ))}
          <button onClick={fetchLogs} style={{
            padding: "6px 14px", borderRadius: 8, border: "1px solid #334155",
            background: "transparent", color: "#94a3b8", cursor: "pointer", fontSize: 12,
          }}>🔄 Actualizar</button>
        </div>
      </div>

      {loading ? (
        <div style={{ color: "#64748b", padding: 32 }}>Cargando registros...</div>
      ) : logs.length === 0 ? (
        <div style={{ color: "#64748b", padding: 32, background: "#1e293b", borderRadius: 12, textAlign: "center" }}>
          No hay consultas registradas aún. Realiza una predicción para ver los logs.
        </div>
      ) : (
        <div style={{ background: "#1e293b", borderRadius: 12, border: "1px solid #334155", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#0f172a" }}>
                {["#", "Timestamp", "Tenant", "Intersección", "Tipo", "Modelo", "Resultado", "Latencia"].map(h => (
                  <th key={h} style={{ padding: "12px 16px", textAlign: "left", color: "#64748b", fontWeight: 600, fontSize: 12 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr key={log.id} style={{ borderTop: "1px solid #334155", background: i % 2 === 0 ? "transparent" : "#0f172a22" }}>
                  <td style={{ padding: "10px 16px", color: "#475569" }}>{log.id}</td>
                  <td style={{ padding: "10px 16px", color: "#64748b", fontSize: 11 }}>
                    {new Date(log.timestamp).toLocaleString("es-CO")}
                  </td>
                  <td style={{ padding: "10px 16px" }}>
                    <span style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 4, padding: "2px 8px", fontSize: 11, color: "#38bdf8" }}>
                      {log.tenantId}
                    </span>
                  </td>
                  <td style={{ padding: "10px 16px", color: "#94a3b8" }}>{log.intersectionName}</td>
                  <td style={{ padding: "10px 16px" }}>
                    <span style={{ color: log.queryType === "predict" ? "#818cf8" : "#34d399", fontSize: 12 }}>
                      {log.queryType === "predict" ? "🤖 predict" : "📋 explain"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 16px", color: "#64748b", fontSize: 12 }}>{log.modelUsed?.toUpperCase()}</td>
                  <td style={{ padding: "10px 16px" }}>
                    {log.riskResult && log.riskResult !== "?" ? (
                      <span style={{ color: RISK_COLORS[log.riskResult] || "#94a3b8", fontWeight: 700, fontSize: 12 }}>
                        {log.riskResult.toUpperCase()}
                      </span>
                    ) : <span style={{ color: "#475569" }}>—</span>}
                  </td>
                  <td style={{ padding: "10px 16px", color: "#64748b", fontSize: 12 }}>
                    {log.latencyMs ? `${log.latencyMs} ms` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div style={{ marginTop: 12, fontSize: 11, color: "#475569" }}>
        Mostrando últimas {logs.length} consultas · Base de datos H2 en memoria
      </div>
    </div>
  );
}
