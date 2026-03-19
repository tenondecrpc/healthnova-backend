# Oportunidad: Migrar procesamiento Glue → Lambda

## Problema actual

El job de AWS Glue tiene un cold start de **2-5 minutos** cada vez que se activa (cada upload de un export de Apple Health). Esto introduce una latencia significativa en el flujo de procesamiento.

Intentar reducir la latencia bajando los DPUs al mínimo (2) empeora el rendimiento: el procesamiento pasa de ~1 min a ~30 min por la falta de paralelismo.

## Oportunidad

Reemplazar el job de Glue con una **Lambda function** para el parsing del XML de Apple Health.

### Por qué Lambda funciona aquí

- Cold start en milisegundos vs. 2-5 min de Glue
- Los exports de Apple Health típicos son 50-500 MB — manejable con Lambda de 3 GB RAM y 15 min de timeout
- El diseño ya contempla streaming XML para archivos grandes (no se carga todo en memoria)
- Más barato para este volumen de procesamiento

### Limitaciones a considerar

- **Timeout de 15 min**: exports muy grandes o usuarios con años de datos podrían superar el límite
- **Memoria máxima 10 GB**: si el XML descomprimido excede esto, Lambda no es viable
- **Sin Spark**: transformaciones que requieran joins distribuidos seguirían necesitando Glue o similar

## Análisis de Costos

### Glue (estado actual: 1 DPU)
- **Costo por DPU-hora**: $0.44
- **Por ejecución** (2-5 min): $0.015 - $0.037
- **Supuesto**: 50 uploads/día → ~$0.75 - $1.85 / día (~$23-55 / mes)

### Lambda (3 GB RAM, 10 min promedio)
- **Costo**: $0.0000166667 por GB-segundo
- **Por ejecución** (10 min): 3 GB × 600 s = $0.03 / ejecución
- **Por 50 uploads/día**: $1.50 / día (~$45 / mes)

### Resultado
- **Glue actual**: ~$23-55 / mes (dependiendo de volumen)
- **Lambda propuesto**: ~$45 / mes
- **Diferencia**: Muy similar en costo, pero Lambda elimina 2-5 min de cold start por upload

### Trade-off
El costo es prácticamente equivalente. La ventaja de Lambda es la **reducción de latencia** (cold start de 2-5 min → <1 seg), lo cual mejora significativamente la UX. El costo operacional no es un diferenciador.

## Recomendación

Para la mayoría de usuarios, Lambda es suficiente. Si se identifican exports que superen los límites, se puede implementar una estrategia híbrida: Lambda para el caso común, Glue como fallback para archivos grandes.

## Estado

Oportunidad identificada — no priorizada aún. Revisar cuando el cold start de Glue sea un bloqueante real para la experiencia del usuario.
