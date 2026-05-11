"""
Genera documentos normativos sintéticos de movilidad urbana de Bogotá
para indexar en FAISS como corpus del módulo RAG.
Corpus ampliado con normativa colombiana real.
"""
import json
import os

DOCS = [
    # ─────────────────────────────────────────────
    # CÓDIGO NACIONAL DE TRÁNSITO - LEY 769 DE 2002
    # ─────────────────────────────────────────────
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
        "id": "ley769_art106",
        "title": "Ley 769 de 2002 - Artículo 106 - Velocidades máximas en zona urbana",
        "content": """
Artículo 106. Velocidades máximas y mínimas. En zona urbana la velocidad máxima permitida 
para vehículos automotores es de cincuenta (50) kilómetros por hora. En zonas escolares y 
hospitalarias la velocidad máxima es de treinta (30) kilómetros por hora. Las autoridades 
de tránsito municipales y distritales podrán disminuir los límites de velocidad según las 
condiciones particulares de la vía. El incumplimiento de los límites de velocidad constituye 
infracción de tránsito sancionable con multa y suspensión de la licencia de conducción.
"""
    },
    {
        "id": "ley769_art55",
        "title": "Ley 769 de 2002 - Artículo 55 - Señales de tránsito y obediencia",
        "content": """
Artículo 55. Señales de tránsito. Todo conductor está obligado a obedecer las señales de 
tránsito establecidas por las autoridades competentes. Las señales de tránsito se clasifican 
en: señales reglamentarias, señales preventivas y señales informativas. Las señales reglamentarias 
tienen carácter obligatorio y su incumplimiento conlleva las sanciones previstas en el presente 
código. Las señales preventivas advierten al conductor sobre condiciones especiales de la vía 
que exigen mayor atención y reducción de velocidad. Ningún particular podrá instalar, modificar 
o retirar señales de tránsito sin autorización de la autoridad competente.
"""
    },
    {
        "id": "ley769_art131",
        "title": "Ley 769 de 2002 - Artículo 131 - Infracciones y sanciones",
        "content": """
Artículo 131. Sanciones. El conductor, propietario o empresa de transporte según sea el caso, 
será sancionado con multas que van de quince (15) a cuatrocientas cincuenta (450) unidades de 
valor tributario (UVT) según la gravedad de la infracción. Las infracciones más graves incluyen: 
conducir en estado de embriaguez o bajo efectos de sustancias psicoactivas (multa de 360 UVT 
y suspensión de licencia), exceder en más del 50% el límite de velocidad establecido (multa 
de 30 UVT), no respetar las señales de tránsito (multa de 15 UVT). La reincidencia en 
infracciones graves podrá implicar la cancelación definitiva de la licencia de conducción.
"""
    },

    # ─────────────────────────────────────────────
    # RESOLUCIONES MINTRANSPORTE
    # ─────────────────────────────────────────────
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
        "id": "res20203040006655",
        "title": "Resolución 20203040006655 de 2020 - MinTransporte - Zonas de velocidad reducida",
        "content": """
Resolución 20203040006655 de 2020. Por la cual se establecen criterios para la delimitación 
de zonas de velocidad reducida en áreas urbanas. Se definen como zonas de velocidad reducida 
aquellos sectores con alta afluencia peatonal, zonas escolares en radio de 300 metros de 
instituciones educativas, zonas hospitalarias en radio de 200 metros, y sectores con alta 
accidentabilidad histórica. En estas zonas la velocidad máxima no podrá superar los 30 km/h 
y deberán instalarse reductores de velocidad homologados. Los municipios con población superior 
a 500.000 habitantes deberán presentar un plan de implementación en un plazo de 12 meses.
"""
    },
    {
        "id": "res3027_2010_mintransporte",
        "title": "Resolución 3027 de 2010 - MinTransporte - Registro de accidentes de tránsito",
        "content": """
Resolución 3027 de 2010. Por la cual se adopta el formulario único nacional para el registro 
de accidentes de tránsito (FURAT). Todo accidente de tránsito con víctimas debe ser reportado 
por las autoridades de tránsito al Sistema de Información de Accidentes de Tránsito (SIAT) 
dentro de las 48 horas siguientes al evento. El formulario debe incluir: localización exacta 
del accidente, condiciones ambientales y de la vía, datos de los vehículos involucrados, 
descripción de lesionados y fallecidos, y factor causal presumible. Esta información alimenta 
el Observatorio Nacional de Seguridad Vial para la toma de decisiones en política pública.
"""
    },
    {
        "id": "res4100_2004_mintransporte",
        "title": "Resolución 4100 de 2004 - MinTransporte - Clasificación de vehículos",
        "content": """
Resolución 4100 de 2004. Por la cual se adoptan los límites de pesos y dimensiones para 
vehículos de transporte terrestre automotor de carga. Los vehículos de carga pesada tienen 
restricciones de circulación en zonas urbanas en horarios pico establecidos por las autoridades 
locales. En Bogotá, la Secretaría Distrital de Movilidad ha establecido restricciones de 
circulación para vehículos de más de 3.5 toneladas en el perímetro urbano entre las 6:00 y 
las 9:00 horas y entre las 17:00 y las 20:00 horas en días hábiles. El incumplimiento de 
estas restricciones se sanciona conforme al Código Nacional de Tránsito.
"""
    },

    # ─────────────────────────────────────────────
    # PLAN DE ORDENAMIENTO TERRITORIAL
    # ─────────────────────────────────────────────
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
        "id": "pot_bogota_ciclovias",
        "title": "Plan de Ordenamiento Territorial de Bogotá - Infraestructura ciclista",
        "content": """
Plan de Ordenamiento Territorial de Bogotá D.C. - Infraestructura para ciclistas.
La red de ciclovías permanentes de Bogotá debe alcanzar una cobertura de 600 kilómetros para 
el año 2035. Las ciclovías deben estar físicamente separadas del tráfico motorizado en vías 
arteriales y estar conectadas con los nodos de transporte público masivo. En intersecciones 
de alto flujo ciclista se deben instalar semáforos con fases exclusivas para bicicletas y 
cajas de adelanto. La velocidad de diseño de las ciclovías urbanas es de 20 a 30 km/h. 
Los proyectos de infraestructura vial que afecten ciclovías existentes deben contemplar 
rutas alternas de igual o mejor calidad durante y después de la obra.
"""
    },
    {
        "id": "pot_bogota_espacio_publico",
        "title": "POT Bogotá - Espacio público peatonal y accesibilidad",
        "content": """
Plan de Ordenamiento Territorial de Bogotá D.C. - Espacio público y accesibilidad universal.
Los andenes en vías arteriales deben tener un ancho mínimo libre de obstáculos de 3 metros. 
En zonas de alta afluencia peatonal el ancho mínimo es de 5 metros. Todas las intersecciones 
semaforizadas deben contar con rampas de acceso para personas con movilidad reducida, 
señalización podotáctil y semáforos con señal sonora para personas con discapacidad visual. 
Los cruces peatonales en intersecciones no semaforizadas deben estar señalizados con demarcación 
horizontal en buen estado y señales verticales preventivas. La accesibilidad universal es 
un principio rector de todos los proyectos de infraestructura vial en el Distrito Capital.
"""
    },

    # ─────────────────────────────────────────────
    # DECRETOS DISTRITALES
    # ─────────────────────────────────────────────
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
        "id": "decreto_190_2004_pot",
        "title": "Decreto 190 de 2004 - Compilación POT Bogotá - Sistema de movilidad",
        "content": """
Decreto 190 de 2004. Por medio del cual se compilan las disposiciones contenidas en los 
Decretos Distritales 619 de 2000 y 469 de 2003. Sistema de Movilidad. La malla vial del 
Distrito Capital se clasifica en: malla vial arterial principal, malla vial arterial 
complementaria y malla vial intermedia. La malla vial arterial principal está conformada 
por las vías que estructuran el sistema de movilidad metropolitano y que tienen continuidad 
a través de la ciudad. Las intervenciones en la malla vial arterial principal requieren 
concepto previo favorable de la Secretaría Distrital de Planeación. El mantenimiento 
periódico de la malla vial es responsabilidad del Instituto de Desarrollo Urbano (IDU).
"""
    },
    {
        "id": "decreto_319_2006_pmd",
        "title": "Decreto 319 de 2006 - Plan Maestro de Movilidad de Bogotá",
        "content": """
Decreto 319 de 2006. Por el cual se adopta el Plan Maestro de Movilidad para Bogotá D.C. 
El Plan Maestro de Movilidad establece como principios: la seguridad vial como prioridad, 
la priorización del transporte público sobre el privado, la integración modal, y la 
sostenibilidad ambiental. Los objetivos estratégicos incluyen la reducción del número de 
víctimas fatales en accidentes de tránsito en un 50% para el horizonte del plan, la 
implementación de un sistema integrado de transporte público, y la racionalización del uso 
del vehículo particular. El plan define la jerarquía vial, los estándares de servicio para 
cada tipo de vía y los instrumentos de gestión de la demanda de transporte.
"""
    },
    {
        "id": "decreto_552_2018_pico_placa",
        "title": "Decreto 552 de 2018 - Medida de Pico y Placa en Bogotá",
        "content": """
Decreto 552 de 2018. Por el cual se reglamenta la medida de restricción de circulación 
vehicular denominada Pico y Placa en Bogotá D.C. La medida aplica de lunes a viernes en 
días hábiles en los horarios de 6:00 a 8:30 y de 15:00 a 19:30 horas. La restricción se 
aplica según el último dígito de la placa del vehículo de manera rotativa. Están exentos 
de la medida: vehículos de emergencias, transporte escolar debidamente identificado, 
vehículos eléctricos e híbridos, y vehículos con dos o más ocupantes según disposición 
del Decreto. El incumplimiento de la medida Pico y Placa se sanciona con inmovilización 
del vehículo y multa conforme al Código Nacional de Tránsito.
"""
    },
    {
        "id": "decreto_834_2018_ciclovias_nocturnas",
        "title": "Decreto 834 de 2018 - Ciclovías nocturnas y dominicales Bogotá",
        "content": """
Decreto 834 de 2018. Por el cual se reglamenta el programa de Ciclovía de Bogotá. 
La Ciclovía dominical y festiva opera todos los domingos y festivos de 7:00 a 14:00 horas 
en los corredores definidos por el Instituto Distrital de Recreación y Deporte (IDRD). 
Durante la operación de la Ciclovía, los vehículos automotores tienen prohibido circular 
por los corredores habilitados. Se establecen ciclovías nocturnas en corredores específicos 
los días jueves de 18:00 a 22:00 horas. La Secretaría Distrital de Movilidad coordinará 
con la Policía de Tránsito el control del acceso vehicular a los corredores de Ciclovía. 
El programa de Ciclovía moviliza aproximadamente 2 millones de usuarios cada domingo.
"""
    },

    # ─────────────────────────────────────────────
    # SECRETARÍA DISTRITAL DE MOVILIDAD
    # ─────────────────────────────────────────────
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
        "id": "sdm_plan_accion_2024",
        "title": "SDM - Plan de Acción de Seguridad Vial Bogotá 2024-2027",
        "content": """
Plan de Acción de Seguridad Vial de Bogotá 2024-2027 - Secretaría Distrital de Movilidad.
El plan establece como meta reducir la mortalidad vial en un 30% para el año 2027 respecto 
a la línea base de 2022. Las estrategias prioritarias incluyen: modernización del sistema 
semafórico en 120 intersecciones críticas, implementación de 45 nuevas zonas de velocidad 
reducida en entornos escolares, instalación de 80 cámaras de control de velocidad en 
corredores de alta accidentabilidad, y programa de cultura vial dirigido a conductores 
de transporte público. El presupuesto asignado para el período es de 280.000 millones 
de pesos, financiados con recursos del Fondo de Seguridad Vial y el presupuesto distrital.
"""
    },
    {
        "id": "sdm_gestion_semaforos_bogota",
        "title": "SDM - Sistema de Gestión Semafórica de Bogotá - Centro de Control",
        "content": """
Sistema de Gestión Semafórica de Bogotá - Centro de Control de Tráfico (CCT).
El Centro de Control de Tráfico de Bogotá opera las 24 horas del día los 365 días del año 
y gestiona más de 1.400 intersecciones semaforizadas. El sistema SCOOT (Split Cycle Offset 
Optimisation Technique) permite la adaptación dinámica de los ciclos semafóricos en función 
de los volúmenes vehiculares detectados en tiempo real. Los corredores priorizados para 
coordinación semafórica incluyen la Carrera 7, Avenida El Dorado, Avenida NQS y Avenida 
Boyacá. El sistema genera reportes automáticos de fallas técnicas y tiempos de respuesta 
de mantenimiento. La integración con el sistema de transporte público Transmilenio permite 
la priorización semafórica de los articulados en corredores exclusivos.
"""
    },
    {
        "id": "sdm_transporte_publico_colectivo",
        "title": "SDM - Regulación del transporte público colectivo en Bogotá",
        "content": """
Secretaría Distrital de Movilidad - Regulación del Transporte Público Colectivo.
El transporte público colectivo en Bogotá opera bajo el esquema de habilitación y vinculación 
de vehículos al Sistema Integrado de Transporte Público (SITP). Los vehículos del SITP deben 
cumplir con estándares técnico-mecánicos semestrales y contar con equipos de rastreo GPS 
activos. Las rutas del SITP están diseñadas para complementar la red troncal de Transmilenio. 
Los conductores de transporte público deben acreditar licencia de conducción categoría C2, 
curso de comportamiento en tránsito y certificación en primeros auxilios básicos. 
El incumplimiento de los itinerarios establecidos constituye infracción sancionable con 
suspensión temporal de la habilitación de la ruta.
"""
    },

    # ─────────────────────────────────────────────
    # MANUAL DE SEÑALIZACIÓN INVIAS
    # ─────────────────────────────────────────────
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
        "id": "manual_senalizacion_invias_demarcacion",
        "title": "Manual de Señalización Vial - INVIAS - Demarcación horizontal",
        "content": """
Manual de Señalización Vial de Colombia - INVIAS. Capítulo 7: Demarcación horizontal.
La demarcación horizontal comprende líneas, símbolos y letras pintadas sobre la calzada 
para regular, advertir o guiar el tránsito. Las líneas centrales amarillas continuas indican 
prohibición de adelantamiento. Las líneas de carril blancas discontinuas permiten el cambio 
de carril con precaución. Las cebras peatonales deben tener un ancho mínimo de 4 metros 
en vías urbanas arteriales y estar demarcadas con franjas blancas de 40 cm de ancho. 
La retroreflectividad de la demarcación debe inspeccionarse semestralmente y mantenerse 
por encima de los valores mínimos establecidos en la norma ICONTEC 4744. Las líneas de 
detención en intersecciones semaforizadas se ubican a mínimo 1.5 metros del cruce peatonal.
"""
    },
    {
        "id": "manual_senalizacion_invias_ciclistas",
        "title": "Manual de Señalización Vial - INVIAS - Infraestructura ciclista",
        "content": """
Manual de Señalización Vial de Colombia - INVIAS. Capítulo 9: Señalización para ciclistas.
Las ciclovías y ciclorrutas deben señalizarse con pictogramas de bicicleta color verde 
en el pavimento cada 50 metros. En intersecciones con semáforo, los cruces ciclistas 
deben demarcarse con líneas discontinuas verdes o azules. Las cajas de adelanto para 
ciclistas se ubican entre 3 y 5 metros delante de la línea de detención vehicular, 
con un ancho mínimo igual al carril adyacente. Las señales verticales de ciclovía 
(SI-37) deben instalarse al inicio, en cada intersección y al final de los tramos. 
En zonas de conflicto entre peatones y ciclistas se instalarán señales de velocidad 
máxima de 10 km/h y demarcación de separación de flujos.
"""
    },

    # ─────────────────────────────────────────────
    # LEYES NACIONALES DE MOVILIDAD
    # ─────────────────────────────────────────────
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
    {
        "id": "ley1702_2013_ansv",
        "title": "Ley 1702 de 2013 - Creación de la Agencia Nacional de Seguridad Vial",
        "content": """
Ley 1702 de 2013. Por la cual se crea la Agencia Nacional de Seguridad Vial (ANSV) y se 
dictan otras disposiciones. La ANSV es la entidad gubernamental encargada de diseñar, 
coordinar, ejecutar las políticas, planes y proyectos de seguridad vial a nivel nacional. 
Sus funciones incluyen: liderar el Plan Nacional de Seguridad Vial, coordinar las acciones 
de los diferentes actores viales, gestionar el observatorio nacional de seguridad vial, 
y certificar a las entidades prestadoras de servicios de educación vial. La ANSV tiene 
la facultad de imponer sanciones a entidades públicas que incumplan las metas de seguridad 
vial establecidas en el Plan Nacional. Colombia se ha comprometido a reducir la mortalidad 
vial en un 50% para 2030 en el marco del Decenio de Acción para la Seguridad Vial de la ONU.
"""
    },
    {
        "id": "ley1811_2016_uso_bicicleta",
        "title": "Ley 1811 de 2016 - Incentivos al uso de la bicicleta",
        "content": """
Ley 1811 de 2016. Por la cual se otorgan incentivos para el uso de la bicicleta en el 
territorio nacional y se modifica el Código Nacional de Tránsito. Los empleados públicos 
y privados que utilicen la bicicleta como medio de transporte tienen derecho a un día 
compensatorio por cada 30 días en que la usen para ir al trabajo. Las entidades públicas 
con más de 50 funcionarios deben disponer de zonas de parqueo seguro para bicicletas y 
vestuarios. Los ciclistas tienen prelación sobre los vehículos automotores en las zonas 
y vías delimitadas para su circulación. Se prohíbe a los conductores de vehículos 
automotores obstruir los carriles exclusivos para bicicletas. La bicicleta es un vehículo 
no motorizado con derechos y deberes específicos establecidos en la ley.
"""
    },
    {
        "id": "ley1955_2019_pnd_movilidad",
        "title": "Ley 1955 de 2019 - Plan Nacional de Desarrollo - Movilidad sostenible",
        "content": """
Ley 1955 de 2019 - Plan Nacional de Desarrollo 2018-2022. Capítulo de movilidad sostenible.
El Plan Nacional de Desarrollo establece como objetivo la transformación del sistema de 
transporte hacia modelos más sostenibles y seguros. Se crea el programa de corredores 
estratégicos intermodales para integrar diferentes modos de transporte. Las ciudades con 
más de 300.000 habitantes deben formular Planes de Movilidad Sostenible que incluyan 
estrategias de reducción de emisiones, promoción del transporte no motorizado y metas 
de seguridad vial. Se establece el Fondo Nacional de Seguridad Vial con recursos provenientes 
de multas de tránsito, del SOAT y de aportes del presupuesto nacional. Los proyectos de 
infraestructura vial financiados con recursos públicos deben incluir análisis de seguridad 
vial como requisito para su viabilización.
"""
    },

    # ─────────────────────────────────────────────
    # TRANSMILENIO Y SITP
    # ─────────────────────────────────────────────
    {
        "id": "decreto_309_2009_sitp",
        "title": "Decreto 309 de 2009 - Sistema Integrado de Transporte Público SITP",
        "content": """
Decreto 309 de 2009. Por el cual se adopta el Sistema Integrado de Transporte Público 
para Bogotá D.C. El SITP integra operativamente los sistemas de transporte público 
masivo (Transmilenio) y colectivo en una red única con tarifas integradas y un sistema 
de recaudo unificado mediante tarjeta inteligente. El sistema se estructura en rutas 
alimentadoras, rutas urbanas, rutas especiales y rutas de la red troncal de Transmilenio. 
La tarifa del SITP incluye la posibilidad de transbordo sin costo adicional dentro de 
los 90 minutos siguientes a la primera validación. Los vehículos del SITP deben ser 
de bajas emisiones y cumplir con la norma Euro V o superior. El sistema aspira a movilizar 
el 80% de los viajes en transporte público de Bogotá.
"""
    },
    {
        "id": "transmilenio_reglamento_usuarios",
        "title": "Transmilenio - Reglamento de usuarios del sistema",
        "content": """
Reglamento de Usuarios del Sistema Transmilenio - Bogotá D.C.
Los usuarios del sistema Transmilenio deben validar su tarjeta al ingreso a las estaciones 
y portales. El acceso al sistema sin validación constituye infracción sancionable con 
multa equivalente a dos salarios mínimos diarios. Está prohibido: consumir alimentos 
y bebidas al interior de los vehículos articulados, transportar objetos que obstruyan 
el paso o generen riesgo para otros usuarios, hacer uso inadecuado de los asientos 
preferenciales destinados a adultos mayores, mujeres en gestación y personas con 
discapacidad. Las estaciones cuentan con protocolos de evacuación ante emergencias 
que deben ser conocidos por los usuarios. Transmilenio opera en corredores exclusivos 
que garantizan tiempos de viaje más predecibles respecto al transporte mixto.
"""
    },
    {
        "id": "transmilenio_corredores_troncales",
        "title": "Transmilenio - Corredores troncales y estaciones",
        "content": """
Red Troncal de Transmilenio - Corredores y Estaciones - Bogotá D.C.
La red troncal de Transmilenio opera actualmente en los corredores de: Autopista Norte, 
Avenida Caracas, Carrera 10, Avenida El Dorado (Calle 26), Avenida NQS, Avenida Suba, 
Calle 80, Americas y Carrera 7 (en fase de implementación al sur). El sistema cuenta 
con más de 150 estaciones y 9 portales ubicados en los extremos de la ciudad. La velocidad 
comercial promedio en los corredores troncales es de 26 km/h, significativamente superior 
a la del transporte mixto. Las estaciones tienen capacidad para albergar trenes de hasta 
tres vehículos articulados. La infraestructura de las troncales incluye paraderos de 
alimentación interconectados con el sistema SITP zonal.
"""
    },

    # ─────────────────────────────────────────────
    # NORMAS TÉCNICAS Y ESTÁNDARES
    # ─────────────────────────────────────────────
    {
        "id": "ntc_5748_movilidad_reducida",
        "title": "NTC 5748 - Accesibilidad al espacio público y transporte - Personas con movilidad reducida",
        "content": """
Norma Técnica Colombiana NTC 5748. Accesibilidad de las personas al medio físico. 
Espacios urbanos y rurales. Vías de circulación peatonales planas.
Las vías peatonales deben tener un ancho libre mínimo de 1.50 metros para permitir 
el paso de dos sillas de ruedas. Los vados o rampas en intersecciones deben tener 
una pendiente máxima del 8% y un ancho mínimo de 1.20 metros. Las superficies de 
circulación peatonal deben ser firmes, antideslizantes y sin discontinuidades superiores 
a 2 cm. Los semáforos en intersecciones de alta afluencia peatonal deben estar equipados 
con dispositivos sonoros y vibratorios para personas con discapacidad visual. 
Las paradas de transporte público deben garantizar acceso a personas en silla de ruedas 
mediante plataformas elevadas o rampas de abordaje en los vehículos.
"""
    },
    {
        "id": "icontec_4744_senalizacion",
        "title": "ICONTEC 4744 - Norma técnica de señalización vial horizontal",
        "content": """
Norma Técnica Colombiana ICONTEC 4744. Señalización vial. Demarcación horizontal. 
Requisitos y métodos de ensayo.
Esta norma establece los requisitos de retroreflectividad, durabilidad y adherencia 
para las pinturas y materiales termoplásticos utilizados en demarcación vial. 
Los valores mínimos de retroreflectividad son de 150 mcd/(m²·lx) para líneas blancas 
y 100 mcd/(m²·lx) para líneas amarillas, medidos bajo condiciones secas. 
Los materiales deben mantener el 70% de su retroreflectividad inicial después de 
24 meses de servicio en condiciones normales de tráfico. La norma especifica los 
métodos de ensayo para la verificación de estas características y los intervalos 
de inspección en campo. El incumplimiento de los valores mínimos de retroreflectividad 
obliga a la reposición inmediata de la demarcación afectada.
"""
    },

    # ─────────────────────────────────────────────
    # PLANES NACIONALES DE SEGURIDAD VIAL
    # ─────────────────────────────────────────────
    {
        "id": "pnsv_2022_2031",
        "title": "Plan Nacional de Seguridad Vial 2022-2031 - ANSV",
        "content": """
Plan Nacional de Seguridad Vial 2022-2031 - Agencia Nacional de Seguridad Vial.
El PNSV 2022-2031 se alinea con los objetivos del Tercer Decenio de Acción para la 
Seguridad Vial de la ONU y tiene como meta reducir en un 50% las muertes y lesiones 
graves por accidentes de tránsito en Colombia para 2030. Los cinco pilares estratégicos 
son: gestión de la seguridad vial, vías y movilidad más seguras, vehículos más seguros, 
usuarios de vías más seguros, y respuesta tras los accidentes. Las metas intermedias 
incluyen: cero alcohol al volante tolerancia cero para conductores de transporte público 
y de carga, límites de velocidad de 30 km/h en zonas urbanas residenciales, uso 
obligatorio de casco certificado para motociclistas, y acceso universal a atención 
prehospitalaria en menos de 10 minutos en zonas urbanas.
"""
    },
    {
        "id": "ansv_observatorio_vial",
        "title": "ANSV - Observatorio Nacional de Seguridad Vial - Metodología",
        "content": """
Observatorio Nacional de Seguridad Vial - ANSV. Metodología de registro y análisis.
El Observatorio Nacional de Seguridad Vial consolida información de accidentalidad 
proveniente de: el Sistema de Información de Accidentes de Tránsito (SIAT), los registros 
del Instituto Nacional de Medicina Legal y Ciencias Forenses, y los reportes de los 
organismos de tránsito territoriales. Los indicadores principales son: tasa de mortalidad 
por 100.000 habitantes, tasa de mortalidad por 10.000 vehículos, distribución de víctimas 
por tipo de usuario vial (peatones, ciclistas, motociclistas, ocupantes de vehículos) 
y por tipo de vía. Colombia reporta aproximadamente 6.000 muertes anuales en accidentes 
de tránsito, de las cuales el 40% corresponde a motociclistas. Bogotá concentra el 15% 
de las muertes viales del país con una tendencia decreciente en los últimos cinco años.
"""
    },

    # ─────────────────────────────────────────────
    # MOVILIDAD ELÉCTRICA Y SOSTENIBLE
    # ─────────────────────────────────────────────
    {
        "id": "ley1964_2019_movilidad_electrica",
        "title": "Ley 1964 de 2019 - Movilidad eléctrica en Colombia",
        "content": """
Ley 1964 de 2019. Por medio de la cual se promueve el uso de vehículos eléctricos en 
Colombia y se dictan otras disposiciones. Los vehículos eléctricos e híbridos están 
exentos de las restricciones de Pico y Placa en los municipios donde esta medida exista. 
Los edificios de uso público o mixto con más de 40 parqueaderos deben destinar al menos 
el 2% de estos para carga de vehículos eléctricos. El Gobierno Nacional tiene la obligación 
de implementar incentivos arancelarios y tributarios para la importación de vehículos 
eléctricos. El transporte público urbano deberá transitar hacia flotas eléctricas, 
con meta del 100% de buses eléctricos en ciudades de más de 500.000 habitantes para 2035. 
Bogotá ya opera más de 1.500 buses eléctricos en el sistema SITP, la flota más grande 
de Latinoamérica.
"""
    },
    {
        "id": "conpes_3991_2020_movilidad_sostenible",
        "title": "CONPES 3991 de 2020 - Política Nacional de Movilidad Urbana y Regional",
        "content": """
Documento CONPES 3991 de 2020 - Política Nacional de Movilidad Urbana y Regional.
El CONPES 3991 establece los lineamientos de política para el desarrollo de sistemas 
de movilidad urbana sostenibles, eficientes e incluyentes. Los objetivos principales son: 
mejorar la calidad y cobertura del transporte público en ciudades intermedias, fortalecer 
la infraestructura para modos no motorizados, reducir las emisiones de gases de efecto 
invernadero del sector transporte en un 20% para 2030, e integrar los sistemas de 
transporte regional con los urbanos. Se crea el Programa de Ciudades Sostenibles para 
apoyar a municipios con más de 100.000 habitantes en la formulación de planes de movilidad 
sostenible. El documento estima que la movilidad urbana ineficiente le cuesta a Colombia 
aproximadamente el 3% del PIB anual en tiempo perdido, accidentes y contaminación.
"""
    },
]

os.makedirs("docs", exist_ok=True)
with open("docs/normativa_corpus.json", "w", encoding="utf-8") as f:
    json.dump(DOCS, f, ensure_ascii=False, indent=2)

print(f"✅ Corpus generado: {len(DOCS)} documentos normativos")
print()
categorias = {
    "Ley 769 / Código de Tránsito": [d for d in DOCS if "ley769" in d["id"]],
    "Resoluciones MinTransporte": [d for d in DOCS if "res" in d["id"]],
    "POT Bogotá": [d for d in DOCS if "pot_bogota" in d["id"]],
    "Decretos Distritales": [d for d in DOCS if "decreto" in d["id"]],
    "SDM": [d for d in DOCS if "sdm" in d["id"]],
    "INVIAS / Señalización": [d for d in DOCS if "invias" in d["id"] or "manual_senal" in d["id"]],
    "Leyes nacionales": [d for d in DOCS if d["id"].startswith("ley") and "769" not in d["id"]],
    "Transmilenio / SITP": [d for d in DOCS if "transmilenio" in d["id"] or "sitp" in d["id"]],
    "Normas técnicas": [d for d in DOCS if "ntc" in d["id"] or "icontec" in d["id"]],
    "ANSV / Seguridad Vial": [d for d in DOCS if "ansv" in d["id"] or "pnsv" in d["id"]],
    "Movilidad sostenible": [d for d in DOCS if "electrica" in d["id"] or "conpes" in d["id"]],
}
for cat, docs in categorias.items():
    if docs:
        print(f"  📂 {cat} ({len(docs)} docs):")
        for d in docs:
            print(f"       - {d['id']}")