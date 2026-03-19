# Oportunidad: Migrar procesamiento Glue → Lambda

## Contexto actual (datos reales)

El job de AWS Glue ETL (G.1X, 2 workers) procesa ~2M registros en **~9 min** end-to-end incluyendo cold start. El cold start de Glue representa estimativamente 2-4 min de ese total — tiempo en el que el usuario espera sin progreso real.

## Oportunidad

Reemplazar el job de Glue con una **Lambda function** para el parsing del XML de Apple Health.

### Por qué Lambda sigue siendo viable

- Cold start en milisegundos vs. ~2-4 min de Glue ETL
- El script actual ya no usa Spark — es Python puro con `lxml` + `ThreadPoolExecutor`, portable directamente a Lambda
- El parsing real toma ~5-6 min (sin cold start de Glue), dentro del timeout de 15 min de Lambda
- Más barato a este volumen

### Limitaciones a considerar

- **Timeout de 15 min**: usuarios con exports muy grandes (años de datos, >3M registros) podrían acercarse al límite. Necesita validación con casos extremos.
- **Carga del ZIP en memoria**: el script actual hace `obj["Body"].read()` — carga el ZIP completo. Un Lambda de 10 GB RAM lo maneja, pero es un punto a revisar si los exports crecen.
- **Sin Spark**: no es un problema — el script actual no lo usa para el procesamiento real.

## Análisis de Costos

### Glue ETL (estado actual: G.1X, 2 workers)

- DPU por run: 2 workers × 2 DPU = 4 DPU
- Duración: ~8.9 min = 0.148 h
- **Por ejecución**: 4 DPU × 0.148 h × $0.44 = **~$0.26**
- **30 runs/mes (1/día)**: **~$7.83/mes**

### Lambda (10 GB RAM, ~6 min procesamiento real)

- Costo: $0.0000166667/GB-segundo
- Por ejecución: 10 GB × 360 s × $0.0000166667 = **~$0.06**
- **30 runs/mes (1/día)**: **~$1.80/mes**

### Resultado

| | Costo/run | Costo/mes (30 runs) | Cold start |
|---|---|---|---|
| Glue ETL (actual) | $0.26 | $7.83 | ~2-4 min |
| Lambda (propuesto) | $0.06 | $1.80 | <1 seg |

Lambda es **~4x más barato** y elimina el cold start.

## Recomendación

La migración es técnicamente directa (el código Python no depende de Glue/Spark). El principal riesgo es el timeout de 15 min para exports muy grandes. Validar con el export más grande disponible antes de eliminar Glue.

Estrategia sugerida: Lambda como caso principal, Glue como fallback si Lambda supera los 12 min.

## Estado

Oportunidad identificada — no priorizada aún. Revisar cuando el cold start de Glue sea un bloqueante real para la UX, o cuando el volumen de procesamiento aumente.
