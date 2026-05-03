const RISK_COLORS = { bajo: "#22c55e", medio: "#f59e0b", alto: "#ef4444" };

// Mapa SVG simplificado de Bogotá con intersecciones conocidas
const INTERSECTIONS_MAP = [
  { name: "Cra 7 / Cl 26",       x: 195, y: 285 },
  { name: "Cl 100 / Aut Norte",  x: 230, y: 120 },
  { name: "Eldorado / Cra 30",   x: 135, y: 220 },
  { name: "Cra 15 / Cl 72",      x: 210, y: 175 },
  { name: "Cl 80 / Av Boyacá",   x: 105, y: 145 },
  { name: "Caracas / Cl 53",     x: 185, y: 200 },
  { name: "Cra 11 / Cl 93",      x: 225, y: 140 },
  { name: "Av Suba / Cra 91",    x: 95,  y: 105 },
];

export default function RiskMap({ result }) {
  // Encontrar la intersección activa
  const activeIdx = result
    ? INTERSECTIONS_MAP.findIndex(i => result.intersection_name?.includes(i.name.split("/")[0].trim()))
    : -1;

  const activeColor = result ? (RISK_COLORS[result.risk_label] || "#38bdf8") : null;

  return (
    <div style={{ background: "#1e293b", borderRadius: 12, border: "1px solid #334155", padding: 16 }}>
      <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 8 }}>🗺️ Mapa de intersecciones — Bogotá D.C.</div>
      <svg viewBox="0 0 340 370" width="100%" style={{ display: "block" }}>
        {/* Fondo */}
        <rect width="340" height="370" fill="#0f172a" rx="8" />

        {/* Vías principales */}
        {/* Carrera 7 */}
        <line x1="195" y1="50" x2="195" y2="330" stroke="#1e3a5f" strokeWidth="3" />
        {/* Autopista Norte */}
        <line x1="230" y1="50" x2="230" y2="200" stroke="#1e3a5f" strokeWidth="3" />
        {/* Av Caracas */}
        <line x1="185" y1="50" x2="185" y2="330" stroke="#1e3a5f" strokeWidth="2" />
        {/* Calle 26 */}
        <line x1="50" y1="285" x2="290" y2="285" stroke="#1e3a5f" strokeWidth="3" />
        {/* Calle 80 */}
        <line x1="50" y1="145" x2="290" y2="145" stroke="#1e3a5f" strokeWidth="2" />
        {/* Calle 100 */}
        <line x1="50" y1="120" x2="290" y2="120" stroke="#1e3a5f" strokeWidth="2" />
        {/* Av El Dorado */}
        <line x1="50" y1="220" x2="220" y2="220" stroke="#1e3a5f" strokeWidth="3" />
        {/* Av Boyacá */}
        <line x1="105" y1="50" x2="105" y2="330" stroke="#1e3a5f" strokeWidth="3" />
        {/* Av Suba */}
        <line x1="50" y1="105" x2="200" y2="105" stroke="#1e3a5f" strokeWidth="2" />

        {/* Labels de vías */}
        <text x="197" y="45" fill="#334155" fontSize="8" textAnchor="middle">Cra 7</text>
        <text x="232" y="45" fill="#334155" fontSize="8" textAnchor="middle">Aut N</text>
        <text x="107" y="45" fill="#334155" fontSize="8" textAnchor="middle">Av Boyacá</text>
        <text x="52" y="284" fill="#334155" fontSize="8">Cl 26</text>
        <text x="52" y="144" fill="#334155" fontSize="8">Cl 80</text>
        <text x="52" y="119" fill="#334155" fontSize="8">Cl 100</text>

        {/* Intersecciones */}
        {INTERSECTIONS_MAP.map((inter, idx) => {
          const isActive = idx === activeIdx;
          const color = isActive ? activeColor : "#334155";
          const r = isActive ? 9 : 5;
          return (
            <g key={idx}>
              {isActive && (
                <circle cx={inter.x} cy={inter.y} r={16} fill={activeColor} opacity={0.15} />
              )}
              <circle cx={inter.x} cy={inter.y} r={r} fill={color} stroke="#0f172a" strokeWidth="1.5" />
              <text x={inter.x + 11} y={inter.y + 4} fill={isActive ? activeColor : "#475569"} fontSize="7.5" fontWeight={isActive ? "bold" : "normal"}>
                {inter.name}
              </text>
            </g>
          );
        })}

        {/* Leyenda */}
        <g transform="translate(14, 335)">
          {[["bajo", "#22c55e"], ["medio", "#f59e0b"], ["alto", "#ef4444"]].map(([label, color], i) => (
            <g key={label} transform={`translate(${i * 90}, 0)`}>
              <circle cx="6" cy="6" r="5" fill={color} />
              <text x="14" y="10" fill="#64748b" fontSize="9">{label}</text>
            </g>
          ))}
        </g>

        {/* Norte */}
        <text x="310" y="30" fill="#334155" fontSize="11" textAnchor="middle">N</text>
        <line x1="310" y1="34" x2="310" y2="48" stroke="#334155" strokeWidth="1.5" />
        <polygon points="310,22 306,34 314,34" fill="#334155" />
      </svg>
    </div>
  );
}
