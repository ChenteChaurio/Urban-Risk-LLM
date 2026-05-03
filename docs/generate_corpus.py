"""
Genera documentos normativos sintéticos de movilidad urbana de Bogotá
para indexar en FAISS como corpus del módulo RAG.
"""
import json
import os

DOCS = [
    {
        "id": "ley769_art56",
        "title": "Ley 769 de 2002 - Artículo 56 - Intersecciones de alto riesgo",
        "content": """
Artículo 56. Intersecciones de alto riesgo. Las autoridades de tránsito competentes deberán 
identificar y señalizar debidamente las intersecciones que registren más de diez (10) incidentes 
viales en un período de doce (12) meses consecutivos. Dichas intersecciones serán catalogadas 
como zonas de alto riesgo vial y deberán contar con planes de intervención prioritaria que 
incluyan señalización preventiva, control de velocidad y, cuando sea pertinente, la instalación 
de sistemas semafóricos inteligentes. Las entidades responsables deberán presentar informes 
trimestrales sobre las acciones adoptadas ante los organismos de control competentes.
"""
    },
    {
        "id": "res1885_2015",
        "title": "Resolución 1885 de 2015 - MinTransporte - Semáforos inteligentes",
        "content": """
Resolución 1885 de 2015. Por la cual se establecen los criterios técnicos para la implementación 
de sistemas semafóricos inteligentes en intersecciones urbanas. Las intersecciones con índice de 
congestión superior al percentil 85 de su corredor vial, medido durante franjas horarias pico, 
son candidatas prioritarias para la instalación de controladores adaptativos de señal. Los 
sistemas deben cumplir con los estándares NTCGP 1000:2009 y contar con capacidad de comunicación 
con el Centro de Control de Tráfico. La instalación requiere estudio de factibilidad aprobado 
por la Secretaría Distrital de Movilidad.
"""
    },
    {
        "id": "pot_bogota_movilidad",
        "title": "Plan de Ordenamiento Territorial de Bogotá - Capítulo Movilidad",
        "content": """
Plan de Ordenamiento Territorial de Bogotá D.C. - Componente de Movilidad. 
Las intersecciones del sistema vial arterial principal deben mantener un nivel de servicio C 
o superior durante el 80% de las horas del día hábil. Los corredores que presenten niveles 
de servicio D o E de manera recurrente deberán ser objeto de estudios de capacidad vial y 
propuestas de mejoramiento en el Plan de Movilidad Distrital vigente. La congestión crónica 
en intersecciones de la malla vial arterial constituye un indicador de alerta para la 
actualización del modelo de transporte distrital.
"""
    },
    {
        "id": "decreto_462_seguridad_vial",
        "title": "Decreto 462 - Plan Distrital de Seguridad Vial - Clasificación de riesgo",
        "content": """
Decreto 462 - Plan Distrital de Seguridad Vial de Bogotá. 
La clasificación de riesgo vial en intersecciones se realiza conforme a tres categorías: 
riesgo bajo (menos de 5 incidentes anuales y congestión controlada), riesgo medio (entre 5 
y 10 incidentes anuales o congestión recurrente en horas pico), y riesgo alto (más de 10 
incidentes anuales o congestión severa sostenida). Las intersecciones clasificadas como riesgo 
alto deben ser incluidas en el Plan de Intervención Prioritaria con horizonte de ejecución 
no superior a 18 meses. La Secretaría Distrital de Movilidad actualizará esta clasificación 
de forma semestral.
"""
    },
    {
        "id": "manual_senalizacion_invias",
        "title": "Manual de Señalización Vial - INVIAS - Zonas de riesgo",
        "content": """
Manual de Señalización Vial de Colombia - INVIAS. Capítulo 5: Señalización en zonas de riesgo.
Las intersecciones categorizadas como de riesgo alto deben contar con señales preventivas 
SP-31 (intersección peligrosa) instaladas a mínimo 150 metros de la intersección en cada 
aproximación. En condiciones de baja visibilidad o lluvia intensa, la velocidad máxima 
permitida en estas intersecciones se reduce automáticamente un 30% respecto al límite 
ordinario. Las autoridades de tránsito deberán verificar el estado y visibilidad de la 
señalización en intersecciones de alto riesgo con periodicidad mensual.
"""
    },
    {
        "id": "sdm_protocolo_lluvia",
        "title": "Secretaría Distrital de Movilidad - Protocolo de gestión en clima adverso",
        "content": """
Protocolo de Gestión de Tráfico en Condiciones Climáticas Adversas - SDM Bogotá.
En condiciones de lluvia moderada (categoría 1) el sistema de gestión de tráfico debe activar 
ciclos semafóricos extendidos en intersecciones críticas y emitir alertas preventivas a usuarios. 
En condiciones de tormenta (categoría 2), se activa el protocolo de contingencia que incluye 
despliegue de agentes de tránsito en las 15 intersecciones de mayor riesgo histórico y 
reducción de velocidades máximas en vías arteriales. El índice de congestión en condiciones 
de lluvia intensa puede aumentar hasta un 45% respecto a condiciones normales en las mismas 
franjas horarias.
"""
    },
    {
        "id": "sdm_intersecciones_criticas_2024",
        "title": "SDM - Informe de intersecciones críticas Bogotá 2024",
        "content": """
Informe Anual de Intersecciones Críticas - Secretaría Distrital de Movilidad - Bogotá 2024.
Las intersecciones con mayor índice de siniestralidad en 2024 se concentran en los corredores 
de la Carrera 7, Avenida Caracas y Avenida El Dorado. El 68% de los incidentes registrados 
ocurren en franjas horarias pico (7:00-9:00 y 17:00-19:00). Los factores contribuyentes más 
frecuentes son el exceso de velocidad (34%), la falta de señalización visible (22%) y las 
condiciones climáticas adversas (19%). Las intersecciones sin control semafórico presentan 
una tasa de incidentalidad 2.3 veces superior a las intersecciones semaforizadas.
"""
    },
    {
        "id": "ley1503_cultura_vial",
        "title": "Ley 1503 de 2011 - Cultura vial y responsabilidad institucional",
        "content": """
Ley 1503 de 2011. Por la cual se promueve la formación de hábitos, comportamientos y conductas 
seguros en la vía. Las entidades públicas responsables de la gestión vial tienen la obligación 
de publicar trimestralmente los indicadores de accidentabilidad por intersección y corredor vial. 
La información deberá incluir número de incidentes, tipología, condiciones asociadas y acciones 
de mitigación adoptadas. Esta transparencia informativa es condición para la asignación de 
recursos del Fondo de Seguridad Vial Nacional. Las intersecciones con más de 15 incidentes 
anuales deben ser objeto de auditorías externas de seguridad vial.
"""
    },
]

os.makedirs("docs", exist_ok=True)
with open("docs/normativa_corpus.json", "w", encoding="utf-8") as f:
    json.dump(DOCS, f, ensure_ascii=False, indent=2)

print(f"Corpus generado: {len(DOCS)} documentos normativos")
for d in DOCS:
    print(f"  - {d['id']}: {d['title']}")
