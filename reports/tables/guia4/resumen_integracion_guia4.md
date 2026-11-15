# Resumen automático de integración · Guía 4

- EDA_ACC: 1123 municipios y 17 variables, con 0 diferencias en las variables comunes al EDA.
- DANE Cuadro 15 (2024p): 1122 registros municipales válidos de 1131 filas leídas; 9 filas no municipales excluidas.
- Coincidencias DANE–EDA_ACC: 1122; sin valor agregado: 1; solo en DANE: 0.
- La tabla integrada conserva 1123 municipios.
- Variables con más del 10 % de faltantes: crec_anual, parque_liviano, bev_pct_parque.
- La fuente DANE está en miles de millones de COP corrientes, 2024 provisional; cualquier indicador normalizado por población exige verificar el año poblacional de la base de Erika.
- CárgaME se conserva como inventario preliminar y no se considera infraestructura DC pública operativa validada.

## Pendientes antes de un ranking
1. Verificar año de población, compatibilidad de fechas y restricciones de fuentes.
2. Investigar diferencias de DIVIPOLA, incluyendo cambios territoriales.
3. Validar criterios BEV de pasajeros, cobertura de parque liviano y ausencia de crecimiento.
4. Auditar conectores DC, potencia, acceso público, duplicados y geoposiciones en CárgaME.
5. Justificar métricas de accesibilidad, normalización y análisis de sensibilidad con expertos.
