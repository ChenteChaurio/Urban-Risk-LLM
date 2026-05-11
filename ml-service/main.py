"""
ml-service/main.py
Servicio FastAPI: módulo multimodelo (RF, XGBoost, DNN) + módulo RAG con FAISS.
Soporta multitenencia mediante tenant_id en cada petición.
"""

import os, json, time, logging
import requests
from typing import Optional
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ML
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import joblib

# RAG
import faiss
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Globals ────────────────────────────────────────────────────────────────
MODELS = {}          # {"rf": model, "xgb": model, "dnn": model}
SCALER = None
METRICS = {}         # métricas de entrenamiento por modelo
METRICS_META = {}    # info de dataset y distribuciones
FAISS_INDEX = None
CORPUS_DOCS = []
EMBED_MODEL = None
PROCESSED_LOCATIONS = None
FEATURES = [
    "latitude", "longitude",
    "hour", "day_of_week", "is_peak_hour", "is_weekend",
    "severity_local_mean", "accident_rate", "locality_acc_count",
]
RISK_LABELS = {0: "bajo", 1: "medio", 2: "alto"}
TENANT_MODELS = {
    "bogota":       "xgb",
    "metro_agency": "rf",
}

# ─── Startup ─────────────────────────────────────────────────────────────────
def train_models():
    global MODELS, SCALER, METRICS, METRICS_META
    # Usar exclusivamente el dataset histórico de siniestros
    hist_path = "/app/data/historico_siniestros_bogota_d.c_-.csv"
    if not os.path.exists(hist_path):
        raise RuntimeError("Dataset histórico no encontrado en /app/data. Coloca 'historico_siniestros_bogota_d.c_-.csv' en /data.")

    logger.info(f"Cargando histórico de siniestros: {hist_path}")
    df = load_and_preprocess_historico(hist_path)

    # Agregar por ubicación aproximada para facilitar consultas por coordenadas
    global PROCESSED_LOCATIONS
    try:
        grp = df.groupby(["latitude", "longitude"])
        locs = []
        for (lat, lon), g in grp:
            def safe_mean(col):
                return float(g[col].mean()) if col in g.columns else 0.0

            locs.append({
                "latitude": float(lat),
                "longitude": float(lon),
                "accidents_last_12m": int(g["accidents_last_12m"].max()),
                "severity_local_mean": safe_mean("severity_local_mean"),
                "accident_rate": safe_mean("accident_rate"),
                "locality_acc_count": safe_mean("locality_acc_count"),
                "intersection_name": g.get("intersection_name", pd.Series([f"{lat},{lon}"])).mode().iloc[0] if not g.get("intersection_name", pd.Series()).mode().empty else f"{lat},{lon}",
            })
        PROCESSED_LOCATIONS = pd.DataFrame(locs)
        logger.info(f"Ubicaciones procesadas: {len(PROCESSED_LOCATIONS)}")
    except Exception:
        PROCESSED_LOCATIONS = None

    # Mantener solo las FEATURES auténticas
    X_all = df[[c for c in FEATURES if c in df.columns]]
    y_all = df["risk_label"]

    # Split temporal para evitar fuga: entrenar con el pasado, probar con el futuro
    if "dt" not in df.columns:
        raise RuntimeError("Columna 'dt' no disponible para split temporal")

    cutoff = df["dt"].quantile(0.8)
    train_df = df[df["dt"] <= cutoff]
    test_df = df[df["dt"] > cutoff]

    # Fallback si el split temporal deja un set vacío
    if train_df.empty or test_df.empty:
        X = X_all.values
        y = y_all.values
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
    else:
        X_train = train_df[[c for c in FEATURES if c in train_df.columns]].values
        y_train = train_df["risk_label"].values
        X_test = test_df[[c for c in FEATURES if c in test_df.columns]].values
        y_test = test_df["risk_label"].values

    # Guardar info de dataset y distribuciones de clases
    def class_counts(arr):
        vals, counts = np.unique(arr, return_counts=True)
        return {RISK_LABELS[int(v)]: int(c) for v, c in zip(vals, counts)}

    METRICS_META = {
        "dataset_size": int(len(df)),
        "split_type": "temporal_80_20",
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
        "class_dist_train": class_counts(y_train),
        "class_dist_test": class_counts(y_test),
    }

    # Balanceo SMOTE
    sm = SMOTE(random_state=42)
    X_train_bal, y_train_bal = sm.fit_resample(X_train, y_train)

    # Escaler para DNN
    SCALER = StandardScaler()
    X_train_sc = SCALER.fit_transform(X_train_bal)
    X_test_sc  = SCALER.transform(X_test)

    def eval_model(model, Xtr, Xte):
        model.fit(Xtr, y_train_bal)
        preds = model.predict(Xte)
        rep = classification_report(y_test, preds, output_dict=True)
        return model, {
            "accuracy":  round(rep["accuracy"], 4),
            "f1_macro":  round(f1_score(y_test, preds, average="macro"), 4),
            "precision": round(rep["macro avg"]["precision"], 4),
            "recall":    round(rep["macro avg"]["recall"], 4),
            "per_class": {
                "bajo":  {"precision": round(rep["0"]["precision"],3), "recall": round(rep["0"]["recall"],3), "f1": round(rep["0"]["f1-score"],3)},
                "medio": {"precision": round(rep["1"]["precision"],3), "recall": round(rep["1"]["recall"],3), "f1": round(rep["1"]["f1-score"],3)},
                "alto":  {"precision": round(rep["2"]["precision"],3), "recall": round(rep["2"]["recall"],3), "f1": round(rep["2"]["f1-score"],3)},
            }
        }

    logger.info("Entrenando Random Forest...")
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    MODELS["rf"], METRICS["rf"] = eval_model(rf, X_train_bal, X_test)

    logger.info("Entrenando XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        use_label_encoder=False, eval_metric="mlogloss",
        random_state=42, n_jobs=-1
    )
    MODELS["xgb"], METRICS["xgb"] = eval_model(xgb_model, X_train_bal, X_test)

    logger.info("Entrenando Red Neuronal...")
    dnn = MLPClassifier(
        hidden_layer_sizes=(96, 48), activation="relu",
        max_iter=100, early_stopping=True, n_iter_no_change=10,
        random_state=42
    )
    MODELS["dnn"], METRICS["dnn"] = eval_model(dnn, X_train_sc, X_test_sc)

    logger.info("✅ Todos los modelos entrenados")
    for name, m in METRICS.items():
        logger.info(f"  {name}: accuracy={m['accuracy']} f1={m['f1_macro']}")


def build_rag_index():
    global FAISS_INDEX, CORPUS_DOCS, EMBED_MODEL

    corpus_path = "/app/docs/normativa_corpus.json"
    if not os.path.exists(corpus_path):
        logger.warning("Corpus no encontrado, generando...")
        os.system("python /app/docs/generate_corpus.py")

    with open(corpus_path, encoding="utf-8") as f:
        CORPUS_DOCS = json.load(f)

    logger.info("Cargando modelo de embeddings...")
    EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [d["title"] + " " + d["content"] for d in CORPUS_DOCS]
    logger.info(f"Vectorizando {len(texts)} documentos normativos...")
    embeddings = EMBED_MODEL.encode(texts, convert_to_numpy=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    dim = embeddings.shape[1]
    FAISS_INDEX = faiss.IndexFlatIP(dim)
    FAISS_INDEX.add(embeddings.astype(np.float32))
    logger.info(f"✅ Índice FAISS construido: {FAISS_INDEX.ntotal} vectores (dim={dim})")


def compute_features_for_coords(lat: float, lon: float, radius_m: int = 200) -> dict:
    """Devuelve features históricas agregadas cerca de lat/lon. Retorna campos reales del histórico."""
    global PROCESSED_LOCATIONS
    if PROCESSED_LOCATIONS is None or PROCESSED_LOCATIONS.empty:
        raise HTTPException(status_code=500, detail="Datos históricos no disponibles para consultas por coordenadas")

    df = PROCESSED_LOCATIONS.copy()
    # distancia aproximada en grados
    df["dist_deg"] = ((df["latitude"] - lat) ** 2 + (df["longitude"] - lon) ** 2) ** 0.5
    radius_deg = radius_m / 111000.0
    nearby = df[df["dist_deg"] <= radius_deg]
    if nearby.empty:
        nearest = df.loc[df["dist_deg"].idxmin()]
        return {
            "intersection_name": nearest.get("intersection_name"),
            "latitude": float(nearest.get("latitude")),
            "longitude": float(nearest.get("longitude")),
            "accidents_last_12m": int(nearest.get("accidents_last_12m")),
            "severity_local_mean": float(nearest.get("severity_local_mean", 0.0)),
            "accident_rate": float(nearest.get("accident_rate", 0.0)),
            "locality_acc_count": float(nearest.get("locality_acc_count", 0.0)),
        }

    agg = {
        "intersection_name": nearby["intersection_name"].mode().iloc[0],
        "latitude": float(nearby["latitude"].mean()),
        "longitude": float(nearby["longitude"].mean()),
        "accidents_last_12m": int(nearby["accidents_last_12m"].max()),
        "severity_local_mean": float(nearby["severity_local_mean"].mean()) if "severity_local_mean" in nearby.columns else 0.0,
        "accident_rate": float(nearby["accident_rate"].mean()) if "accident_rate" in nearby.columns else 0.0,
        "locality_acc_count": float(nearby["locality_acc_count"].mean()) if "locality_acc_count" in nearby.columns else 0.0,
    }
    return agg


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando servicio ML + RAG...")
    train_models()
    build_rag_index()
    logger.info("✅ Servicio listo")
    yield


# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Urban Risk ML + RAG Service",
    description="Predicción multimodelo y explicación normativa de riesgo urbano en Bogotá",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Schemas ─────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    intersection_name: str
    latitude: float
    longitude: float
    hour: int
    day_of_week: int
    accidents_last_12m: int
    severity_local_mean: Optional[float] = 0.0
    accident_rate: Optional[float] = 0.0
    locality_acc_count: Optional[float] = 0.0
    # Solo se aceptan campos derivados del histórico; otros datos no están disponibles
    model_override: Optional[str] = None  # rf | xgb | dnn


class ExplainRequest(BaseModel):
    intersection_name: str
    risk_label: str               # "bajo" | "medio" | "alto"
    accidents_last_12m: int
    top_k: int = 3


# ─── Helpers ─────────────────────────────────────────────────────────────────
def build_features(req: PredictRequest) -> np.ndarray:
    is_peak = 1 if req.hour in [7, 8, 9, 17, 18, 19] else 0
    is_weekend = 1 if req.day_of_week >= 5 else 0
    # Solo features derivadas directamente del histórico
    return np.array([[
        req.latitude, req.longitude,
        req.hour, req.day_of_week, is_peak, is_weekend,
        float(req.severity_local_mean or 0.0),
        float(req.accident_rate or 0.0),
        float(req.locality_acc_count or 0.0),
    ]])


def select_model(tenant_id: str, override: Optional[str]) -> str:
    if override and override in MODELS:
        return override
    return TENANT_MODELS.get(tenant_id, "xgb")


# ─── Endpoints ───────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": list(MODELS.keys()),
        "rag_docs": len(CORPUS_DOCS),
        "faiss_vectors": FAISS_INDEX.ntotal if FAISS_INDEX else 0,
    }


@app.post("/predict")
def predict(req: PredictRequest, x_tenant_id: str = Header(default="bogota")):
    t0 = time.time()
    model_key = select_model(x_tenant_id, req.model_override)
    model = MODELS[model_key]

    X = build_features(req)
    X_input = SCALER.transform(X) if model_key == "dnn" else X

    proba = model.predict_proba(X_input)[0]
    predicted_class = int(np.argmax(proba))
    risk_label = RISK_LABELS[predicted_class]

    latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "intersection_name": req.intersection_name,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "risk_label": risk_label,
        "risk_class": predicted_class,
        "probabilities": {
            "bajo":  round(float(proba[0]), 4),
            "medio": round(float(proba[1]), 4),
            "alto":  round(float(proba[2]), 4),
        },
        "model_used": model_key,
        "tenant_id": x_tenant_id,
        "latency_ms": latency_ms,
    }


@app.post("/explain")
def explain(req: ExplainRequest, x_tenant_id: str = Header(default="bogota")):
    t0 = time.time()

    # Construir query semántica basada solo en información histórica disponible
    query = (
        f"Intersección de {req.risk_label} riesgo vial con {req.accidents_last_12m} "
        f"accidentes en 12 meses. Normativa aplicable y medidas de intervención."
    )

    # Recuperación semántica FAISS
    q_vec = EMBED_MODEL.encode([query], convert_to_numpy=True)
    q_vec = q_vec / np.linalg.norm(q_vec)
    scores, indices = FAISS_INDEX.search(q_vec.astype(np.float32), req.top_k)

    retrieved = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(CORPUS_DOCS):
            doc = CORPUS_DOCS[idx]
            retrieved.append({
                "doc_id":    doc["id"],
                "title":     doc["title"],
                "excerpt":   doc["content"].strip()[:400] + "...",
                "similarity": round(float(score), 4),
            })

    # Generación de explicación basada en documentos recuperados
    # Si hay una key de Groq configurada, generar con LLM; si no, usar explicación local
    llm_resp = None
    try:
        prompt_parts = [
            f"Context: Se tiene la predicción de riesgo '{req.risk_label}' para la intersección {req.intersection_name}.\n",
            "Documentos recuperados:\n",
        ]
        # añadir excerpts acotados
        for d in retrieved:
            excerpt = d.get("excerpt", "")
            # limitar excerpt
            if len(excerpt) > 1500:
                excerpt = excerpt[:1500] + "..."
            prompt_parts.append(f"- {d.get('title')}:\n{excerpt}\n")

        prompt_parts.append("\nInstrucciones: Explica brevemente por qué la intersección podría ser de ese nivel de riesgo, cita los fragmentos relevantes y sugiere medidas prácticas de intervención concordes con la normativa citada. Sé conciso (máx. 300 tokens).")
        prompt = "\n".join(prompt_parts)

        llm_resp = call_groq_llm(prompt)
    except Exception:
        llm_resp = None

    explanation = llm_resp if llm_resp else _generate_explanation(req, retrieved)

    latency_ms = round((time.time() - t0) * 1000, 2)
    return {
        "intersection_name":  req.intersection_name,
        "risk_label":         req.risk_label,
        "tenant_id":          x_tenant_id,
        "explanation":        explanation,
        "retrieved_documents": retrieved,
        "latency_ms":         latency_ms,
    }


def _generate_explanation(req: ExplainRequest, docs: list) -> str:
    """Genera explicación usando los fragmentos recuperados (excerpts) y los cita.
    Evita textos completamente hardcodeados y muestra los fragmentos relevantes."""
    header = (
        f"Intersección: {req.intersection_name}. Clasificación: {req.risk_label.upper()}. "
        f"Accidentes últimos 12 meses: {req.accidents_last_12m}.\n\n"
    )

    if not docs:
        return header + "No se encontraron documentos normativos relevantes para esta consulta."

    parts = [header, "Fragmentos normativos relevantes:"]
    for i, d in enumerate(docs, start=1):
        parts.append(f"{i}) {d['title']} (similitud: {d['similarity']}):\n{d['excerpt']}\n")

    parts.append("Sugerencia: revisar los fragmentos anteriores para identificar obligaciones y medidas aplicables a la intersección. Las medidas sugeridas deben contrastarse con los protocolos institucionales.")
    return "\n".join(parts)


def call_groq_llm(prompt: str, max_tokens: int = 400, timeout: int = 15) -> str:
    """Llama a Groq API (https://api.groq.com/openai/v1/chat/completions).
    Si no hay `GROQ_API_KEY` en el entorno, lanza RuntimeError.
    Usa formato compatible con OpenAI (messages).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    api_url = os.environ.get("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    model_name = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY no configurada")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Eres un experto en movilidad urbana y normativa de tránsito. Proporciona explicaciones claras, concisas y basadas en documentos de referencia."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code >= 400:
            logger.error(f"Error llamando a Groq: {resp.status_code} {resp.text}")
            resp.raise_for_status()
        data = resp.json()

        # Extraer texto del formato OpenAI-compatible de xAI
        if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            msg = choice.get("message", {})
            content = msg.get("content", "")
            logger.info("✅ Explicacion generada por Groq")
            return content.strip()

        logger.warning(f"Respuesta inesperada de Groq: {data}")
        return str(data)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error llamando a Groq: {e}")
        raise


def load_and_preprocess_historico(path: str) -> pd.DataFrame:
    """Carga el histórico de siniestros y mapea a las columnas esperadas por el pipeline.
    Produce columnas: hour, day_of_week, is_peak_hour, is_weekend,
    accidents_last_12m, latitude, longitude, intersection_name, risk_label, tenant_id, dt
    """
    logger.info(f"Preprocesando histórico desde {path}")
    df = pd.read_csv(path, parse_dates=["FECHA_HORA_ACC"], dayfirst=False, encoding="utf-8", low_memory=False)

    # Normalizar nombres de columnas con lat/lon y fecha
    if "FECHA_HORA_ACC" in df.columns:
        df["dt"] = pd.to_datetime(df["FECHA_HORA_ACC"], errors="coerce")
    elif "FECHA_OCURRENCIA_ACC" in df.columns:
        df["dt"] = pd.to_datetime(df["FECHA_OCURRENCIA_ACC"], errors="coerce")
    else:
        df["dt"] = pd.to_datetime(df.iloc[:,0], errors="coerce")

    df = df.dropna(subset=["dt"]) 
    # lat/lon columns may be named LATITUD/LONGITUD or Y/X
    lat_col = "LATITUD" if "LATITUD" in df.columns else ("Y" if "Y" in df.columns else None)
    lon_col = "LONGITUD" if "LONGITUD" in df.columns else ("X" if "X" in df.columns else None)

    if not lat_col or not lon_col:
        raise RuntimeError("No se encontraron columnas de latitud/longitud en el histórico")

    df["latitude"] = pd.to_numeric(df[lat_col], errors="coerce")
    df["longitude"] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    # Agrupar por ubicación aproximada (3 decimales) para contar accidentes por punto
    df["lat_r"] = df["latitude"].round(3)
    df["lon_r"] = df["longitude"].round(3)

    # Ordenar por fecha para conteos temporales
    df = df.sort_values("dt")

    # Para cada fila, contar accidentes en los 365 días anteriores y posteriores en la misma ubicación
    df["accidents_last_12m"] = 0
    df["accidents_next_12m"] = 0
    groups = df.groupby(["lat_r", "lon_r"])
    out_rows = []
    for (lat_r, lon_r), grp in groups:
        grp = grp.copy()
        grp = grp.sort_values("dt")
        past_counts = []
        future_counts = []
        for idx, cur in grp.iterrows():
            window_start = cur["dt"] - pd.Timedelta(days=365)
            window_end = cur["dt"] + pd.Timedelta(days=365)
            cnt_past = grp[(grp["dt"] >= window_start) & (grp["dt"] < cur["dt"])].shape[0]
            cnt_future = grp[(grp["dt"] > cur["dt"]) & (grp["dt"] <= window_end)].shape[0]
            past_counts.append(cnt_past)
            future_counts.append(cnt_future)
        grp["accidents_last_12m"] = past_counts
        grp["accidents_next_12m"] = future_counts
        out_rows.append(grp)

    df_proc = pd.concat(out_rows, ignore_index=True)

    # Features time-based
    df_proc["hour"] = df_proc["dt"].dt.hour
    df_proc["day_of_week"] = df_proc["dt"].dt.weekday
    df_proc["is_peak_hour"] = df_proc["hour"].isin([7,8,9,17,18,19]).astype(int)
    df_proc["is_weekend"] = df_proc["day_of_week"].isin([5,6]).astype(int)

    # No inventamos features que no estén en el histórico.
    max_cnt_future = max(1, df_proc["accidents_next_12m"].max())

    # Severidad (GRAVEDAD) a score numerico
    if "GRAVEDAD" in df_proc.columns:
        def severity_score(val: str) -> float:
            s = str(val).upper()
            if "MUER" in s:
                return 2.0
            if "HER" in s:
                return 1.0
            return 0.0
        df_proc["severity_score_raw"] = df_proc["GRAVEDAD"].apply(severity_score)
    else:
        df_proc["severity_score_raw"] = 0.0

    # Estadisticas locales por ubicacion aproximada
    loc_grp = df_proc.groupby(["lat_r", "lon_r"], as_index=False)
    df_proc["severity_local_mean"] = loc_grp["severity_score_raw"].transform("mean")
    df_proc["loc_total_acc"] = loc_grp["accidents_last_12m"].transform("count")
    df_proc["accident_rate"] = (df_proc["accidents_last_12m"] + 1) / (df_proc["loc_total_acc"] + 1)

    # Conteo por localidad (frecuencia total por localidad)
    if "LOCALIDAD" in df_proc.columns:
        loc_counts = df_proc["LOCALIDAD"].value_counts()
        df_proc["locality_acc_count"] = df_proc["LOCALIDAD"].map(loc_counts).fillna(0.0)
    else:
        df_proc["locality_acc_count"] = 0.0

    # intersection name from DIRECCION or FORMULARIO
    if "DIRECCION" in df_proc.columns:
        df_proc["intersection_name"] = df_proc["DIRECCION"].astype(str)
    elif "FORMULARIO" in df_proc.columns:
        df_proc["intersection_name"] = df_proc["FORMULARIO"].astype(str)
    else:
        df_proc["intersection_name"] = (df_proc["lat_r"].astype(str) + "," + df_proc["lon_r"].astype(str))
    # risk_label: discretizar en base a accidentes en los 12 meses futuros (balanceado)
    target = df_proc["accidents_next_12m"]
    if target.nunique() >= 3:
        try:
            df_proc["risk_label"] = pd.qcut(target, q=3, labels=[0, 1, 2]).astype(int)
        except ValueError:
            df_proc["risk_label"] = pd.cut(target, bins=[-1, 0, 2, target.max()], labels=[0, 1, 2]).astype(int)
    else:
        df_proc["risk_label"] = pd.cut(target, bins=[-1, 0, 2, target.max()], labels=[0, 1, 2]).astype(int)
    df_proc["tenant_id"] = "bogota"

    # Seleccionar columnas necesarias (solo las que existen y son auténticas)
    cols_needed = [
        "intersection_name", "latitude", "longitude",
        "hour", "day_of_week", "is_peak_hour", "is_weekend",
        "accidents_last_12m", "severity_local_mean", "accident_rate", "locality_acc_count",
        "risk_label", "tenant_id", "dt"
    ]
    return df_proc[[c for c in cols_needed if c in df_proc.columns]]


@app.get("/metrics")
def metrics():
    return {
        "models": METRICS,
        "features": FEATURES,
        "risk_classes": RISK_LABELS,
        "meta": METRICS_META,
        "tenant_model_mapping": TENANT_MODELS,
    }


@app.get("/models")
def list_models():
    return {
        "available": list(MODELS.keys()),
        "tenant_defaults": TENANT_MODELS,
    }


@app.post("/features")
def features_for_location(payload: dict):
    """POST /features
    Body: { "latitude": float, "longitude": float, "radius_m": int (optional) }
    Returns computed features from historical dataset for that location.
    """
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    radius = int(payload.get("radius_m", 200))
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="'latitude' and 'longitude' required")

    features = compute_features_for_coords(float(lat), float(lon), radius)
    return features
