import { useEffect, useState } from "react";

const MODEL_NAMES = { rf: "Random Forest", xgb: "XGBoost", dnn: "Red Neuronal" };
const MODEL_DESC  = {
  rf:  "200 árboles · max_depth=12 · SMOTE balanceado",
  xgb: "200 estimadores · lr=0.1 · max_depth=6 · SMOTE",
  dnn: "MLP (96→48) · ReLU · early stopping · datos escalados",
};

function MetricCard({ name, data }) {
  const bar = (val) => (
    <div style={{ background: "#0f172a", borderRadius: 4, height: 6, marginTop: 3 }}>
      <div style={{ width: `${val * 100}%`, background: "#0284c7", borderRadius: 4, height: 6 }} />
    </div>
  );

  return (
    <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 12, padding: 20 }}>
      <div style={{ fontSize: 15, fontWeight: 700, color: "#38bdf8", marginBottom: 4 }}>{MODEL_NAMES[name] || name}</div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 16 }}>{MODEL_DESC[name]}</div>

      {[["Accuracy", data.accuracy], ["F1 Macro", data.f1_macro], ["Precision", data.precision], ["Recall", data.recall]].map(([label, val]) => (
        <div key={label} style={{ marginBottom: 10 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#94a3b8" }}>
            <span>{label}</span><span style={{ fontWeight: 700, color: "#f1f5f9" }}>{(val * 100).toFixed(1)}%</span>
          </div>
          {bar(val)}
        </div>
      ))}

      {data.per_class && (
        <div style={{ marginTop: 16, borderTop: "1px solid #334155", paddingTop: 12 }}>
          <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }}>F1 por clase</div>
          {Object.entries(data.per_class).map(([cls, m]) => (
            <div key={cls} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
              <span style={{ color: cls === "bajo" ? "#22c55e" : cls === "medio" ? "#f59e0b" : "#ef4444" }}>
                {cls.charAt(0).toUpperCase() + cls.slice(1)}
              </span>
              <span style={{ color: "#94a3b8" }}>P:{m.precision} R:{m.recall} F1:{m.f1}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function MetricsPanel({ api }) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    fetch(`${api}/metrics`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [api]);

  if (loading) return <div style={{ color: "#64748b", padding: 32 }}>Cargando métricas...</div>;
  if (error)   return <div style={{ color: "#ef4444", padding: 32 }}>Error: {error}</div>;

  return (
    <div>
      <h2 style={{ color: "#f1f5f9", marginBottom: 8 }}>📊 Métricas de Modelos Entrenados</h2>
      <p style={{ color: "#64748b", fontSize: 13, marginBottom: 24 }}>
        Dataset: {data?.meta?.dataset_size ?? "?"} registros · Split {data?.meta?.split_type ?? "?"} · Balanceo SMOTE
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
        {data?.models && Object.entries(data.models).map(([name, m]) => (
          <MetricCard key={name} name={name} data={m} />
        ))}
      </div>

      {data?.meta && (
        <div style={{ marginTop: 16, background: "#1e293b", border: "1px solid #334155", borderRadius: 12, padding: 20 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#38bdf8", marginBottom: 12 }}>Distribución por clase</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16, fontSize: 12, color: "#94a3b8" }}>
            <div>
              <div style={{ color: "#64748b", marginBottom: 6 }}>Train</div>
              {Object.entries(data.meta.class_dist_train || {}).map(([k, v]) => (
                <div key={`train-${k}`}>{k}: {v}</div>
              ))}
            </div>
            <div>
              <div style={{ color: "#64748b", marginBottom: 6 }}>Test</div>
              {Object.entries(data.meta.class_dist_test || {}).map(([k, v]) => (
                <div key={`test-${k}`}>{k}: {v}</div>
              ))}
            </div>
          </div>
        </div>
      )}

      {data?.features && (
        <div style={{ marginTop: 24, background: "#1e293b", border: "1px solid #334155", borderRadius: 12, padding: 20 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#38bdf8", marginBottom: 12 }}>Variables de entrada</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {data.features.map(f => (
              <span key={f} style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 6, padding: "4px 10px", fontSize: 12, color: "#94a3b8" }}>
                {f}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
