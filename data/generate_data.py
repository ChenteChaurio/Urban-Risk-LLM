import pandas as pd
import numpy as np
import os

np.random.seed(42)

INTERSECTIONS = [
    ("Cra 7 con Calle 26", 4.6097, -74.0817),
    ("Calle 100 con Autopista Norte", 4.6869, -74.0444),
    ("Av. Eldorado con Cra 30", 4.6476, -74.1024),
    ("Cra 15 con Calle 72", 4.6599, -74.0569),
    ("Calle 80 con Av. Boyaca", 4.6986, -74.1107),
    ("Cra 7 con Calle 45", 4.6359, -74.0644),
    ("Av. Caracas con Calle 53", 4.6427, -74.0737),
    ("Cra 11 con Calle 93", 4.6769, -74.0503),
    ("Calle 170 con Cra 7", 4.7534, -74.0444),
    ("Av. 68 con Calle 26", 4.6073, -74.1099),
    ("Cra 30 con Calle 45", 4.6363, -74.1017),
    ("Calle 13 con Cra 50", 4.6027, -74.1103),
    ("Av. Suba con Cra 91", 4.7241, -74.0912),
    ("Cra 7 con Calle 116", 4.6986, -74.0431),
    ("Calle 63 con Av. Caracas", 4.6516, -74.0737),
    ("Av. Boyaca con Calle 80", 4.6989, -74.1107),
    ("Cra 19 con Calle 100", 4.6869, -74.0656),
    ("Calle 26 con Cra 50", 4.6084, -74.1100),
    ("Av. Ciudad de Cali con Calle 80", 4.6979, -74.1281),
    ("Cra 7 con Calle 32", 4.6195, -74.0763),
]

hour_probs = np.array([0.01,0.01,0.01,0.01,0.02,0.04,0.07,0.08,0.08,0.06,
                       0.05,0.05,0.06,0.05,0.05,0.06,0.08,0.08,0.06,0.04,
                       0.03,0.02,0.02,0.01], dtype=float)
hour_probs /= hour_probs.sum()

N = 11650
records = []

for i in range(N):
    inter = INTERSECTIONS[i % len(INTERSECTIONS)]
    hour = int(np.random.choice(range(24), p=hour_probs))
    day = int(np.random.randint(0, 7))
    is_peak = 1 if hour in [7,8,9,17,18,19] else 0
    is_weekend = 1 if day >= 5 else 0

    flow = float(np.clip(np.random.normal(1200 if is_peak else 600, 300 if is_peak else 200), 50, 5000))
    congestion = float(np.clip(0.4*is_peak + 0.2*(1-is_weekend) + np.random.normal(0,0.15), 0, 1))
    accidents = int(np.random.negative_binomial(2, 0.3 if congestion > 0.6 else 0.6))
    climate = int(np.random.choice([0,1,2], p=[0.6,0.3,0.1]))
    inter_type = int(np.random.choice([0,1,2], p=[0.5,0.3,0.2]))

    risk_score = (0.35*congestion + 0.30*min(1.0, accidents/20) +
                  0.15*(climate/2) + 0.10*(inter_type/2) + 0.10*is_peak)
    risk = 0 if risk_score < 0.33 else (1 if risk_score < 0.60 else 2)

    records.append({
        "intersection_name": inter[0],
        "latitude": inter[1] + np.random.normal(0, 0.001),
        "longitude": inter[2] + np.random.normal(0, 0.001),
        "hour": hour, "day_of_week": day,
        "is_peak_hour": is_peak, "is_weekend": is_weekend,
        "vehicle_flow": round(flow, 1),
        "congestion_index": round(congestion, 3),
        "accidents_last_12m": accidents,
        "climate_condition": climate,
        "intersection_type": inter_type,
        "risk_label": risk,
        "tenant_id": "bogota" if i % 3 != 0 else "metro_agency",
    })

os.makedirs("data", exist_ok=True)
df = pd.DataFrame(records)
df.to_csv("data/bogota_intersections.csv", index=False)
print(f"Dataset generado: {len(df)} registros")
print(df["risk_label"].value_counts().to_string())
