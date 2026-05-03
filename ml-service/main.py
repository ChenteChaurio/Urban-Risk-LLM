"""
ml-service/main.py
Servicio FastAPI: módulo multimodelo (RF, XGBoost, DNN) + módulo RAG con FAISS.
Soporta multitenencia mediante tenant_id en cada petición.
"""

import os, json, time, logging
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
FAISS_INDEX = None
CORPUS_DOCS = []
EMBED_MODEL = None
FEATURES = [
    "hour", "day_of_week", "is_peak_hour", "is_weekend",
    "vehicle_flow", "congestion_index", "accidents_last_12m",
    "climate_condition", "intersection_type"
]
RISK_LABELS = {0: "bajo", 1: "medio", 2: "alto"}
TENANT_MODELS = {
    "bogota":       "xgb",
    "metro_agency": "rf",
}

# ─── Startup ─────────────────────────────────────────────────────────────────
def train_models():
    global MODELS, SCALER, METRICS

    data_path = "/app/data/bogota_intersections.csv"
    if not os.path.exists(data_path):
        logger.warning("Dataset no encontrado, generando datos sintéticos...")
        os.system("python /app/data/generate_data.py")

    df = pd.read_csv(data_path)
    X = df[FEATURES].values
    y = df["risk_label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

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
        hidden_layer_sizes=(128, 64), activation="relu",
        max_iter=200, random_state=42
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
    vehicle_flow: float
    congestion_index: float
    accidents_last_12m: int
    climate_condition: int        # 0=seco 1=lluvia 2=tormenta
    intersection_type: int        # 0=semáforo 1=rotonda 2=sin control
    model_override: Optional[str] = None  # rf | xgb | dnn


class ExplainRequest(BaseModel):
    intersection_name: str
    risk_label: str               # "bajo" | "medio" | "alto"
    congestion_index: float
    accidents_last_12m: int
    climate_condition: int
    top_k: int = 3


# ─── Helpers ─────────────────────────────────────────────────────────────────
def build_features(req: PredictRequest) -> np.ndarray:
    is_peak = 1 if req.hour in [7, 8, 9, 17, 18, 19] else 0
    is_weekend = 1 if req.day_of_week >= 5 else 0
    return np.array([[
        req.hour, req.day_of_week, is_peak, is_weekend,
        req.vehicle_flow, req.congestion_index, req.accidents_last_12m,
        req.climate_condition, req.intersection_type
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

    # Construir query semántica
    climate_map = {0: "clima seco", 1: "condiciones de lluvia", 2: "tormenta"}
    query = (
        f"Intersección de {req.risk_label} riesgo vial con {req.accidents_last_12m} "
        f"accidentes en 12 meses, índice de congestión {req.congestion_index:.2f}, "
        f"{climate_map.get(req.climate_condition, 'condiciones normales')}. "
        f"Normativa aplicable y medidas de intervención."
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
    explanation = _generate_explanation(req, retrieved)

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
    """Genera explicación en lenguaje natural basada en los documentos recuperados."""
    climate_map = {0: "condiciones secas", 1: "lluvia moderada", 2: "tormenta"}
    inter_map   = {0: "intersección semaforizada", 1: "rotonda", 2: "intersección sin control semafórico"}
    climate_str = climate_map.get(req.climate_condition, "condiciones normales")
    inter_str   = inter_map.get(0, "intersección")

    primary_doc = docs[0] if docs else None
    secondary_doc = docs[1] if len(docs) > 1 else None

    if req.risk_label == "alto":
        base = (
            f"La intersección '{req.intersection_name}' ha sido clasificada como de RIESGO ALTO "
            f"debido a que registra {req.accidents_last_12m} incidentes en los últimos 12 meses "
            f"y presenta un índice de congestión de {req.congestion_index:.2f} bajo {climate_str}. "
        )
        if primary_doc:
            base += (
                f"Conforme a lo establecido en '{primary_doc['title']}', esta situación activa "
                f"los protocolos de intervención prioritaria. "
            )
        if secondary_doc:
            base += (
                f"Adicionalmente, '{secondary_doc['title']}' establece que las autoridades "
                f"competentes deben revisar la señalización y evaluar la implementación de "
                f"sistemas semafóricos adaptativos en esta ubicación. "
            )
        base += (
            "Se recomienda incluir esta intersección en el Plan de Intervención Prioritaria "
            "con horizonte de ejecución no mayor a 18 meses."
        )

    elif req.risk_label == "medio":
        base = (
            f"La intersección '{req.intersection_name}' presenta un nivel de RIESGO MEDIO, "
            f"con {req.accidents_last_12m} incidentes registrados en 12 meses e índice de "
            f"congestión de {req.congestion_index:.2f}. "
        )
        if primary_doc:
            base += (
                f"Según '{primary_doc['title']}', esta categoría requiere seguimiento semestral "
                f"y puede requerir medidas de señalización preventiva. "
            )
        base += (
            "Se recomienda monitoreo continuo de los indicadores y revisión de la señalización "
            "existente para prevenir el escalamiento a riesgo alto."
        )

    else:  # bajo
        base = (
            f"La intersección '{req.intersection_name}' se clasifica en RIESGO BAJO, "
            f"con {req.accidents_last_12m} incidentes en 12 meses e índice de congestión "
            f"de {req.congestion_index:.2f} bajo {climate_str}. "
        )
        if primary_doc:
            base += (
                f"De acuerdo con '{primary_doc['title']}', los indicadores se encuentran "
                f"dentro de los rangos operativos normales. "
            )
        base += "No se requiere intervención prioritaria en el período evaluado."

    return base


@app.get("/metrics")
def metrics():
    return {
        "models": METRICS,
        "features": FEATURES,
        "risk_classes": RISK_LABELS,
        "tenant_model_mapping": TENANT_MODELS,
    }


@app.get("/models")
def list_models():
    return {
        "available": list(MODELS.keys()),
        "tenant_defaults": TENANT_MODELS,
    }
