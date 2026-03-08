# Ejemplos Prácticos de OpenSpec

Esta guía contiene ejemplos reales de cómo usar OpenSpec en diferentes escenarios.

## Ejemplo 1: Agregar una Nueva API Endpoint

### Contexto
Necesitas agregar un endpoint REST para obtener el perfil de usuario.

### Flujo Completo

```
Usuario: /opsx:propose agregar-endpoint-perfil-usuario

Claude: Creando cambio: agregar-endpoint-perfil-usuario

[Genera proposal.md]
# Propuesta: Agregar Endpoint de Perfil de Usuario

## Objetivo
Crear un endpoint GET /api/users/{id}/profile que retorne información del perfil.

## Por qué
Los clientes móviles necesitan obtener datos del perfil para mostrar en la UI.

## Alcance
- Endpoint GET /api/users/{id}/profile
- Autenticación requerida
- Retorna: nombre, email, avatar, fecha de registro

## No-objetivos
- Edición de perfil (será otro cambio)
- Perfiles públicos vs privados

[Genera design.md]
# Diseño: Endpoint de Perfil de Usuario

## Arquitectura
```
Cliente → API Gateway → Lambda (getUserProfile) → DynamoDB
```

## Decisiones Técnicas
- Usar Lambda existente en lib/lambda/user/
- Tabla DynamoDB: Users
- Respuesta en formato JSON estándar
- Cache con TTL de 5 minutos

## Seguridad
- Validar JWT token
- Usuario solo puede ver su propio perfil
- Rate limiting: 100 req/min

[Genera specs/user-profile/spec.md]
# Especificación: Perfil de Usuario

## Endpoint
GET /api/users/{id}/profile

## Autenticación
Bearer token requerido

## Respuesta Exitosa (200)
```json
{
  "id": "user-123",
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "avatar": "https://...",
  "registeredAt": "2026-01-15T10:30:00Z"
}
```

## Errores
- 401: Token inválido o expirado
- 403: Usuario intenta acceder a perfil ajeno
- 404: Usuario no existe
- 429: Rate limit excedido

[Genera tasks.md]
# Tareas: Agregar Endpoint de Perfil de Usuario

- [ ] Crear función Lambda getUserProfile en src/lambda/user/get-profile/
- [ ] Agregar validación de JWT en la función
- [ ] Implementar query a DynamoDB para obtener datos
- [ ] Agregar endpoint en lib/construct/rest-api-construct.ts
- [ ] Configurar políticas IAM para acceso a DynamoDB
- [ ] Agregar tests unitarios para la función Lambda
- [ ] Actualizar documentación de API

✓ Todos los artefactos creados. Listo para implementación.

Usuario: /opsx:apply

Claude: Usando cambio: agregar-endpoint-perfil-usuario

Trabajando en tarea 1/7: Crear función Lambda getUserProfile
[Crea src/lambda/user/get-profile/index.py]
✓ Completada

Trabajando en tarea 2/7: Agregar validación de JWT
[Agrega validación en la función]
✓ Completada

[... continúa con todas las tareas ...]

¡Implementación completa! 7/7 tareas completadas.

Usuario: /opsx:archive

Claude: Cambio archivado exitosamente.
```

## Ejemplo 2: Refactorizar Código Existente

### Contexto
El código de autenticación está disperso en múltiples archivos y necesita consolidación.

### Flujo con Exploración

```
Usuario: /opsx:explore el código de autenticación está muy disperso

Claude: Déjame investigar la estructura actual...

[Lee archivos relevantes]

ARQUITECTURA ACTUAL DE AUTH
════════════════════════════════════════════

src/lambda/core/authorizer/index.py
    ├─ Validación JWT (150 líneas)
    ├─ Verificación de permisos (80 líneas)
    └─ Logging (30 líneas)

src/lambda/user/pre-signup/index.py
    └─ Validación de email (duplicado)

src/lambda/user/post-confirmation-signup/index.py
    └─ Creación de sesión (lógica similar a authorizer)

PROBLEMAS IDENTIFICADOS:
1. Lógica de JWT duplicada en 3 lugares
2. No hay capa común de autenticación
3. Tests dispersos y difíciles de mantener

PROPUESTA DE REFACTOR:
```
src/layer/python-common/python/common/
    └── auth/
        ├── jwt_validator.py      # Validación centralizada
        ├── permissions.py        # Lógica de permisos
        └── session.py            # Manejo de sesiones
```

BENEFICIOS:
✓ Código reutilizable
✓ Tests centralizados
✓ Más fácil de mantener
✓ Reduce duplicación en ~200 líneas

¿Quieres que cree una propuesta para este refactor?

Usuario: Sí, créala

Claude: /opsx:propose refactor-auth-layer

[Genera todos los artefactos basados en la exploración]

Usuario: /opsx:apply

[Implementa el refactor paso a paso]
```

## Ejemplo 3: Agregar Feature con Dependencias Externas

### Contexto
Necesitas integrar un servicio de procesamiento de imágenes con AWS Rekognition.

### Flujo Completo

```
Usuario: /opsx:explore integración con rekognition para análisis de imágenes

Claude: Análisis de imágenes con Rekognition. Veamos las opciones...

CAPACIDADES DE REKOGNITION
════════════════════════════════════════════

Detección          Análisis           Comparación
    │                  │                   │
    ▼                  ▼                   ▼
┌─────────┐      ┌─────────┐        ┌─────────┐
│ Objetos │      │Moderación│        │  Caras  │
│ Texto   │      │Contenido │        │Celebrity│
│ Caras   │      │ Adulto   │        │ Match   │
└─────────┘      └─────────┘        └─────────┘

CONSIDERACIONES:
• Costo: $0.001 por imagen (primeras 1M)
• Latencia: ~500ms promedio
• Límites: 15 imágenes/segundo
• Tamaño máximo: 15MB

¿Qué tipo de análisis necesitas?

Usuario: Necesito detectar objetos y moderar contenido inapropiado

Claude: Perfecto. Dos casos de uso claros:

FLUJO PROPUESTO:
```
Usuario sube imagen → S3
    ↓
Lambda trigger → Rekognition (detectLabels + detectModerationLabels)
    ↓
Resultados → DynamoDB
    ↓
Notificación → Usuario (si contenido rechazado)
```

DECISIONES CLAVE:
1. Procesamiento asíncrono (no bloquear upload)
2. Almacenar resultados para auditoría
3. Política de moderación: rechazar si confidence > 80%

¿Listo para crear la propuesta?

Usuario: Sí

Claude: /opsx:propose agregar-analisis-imagenes-rekognition

[Genera artefactos]

proposal.md incluye:
- Integración con Rekognition
- Procesamiento asíncrono
- Políticas de moderación

design.md incluye:
- Arquitectura con S3 triggers
- Configuración de Rekognition
- Manejo de errores y reintentos
- Políticas IAM necesarias

specs/image-analysis/spec.md incluye:
- Tipos de análisis soportados
- Umbrales de confianza
- Formato de resultados
- Casos de rechazo

tasks.md incluye:
- [ ] Agregar política IAM para Rekognition
- [ ] Crear Lambda de procesamiento
- [ ] Configurar S3 trigger
- [ ] Implementar llamadas a Rekognition API
- [ ] Guardar resultados en DynamoDB
- [ ] Agregar notificaciones de rechazo
- [ ] Tests con imágenes de muestra
- [ ] Documentar configuración de Rekognition

Usuario: /opsx:apply

[Implementa todas las tareas con el contexto completo]
```

## Ejemplo 4: Fix de Bug Complejo

### Contexto
Los usuarios reportan que las sesiones expiran aleatoriamente.

### Flujo de Investigación e Implementación

```
Usuario: /opsx:explore las sesiones expiran aleatoriamente

Claude: Bug de sesiones. Déjame investigar...

[Lee código de autenticación y sesiones]

FLUJO ACTUAL DE SESIÓN:
════════════════════════════════════════════

1. Login → JWT generado (exp: 24h)
2. Request → Authorizer valida JWT
3. JWT válido → Permite acceso

[Busca en logs y código]

PROBLEMA ENCONTRADO:
```python
# En src/lambda/core/authorizer/index.py
token_exp = payload['exp']
current_time = datetime.now().timestamp()  # ⚠️ PROBLEMA

if current_time > token_exp:
    raise Exception('Token expired')
```

BUG IDENTIFICADO:
• datetime.now() usa timezone local (UTC en Lambda)
• Algunos tokens se generan con timezone diferente
• Causa expiración prematura o tardía

SOLUCIÓN:
```python
# Usar UTC explícitamente
current_time = datetime.now(timezone.utc).timestamp()
```

IMPACTO:
• Afecta a ~5% de usuarios (diferentes timezones)
• Sesiones pueden expirar hasta 12h antes/después

¿Creo un cambio para fixear esto?

Usuario: Sí, y agrega tests para prevenir regresión

Claude: /opsx:propose fix-sesion-timezone-bug

[Genera artefactos]

proposal.md:
# Fix: Bug de Timezone en Expiración de Sesiones

## Problema
Sesiones expiran incorrectamente debido a comparación de timestamps
sin timezone explícito.

## Solución
Usar datetime.now(timezone.utc) para consistencia.

## Impacto
Afecta ~5% de usuarios. Fix crítico.

design.md:
# Diseño: Fix de Timezone

## Cambios
1. Actualizar authorizer para usar UTC explícito
2. Agregar tests con diferentes timezones
3. Validar tokens existentes no se invaliden

## Consideraciones
- Backward compatible
- No requiere regenerar tokens existentes
- Tests deben cubrir edge cases de timezone

tasks.md:
- [ ] Actualizar datetime.now() a datetime.now(timezone.utc)
- [ ] Agregar tests con múltiples timezones
- [ ] Verificar tokens existentes siguen funcionando
- [ ] Agregar logging de timezone para debugging
- [ ] Documentar uso correcto de timestamps

Usuario: /opsx:apply

Claude: Implementando fix-sesion-timezone-bug

Tarea 1/5: Actualizar datetime.now() a datetime.now(timezone.utc)
[Actualiza código]
✓ Completada

Tarea 2/5: Agregar tests con múltiples timezones
[Crea tests]
✓ Completada

[... continúa ...]

¡Fix completado! 5/5 tareas.

Usuario: /opsx:archive

Claude: Bug fix archivado. Sesiones ahora usan UTC consistentemente.
```

## Ejemplo 5: Feature Grande con Múltiples Cambios

### Contexto
Necesitas implementar un sistema completo de notificaciones (email, SMS, push).

### Estrategia: Dividir en Cambios Pequeños

```
Usuario: /opsx:explore sistema de notificaciones multi-canal

Claude: Sistema de notificaciones es grande. Veamos cómo dividirlo...

ARQUITECTURA PROPUESTA:
════════════════════════════════════════════

┌─────────────────────────────────────────┐
│      Notification Service (Core)        │
├─────────────────────────────────────────┤
│  • Queue (SQS)                          │
│  • Router (por tipo de notificación)   │
│  • Retry logic                          │
│  • Logging/Monitoring                   │
└─────────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Email  │  │  SMS   │  │  Push  │
    │Provider│  │Provider│  │Provider│
    └────────┘  └────────┘  └────────┘

ESTRATEGIA DE IMPLEMENTACIÓN:
Dividir en 4 cambios independientes:

1. notification-core (base + queue)
2. notification-email (provider de email)
3. notification-sms (provider de SMS)
4. notification-push (provider de push)

BENEFICIOS:
✓ Cada cambio es pequeño y manejable
✓ Puedes implementar en paralelo (si hay equipo)
✓ Puedes priorizar (email primero, push después)
✓ Más fácil de revisar y testear

¿Empezamos con el core?

Usuario: Sí, empecemos con el core

Claude: /opsx:propose notification-core

[Genera artefactos solo para el core]

proposal.md:
# Propuesta: Notification Core

## Objetivo
Crear la infraestructura base para sistema de notificaciones.

## Alcance
- Cola SQS para notificaciones
- Router para dirigir a providers
- Retry logic con exponential backoff
- Logging y métricas

## No-objetivos
- Providers específicos (serán cambios separados)
- UI de administración

design.md:
# Diseño: Notification Core

## Componentes
1. SQS Queue: notification-queue
2. Lambda Router: notification-router
3. DynamoDB: notification-logs
4. CloudWatch: métricas

## Flujo
```
Evento → SQS → Router → [Provider Queue]
                  ↓
            Logs/Metrics
```

tasks.md:
- [ ] Crear SQS queue con DLQ
- [ ] Crear Lambda router
- [ ] Implementar retry logic
- [ ] Configurar CloudWatch alarms
- [ ] Agregar tabla DynamoDB para logs
- [ ] Tests de integración

Usuario: /opsx:apply

[Implementa el core]

Usuario: Ahora el provider de email

Claude: /opsx:propose notification-email

[Genera artefactos para email provider]

proposal.md:
# Propuesta: Email Notification Provider

## Objetivo
Implementar provider de email usando SendGrid.

## Dependencias
- Requiere notification-core (ya implementado ✓)

## Alcance
- Integración con SendGrid
- Templates de email
- Tracking de envíos

[... continúa con email provider ...]

[Después de completar email]

Usuario: Ahora SMS

Claude: /opsx:propose notification-sms

[... y así sucesivamente ...]
```

## Ejemplo 6: Actualizar Diseño Durante Implementación

### Contexto
Durante la implementación descubres que el diseño original no funciona.

### Flujo Adaptativo

```
Usuario: /opsx:apply agregar-cache-redis

Claude: Implementando agregar-cache-redis

Tarea 1/5: Instalar dependencia de Redis
✓ Completada

Tarea 2/5: Crear cliente Redis con conexión persistente

[Intenta implementar]

## Implementación Pausada

**Problema encontrado:**
El diseño especifica conexión persistente, pero Lambda
no mantiene conexiones entre invocaciones de forma confiable.

**Opciones:**
1. Usar ElastiCache con VPC (más complejo, más caro)
2. Cambiar a conexión por request (más simple, overhead mínimo)
3. Usar Redis Serverless (AWS MemoryDB Serverless)

**Recomendación:**
Opción 2 es más práctica para Lambda. El overhead de conexión
es ~10ms, aceptable para la mayoría de casos.

¿Actualizar design.md con este enfoque?

Usuario: Sí, actualiza el diseño

Claude: Actualizando design.md...

[Modifica design.md]
```markdown
## Conexión Redis

~~Usar conexión persistente con pool~~

**Actualizado:** Usar conexión por request
- Overhead: ~10ms por request
- Más simple y confiable en Lambda
- No requiere VPC
- Usar Redis Labs o AWS ElastiCache público
```

✓ Diseño actualizado

Continuando con tarea 2/5: Crear cliente Redis por request
[Implementa con nuevo enfoque]
✓ Completada

[... continúa con el resto ...]
```

## Patrones Comunes

### Patrón 1: Explorar → Proponer → Aplicar

Para features nuevas donde no estás seguro del enfoque:

```
/opsx:explore <idea>
[Discusión y exploración]
/opsx:propose <nombre>
/opsx:apply
/opsx:archive
```

### Patrón 2: Proponer Directo → Aplicar

Para features claras donde sabes exactamente qué hacer:

```
/opsx:propose <nombre>
/opsx:apply
/opsx:archive
```

### Patrón 3: Proponer → Revisar → Ajustar → Aplicar

Para features que requieren validación antes de implementar:

```
/opsx:propose <nombre>
[Revisar artefactos generados]
[Ajustar design.md o specs/]
/opsx:apply
/opsx:archive
```

### Patrón 4: Aplicar Parcial → Pausar → Continuar

Para implementaciones largas que necesitas hacer en sesiones:

```
/opsx:apply
[Implementa 3 de 10 tareas]
[Pausa para el día]

[Al día siguiente]
/opsx:apply
[Continúa desde tarea 4]
```

## Consejos por Tipo de Cambio

### API Endpoints
- Siempre incluye autenticación en specs
- Define todos los códigos de error posibles
- Documenta rate limits
- Incluye ejemplos de request/response

### Refactors
- Usa `/opsx:explore` primero para mapear código existente
- Divide en tareas pequeñas para minimizar riesgo
- Incluye tests de regresión
- Documenta qué NO cambia

### Bug Fixes
- Investiga con `/opsx:explore` para entender la causa raíz
- Incluye tests que reproduzcan el bug
- Documenta el impacto en proposal.md
- Considera backward compatibility

### Integraciones Externas
- Explora la API externa primero
- Documenta límites y costos
- Incluye manejo de errores robusto
- Agrega retry logic
- Considera timeouts

### Features Grandes
- Divide en múltiples cambios pequeños
- Implementa el core primero
- Agrega features incrementalmente
- Cada cambio debe ser deployable independientemente

## Conclusión

OpenSpec brilla cuando:
- Usas exploración para ideas complejas
- Divides trabajo grande en cambios pequeños
- Mantienes artefactos actualizados durante implementación
- Archivas cambios completados para mantener el workspace limpio

¡Experimenta con estos patrones y encuentra tu flujo ideal!
