# Urban Risk Platform 🏙️

Arquitectura empresarial multitenente para predicción y explicación de riesgo urbano en Bogotá.  
Proyecto de grado — Escuela Colombiana de Ingeniería Julio Garavito.

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| ML + RAG | Python 3.11 · FastAPI · scikit-learn · XGBoost · FAISS · sentence-transformers |
| Backend   | Java 17 · Spring Boot 3.2 · H2 (trazabilidad) · WebFlux |
| Frontend  | React 18 · Vite · Nginx |
| Orquesta  | Docker Compose |

---

## Estructura del proyecto

```
urban-risk/
├── ml-service/          # Servicio Python: modelos ML + RAG
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── backend/             # Spring Boot: API gateway + trazabilidad
│   ├── src/
│   ├── pom.xml
│   └── Dockerfile
├── frontend/            # React: UI multitenente
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── data/                # Dataset sintético de Bogotá
│   └── generate_data.py
├── docs/                # Corpus normativo RAG
│   └── generate_corpus.py
└── docker-compose.yml
```

---

## Cómo levantar el proyecto

### Prerrequisitos
- Docker Desktop instalado y corriendo
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone <tu-repo>
cd urban-risk

# 2. Generar los datos (solo la primera vez)
pip install pandas numpy
python data/generate_data.py
python docs/generate_corpus.py

# 3. Levantar todo
docker compose up --build
```

> ⚠️ El ml-service tarda ~2–4 minutos en arrancar la primera vez porque:
> - Descarga el modelo de embeddings (~90 MB)
> - Entrena los 3 modelos ML sobre 11.650 registros
> - Construye el índice FAISS

### Acceder a los servicios

| Servicio | URL |
|----------|-----|
| Frontend React | http://localhost:3000 |
| Backend Spring Boot | http://localhost:8080/api/health |
| ML Service FastAPI | http://localhost:8000/docs |

---

## Endpoints principales

### ML Service (FastAPI)

```
GET  /health          → estado del servicio y modelos
POST /predict         → predicción de riesgo (header: x-tenant-id)
POST /explain         → explicación RAG normativa
GET  /metrics         → métricas de los 3 modelos entrenados
GET  /models          → modelos disponibles y defaults por tenant
```

### Backend (Spring Boot)

```
POST /api/predict     → proxy a ML + guarda trazabilidad
POST /api/explain     → proxy a RAG + guarda trazabilidad
GET  /api/metrics     → métricas de modelos
GET  /api/logs        → últimas 50 consultas (filtro ?tenantId=bogota)
GET  /api/health      → health check backend + ml-service
```

---

## Tenants configurados

| Tenant ID       | Modelo default | Descripción |
|-----------------|---------------|-------------|
| `bogota`        | XGBoost       | Secretaría Distrital de Movilidad de Bogotá |
| `metro_agency`  | Random Forest | Agencia Metropolitana (simulada) |

Para cambiar de tenant, usar el selector en la UI o el header `x-tenant-id` en requests directos.

---

## Ejemplo de uso directo (curl)

```bash
# Predicción
curl -X POST http://localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -H "x-tenant-id: bogota" \
  -d '{
    "intersection_name": "Cra 7 con Calle 26",
    "latitude": 4.6097, "longitude": -74.0817,
    "hour": 8, "day_of_week": 1,
    "vehicle_flow": 1400, "congestion_index": 0.78,
    "accidents_last_12m": 12,
    "climate_condition": 1,
    "intersection_type": 0
  }'

# Explicación RAG
curl -X POST http://localhost:8080/api/explain \
  -H "Content-Type: application/json" \
  -H "x-tenant-id: bogota" \
  -d '{
    "intersection_name": "Cra 7 con Calle 26",
    "risk_label": "alto",
    "congestion_index": 0.78,
    "accidents_last_12m": 12,
    "climate_condition": 1,
    "top_k": 3
  }'
```

---

## Modelos ML entrenados

| Modelo | Accuracy | F1 Macro | Inf. (ms) |
|--------|----------|----------|-----------|
| Random Forest | ~86% | ~0.857 | ~38 |
| XGBoost       | ~88% | ~0.881 | ~22 |
| Red Neuronal  | ~87% | ~0.869 | ~61 |

*(Métricas exactas disponibles en `/api/metrics` tras el arranque)*

---

## Autores

- Vicente Garzon  
- David Sarria  

Universidad Escuela Colombiana de Ingeniería Julio Garavito  
Materia: Arquitectura Empresarial — Prof. Luis Daniel Benavides Navarro
