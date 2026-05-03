const RISK_COLORS = { bajo: "#22c55e", medio: "#f59e0b", alto: "#ef4444" };
const RISK_BG    = { bajo: "#14532d22", medio: "#78350f22", alto: "#7f1d1d22" };
const RISK_EMOJI = { bajo: "🟢", medio: "🟡", alto: "🔴" };

function ProbBar({ label, value, color }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#94a3b8", marginBottom: 3 }}>
        <span>{label}</span><span>{(value * 100).toFixed(1)}%</span>
      </div>
      <div style={{ background: "#334155", borderRadius: 4, height: 8 }}>
        <div style={{ width: `${value * 100}%`, background: color, borderRadius: 4, height: 8, transition: "width 0.5s" }} />
      </div>
    </div>
  );
}

export default function ResultPanel({ result, explanation, loading }) {
  if (loading) return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: 32, border: "1px solid #334155", textAlign: "center", color: "#64748b" }}>
      ⏳ Procesando predicción y generando explicación normativa...
    </div>
  );
  if (!result) return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: 32, border: "1px solid #334155", textAlign: "center", color: "#64748b" }}>
      Completa el formulario y presiona <strong>Predecir Riesgo</strong> para ver los resultados.
    </div>
  );

  const { risk_label, probabilities, model_used, latency_ms, intersection_name } = result;
  const color = RISK_COLORS[risk_label] || "#94a3b8";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Resultado principal */}
      <div style={{ background: RISK_BG[risk_label] || "#1e293b", border: `1px solid ${color}`, borderRadius: 12, padding: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
          <span style={{ fontSize: 32 }}>{RISK_EMOJI[risk_label]}</span>
          <div>
            <div style={{ fontSize: 12, color: "#94a3b8" }}>{intersection_name}</div>
            <div style={{ fontSize: 26, fontWeight: 800, color }}>RIESGO {risk_label.toUpperCase()}</div>
          </div>
          <div style={{ marginLeft: "auto", textAlign: "right" }}>
            <div style={{ fontSize: 11, color: "#64748b" }}>Modelo</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#38bdf8" }}>{model_used?.toUpperCase()}</div>
            <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>{latency_ms} ms</div>
          </div>
        </div>

        {probabilities && (
          <div>
            <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>Probabilidades por clase</div>
            <ProbBar label="Bajo"  value={probabilities.bajo}  color="#22c55e" />
            <ProbBar label="Medio" value={probabilities.medio} color="#f59e0b" />
            <ProbBar label="Alto"  value={probabilities.alto}  color="#ef4444" />
          </div>
        )}
      </div>

      {/* Explicación RAG */}
      {explanation && (
        <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 12, padding: 24 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#38bdf8", marginBottom: 12 }}>📋 Explicación Normativa (RAG)</div>
          <p style={{ fontSize: 14, lineHeight: 1.7, color: "#cbd5e1", margin: "0 0 16px" }}>
            {explanation.explanation}
          </p>
          {explanation.retrieved_documents?.length > 0 && (
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>Documentos recuperados:</div>
              {explanation.retrieved_documents.map((doc, i) => (
                <div key={i} style={{ background: "#0f172a", borderRadius: 8, padding: "10px 14px", marginBottom: 8, borderLeft: "3px solid #0284c7" }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#38bdf8" }}>{doc.title}</div>
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>
                    Similitud: {(doc.similarity * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          )}
          <div style={{ fontSize: 11, color: "#475569", marginTop: 8 }}>
            ⏱ Latencia RAG: {explanation.latency_ms} ms · Tenant: {explanation.tenant_id}
          </div>
        </div>
      )}
    </div>
  );
}
