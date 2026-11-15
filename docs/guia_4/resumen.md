# Resumen automático (datos reales)

Último año completo usado para crecimiento anual: 2025 (el año en curso es parcial y no se compara)

## Bitácora
- RUNT: Duplicados exactos eliminados: 0
- RUNT: Cantidades negativas -> NaN (no se imputan, se reportan): 0
- RUNT: Filas con cantidad > 20,000 (imposible por fila) -> NaN para revisión manual: 0
- RUNT: Filas con DIVIPOLA fuera del catálogo (excluidas): 0

## Indicadores
Universo de exploración: 154 de 1123 municipios (con al menos un eléctrico)
Municipios con todos los indicadores: 79

|                    |   count |   mean |   50% |   faltantes_% | cumple_B2   |
|:-------------------|--------:|-------:|------:|--------------:|:------------|
| bev_por_100k       |     154 |  84.44 | 11.77 |           0   | True        |
| bev_pct_parque     |     154 |   0.55 |  0.12 |           0   | True        |
| matr_anio_por_100k |     154 |  25.2  |  3.05 |           0   | True        |
| crec_anual         |      79 |   2.44 |  1    |          48.7 | False       |

Pares con |rho| > 0.8: [('bev_por_100k', 'matr_anio_por_100k', np.float64(0.85))]

VIF:
|                    |     0 |
|:-------------------|------:|
| bev_por_100k       | 16.51 |
| bev_pct_parque     |  1.83 |
| matr_anio_por_100k | 14.66 |
| crec_anual         |  1.16 |

Varianza acumulada PCA: [0.529, 0.793, 0.992, 1.0]

Clusters (k, silueta, cumple >=0,25): (2, np.float64(0.741), np.True_)

Spearman índice ingenuo vs B-1: 0.833
