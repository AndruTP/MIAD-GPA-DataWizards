# MIAD-GPA-DataWizards
Proyecto de Analytics para la priorización de mercados de inversión en infraestructura pública de carga para vehículos eléctricos en Colombia.


# MIAD-GPA-DataWizards

## Priorización de mercados de inversión en infraestructura pública de carga para vehículos eléctricos en Colombia

**Universidad de los Andes**  
Maestría en Inteligencia Analítica de Datos (MIAD)  
Curso: Gerencia de Proyectos de Analytics  
Equipo: DataWizards

## 1. Descripción del proyecto

El proyecto busca desarrollar una solución analítica que permita identificar y priorizar ciudades colombianas con condiciones relativamente favorables para realizar estudios de prefactibilidad de inversión en infraestructura pública de carga rápida para vehículos eléctricos.

La propuesta integra información pública sobre demanda potencial, infraestructura de carga existente, accesibilidad territorial y condiciones socioeconómicas.

El resultado esperado es una clasificación de mercados que facilite la comparación de alternativas y apoye las decisiones de un comité de inversiones.

**Alcance:** la solución priorizará mercados para estudios posteriores. No pretende pronosticar la utilización de estaciones de carga ni garantizar la rentabilidad financiera de una inversión.

## 2. Objetivo general

Construir y validar un modelo analítico que permita priorizar ciudades colombianas para estudios de prefactibilidad en infraestructura pública de carga de vehículos eléctricos, utilizando indicadores trazables y resultados interpretables.

## 3. Fuentes de información propuestas

| Dimensión | Fuentes | Información requerida |
|---|---|---|
| Demanda potencial | RUNT, ANDI/Fenalco | Parque automotor, matrículas y evolución de vehículos eléctricos |
| Infraestructura de carga | SIEM/UPME, MinEnergía, Open Charge Map y operadores | Estaciones, conectores, localización y características |
| Contexto socioeconómico | DANE | Población e indicadores económicos territoriales |
| Accesibilidad | OpenStreetMap y cartografía oficial | Redes viales e información geográfica |
| Validación | Expertos y stakeholders | Requerimientos y ponderaciones de criterios |

La inclusión definitiva de cada fuente está condicionada a su disponibilidad, cobertura territorial, calidad, granularidad y condiciones de uso.

## 4. Enfoque metodológico

La solución propuesta contempla:

1. Identificación y caracterización de las fuentes de datos.
2. Evaluación de calidad, limpieza e integración.
3. Análisis exploratorio y construcción de indicadores.
4. Desarrollo de un índice multicriterio para priorización de ciudades.
5. Análisis de sensibilidad de pesos y supuestos.
6. Agrupación de ciudades con características semejantes.
7. Validación y presentación de resultados.

El enfoque principal es multicriterio, complementado por análisis descriptivo y técnicas no supervisadas.

## 5. Organización del repositorio

```text
MIAD-GPA-DataWizards/
├── docs/            # Documentación del proyecto
├── data/
│   ├── raw/         # Datos originales (almacenamiento controlado)
│   ├── processed/   # Datos transformados
│   └── metadata/    # Fuentes y diccionario de datos
├── notebooks/       # Análisis exploratorio y preprocesamiento
├── src/             # Funciones y código reutilizable
├── reports/
│   ├── figures/     # Visualizaciones
│   └── tables/      # Resultados tabulares
├── requirements.txt
├── .gitignore
└── README.md
```

*Esta estructura será implementada progresivamente durante el desarrollo del proyecto.*

## 6. Estado del proyecto

**Fase actual:** Guía 4 — Evaluación de calidad, limpieza y entendimiento de los datos.

Actividades iniciales:

- [ ] Inventariar y descargar las fuentes de información.
- [ ] Verificar cobertura y granularidad de los datos.
- [ ] Construir el diccionario de variables.
- [ ] Evaluar completitud, consistencia, claridad y formato.
- [ ] Documentar y ejecutar los procesos de limpieza.
- [ ] Realizar análisis exploratorio.
- [ ] Evaluar la suficiencia de los datos frente al problema de Analytics.
- [ ] Consolidar el informe ejecutivo y los anexos técnicos.

## 7. Trazabilidad y reproducibilidad

Para cada fuente de información se documentarán, cuando estén disponibles:

- Entidad responsable y URL de origen.
- Fecha de descarga y periodo de referencia.
- Cobertura geográfica y granularidad.
- Variables, unidades y formatos.
- Licencia y condiciones de utilización.
- Transformaciones y decisiones de limpieza.
- Limitaciones identificadas.

Los archivos originales se conservarán sin modificaciones. Los scripts y notebooks documentarán los procesos empleados para obtener los conjuntos de datos utilizados en el análisis.

## 8. Equipo de trabajo

| Integrante | Rol |
|---|---|
| Erica Johana Quintero Duque | Líder del proyecto |
| Andrés Toro Perdigón | Análisis de datos, ETL y calidad |
| Jairo Eduardo Hortúa Borbón | Modelamiento analítico |
| David Ricardo Escobar Velazco | Análisis de negocio y visualización |

**Asesor:** Cristian Segura.

## 9. Herramientas previstas

Python, pandas, NumPy, GeoPandas, scikit-learn, Jupyter Notebook y GitHub.

Para el prototipo se contempla Streamlit.

Las herramientas y dependencias definitivas se documentarán a medida que avance el desarrollo.

## 10. Consideraciones

Este proyecto se desarrolla con fines académicos en el marco de la Maestría en Inteligencia Analítica de Datos de la Universidad de los Andes.

Los resultados analíticos deberán interpretarse teniendo en cuenta la calidad, disponibilidad y limitaciones de las fuentes de información.

La clasificación resultante estará orientada a priorizar estudios de prefactibilidad, no a recomendar inversiones definitivas.
