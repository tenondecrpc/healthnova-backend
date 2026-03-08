# Diagramas y Visualizaciones de OpenSpec

Esta guía visual te ayuda a entender OpenSpec a través de diagramas y flujos.

## Ciclo de Vida de un Cambio

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA OPENSPEC                       │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   EXPLORAR   │  (Opcional)
    │  /opsx:explore│
    └──────┬───────┘
           │ Pensar, investigar, comparar
           ▼
    ┌──────────────┐
    │   PROPONER   │  (Requerido)
    │ /opsx:propose│
    └──────┬───────┘
           │ Genera: proposal.md, design.md, specs/, tasks.md
           ▼
    ┌──────────────┐
    │  IMPLEMENTAR │  (Requerido)
    │  /opsx:apply │
    └──────┬───────┘
           │ Ejecuta tareas una por una
           ▼
    ┌──────────────┐
    │   ARCHIVAR   │  (Requerido)
    │ /opsx:archive│
    └──────┬───────┘
           │ Mueve a archive/, sincroniza specs
           ▼
    ┌──────────────┐
    │  COMPLETADO  │
    └──────────────┘
```

## Estructura de Directorios

```
proyecto/
│
├── openspec/
│   │
│   ├── config.yaml                    # Configuración global
│   │   └── [schema, context, rules]
│   │
│   ├── changes/                       # Cambios activos
│   │   │
│   │   ├── agregar-oauth/             # Cambio en progreso
│   │   │   ├── .openspec.yaml         # Metadatos
│   │   │   ├── proposal.md            # Qué y por qué
│   │   │   ├── design.md              # Cómo
│   │   │   ├── specs/                 # Delta specs
│   │   │   │   └── auth/
│   │   │   │       └── spec.md
│   │   │   └── tasks.md               # Lista de tareas
│   │   │
│   │   └── archive/                   # Cambios completados
│   │       └── 2026-03-08-agregar-oauth/
│   │           └── [mismos archivos]
│   │
│   └── specs/                         # Especificaciones principales
│       └── auth/
│           └── spec.md                # Spec consolidada
│
└── .claude/
    ├── commands/opsx/                 # Comandos de workflow
    │   ├── explore.md
    │   ├── propose.md
    │   ├── apply.md
    │   └── archive.md
    │
    └── skills/                        # Skills de OpenSpec
        ├── openspec-explore/
        ├── openspec-propose/
        ├── openspec-apply-change/
        └── openspec-archive-change/
```

## Flujo de Comandos

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO DE COMANDOS                          │
└─────────────────────────────────────────────────────────────────┘

ESCENARIO 1: Idea Clara
═══════════════════════════════════════════════════════════════════

Usuario: /opsx:propose agregar-modo-oscuro
    ↓
Claude: Genera todos los artefactos
    ↓
Usuario: /opsx:apply
    ↓
Claude: Implementa tareas 1/5, 2/5, 3/5, 4/5, 5/5
    ↓
Usuario: /opsx:archive
    ↓
✓ Completado


ESCENARIO 2: Idea Vaga
═══════════════════════════════════════════════════════════════════

Usuario: /opsx:explore sistema de cache
    ↓
Claude: ¿Redis vs Memcached vs In-Memory?
        [Compara opciones con diagramas]
    ↓
Usuario: Redis suena mejor
    ↓
Claude: [Explora detalles de Redis]
        ¿Listo para crear propuesta?
    ↓
Usuario: /opsx:propose agregar-cache-redis
    ↓
Claude: Genera artefactos (basado en exploración)
    ↓
Usuario: /opsx:apply
    ↓
Claude: Implementa
    ↓
Usuario: /opsx:archive
    ↓
✓ Completado


ESCENARIO 3: Problema Durante Implementación
═══════════════════════════════════════════════════════════════════

Usuario: /opsx:apply
    ↓
Claude: Tarea 1/5 ✓
        Tarea 2/5 ✓
        Tarea 3/5 ⚠️ Problema: API requiere OAuth2
        [Pausa]
    ↓
Usuario: Actualiza design.md para incluir OAuth2
    ↓
Claude: [Lee design.md actualizado]
        Tarea 3/5 ✓ (con OAuth2)
        Tarea 4/5 ✓
        Tarea 5/5 ✓
    ↓
Usuario: /opsx:archive
    ↓
✓ Completado
```

## Relación entre Artefactos

```
┌─────────────────────────────────────────────────────────────────┐
│                  DEPENDENCIAS DE ARTEFACTOS                     │
└─────────────────────────────────────────────────────────────────┘

                    proposal.md
                    ┌─────────┐
                    │ QUÉ     │
                    │ POR QUÉ │
                    │ ALCANCE │
                    └────┬────┘
                         │
                         ▼
                    design.md
                    ┌─────────┐
                    │ CÓMO    │
                    │ ARQUI   │
                    │ DECISIO │
                    └────┬────┘
                         │
                         ▼
                    specs/
                    ┌─────────┐
                    │ REQUISI │
                    │ CASOS   │
                    │ VALIDAC │
                    └────┬────┘
                         │
                         ▼
                    tasks.md
                    ┌─────────┐
                    │ TAREA 1 │
                    │ TAREA 2 │
                    │ TAREA 3 │
                    └─────────┘

Cada artefacto se construye sobre el anterior.
Claude lee todos antes de implementar.
```

## Flujo de Exploración

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODO EXPLORACIÓN                             │
└─────────────────────────────────────────────────────────────────┘

Usuario: /opsx:explore autenticación en tiempo real
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Claude: Autenticación en tiempo real es amplio...              │
│                                                                 │
│      ESPECTRO DE AUTENTICACIÓN                                 │
│      ════════════════════════════════════════════              │
│                                                                 │
│      Básica          Intermedia        Avanzada                │
│          │               │                 │                   │
│          ▼               ▼                 ▼                   │
│      ┌────────┐      ┌────────┐       ┌────────┐             │
│      │  JWT   │      │Session │       │ OAuth2 │             │
│      │Stateless│     │ Redis  │       │  +MFA  │             │
│      └────────┘      └────────┘       └────────┘             │
│          │               │                 │                   │
│       simple         moderado          complejo                │
│                                                                 │
│ ¿Qué nivel de seguridad necesitas?                            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Usuario: Intermedio, con Redis
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Claude: Perfecto. Veamos la arquitectura...                    │
│                                                                 │
│      FLUJO CON REDIS                                           │
│      ════════════════════════════════════════════              │
│                                                                 │
│      Login                                                      │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────┐                                                  │
│   │Generate │                                                  │
│   │Session  │                                                  │
│   │  Token  │                                                  │
│   └────┬────┘                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────┐                                                  │
│   │  Store  │                                                  │
│   │  Redis  │                                                  │
│   └────┬────┘                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────┐                                                  │
│   │ Return  │                                                  │
│   │  Token  │                                                  │
│   └─────────┘                                                  │
│                                                                 │
│ ¿Listo para crear propuesta?                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Usuario: Sí
    │
    ▼
/opsx:propose agregar-auth-redis
```

## Flujo de Implementación

```
┌─────────────────────────────────────────────────────────────────┐
│                  FLUJO DE /opsx:apply                           │
└─────────────────────────────────────────────────────────────────┘

Usuario: /opsx:apply agregar-auth-redis
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Claude: Leyendo contexto...                                    │
│   ✓ proposal.md                                                │
│   ✓ design.md                                                  │
│   ✓ specs/auth/spec.md                                         │
│   ✓ tasks.md                                                   │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Progreso: 0/5 tareas completadas                               │
│                                                                 │
│ Trabajando en tarea 1/5: Instalar redis-py                    │
│   [Agrega a requirements.txt]                                  │
│   ✓ Completada                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Trabajando en tarea 2/5: Crear RedisClient                    │
│   [Crea src/cache/redis_client.py]                            │
│   ✓ Completada                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Trabajando en tarea 3/5: Implementar get/set                  │
│   [Agrega métodos a RedisClient]                              │
│   ✓ Completada                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Trabajando en tarea 4/5: Integrar con auth                    │
│   [Modifica auth_service.py]                                   │
│   ✓ Completada                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Trabajando en tarea 5/5: Agregar tests                        │
│   [Crea tests/test_redis_client.py]                           │
│   ✓ Completada                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ✓ Implementación completa!                                     │
│   Progreso: 5/5 tareas completadas                            │
│                                                                 │
│   Listo para archivar con /opsx:archive                       │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Archivo

```
┌─────────────────────────────────────────────────────────────────┐
│                  FLUJO DE /opsx:archive                         │
└─────────────────────────────────────────────────────────────────┘

Usuario: /opsx:archive agregar-auth-redis
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Claude: Verificando estado...                                  │
│   ✓ Todos los artefactos completos                            │
│   ✓ Todas las tareas completadas (5/5)                        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Detectadas delta specs en specs/auth/                         │
│                                                                 │
│ Cambios a sincronizar:                                         │
│   + Agregar: endpoint de login con Redis                      │
│   + Agregar: endpoint de logout                               │
│   ~ Modificar: validación de sesión                           │
│                                                                 │
│ ¿Sincronizar specs ahora? (recomendado)                       │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Usuario: Sí
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Sincronizando specs...                                         │
│   openspec/changes/agregar-auth-redis/specs/auth/spec.md      │
│   → openspec/specs/auth/spec.md                               │
│   ✓ Sincronizado                                               │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Archivando cambio...                                           │
│   openspec/changes/agregar-auth-redis/                        │
│   → openspec/changes/archive/2026-03-08-agregar-auth-redis/   │
│   ✓ Archivado                                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ ✓ Archivo completo!                                            │
│                                                                 │
│   Cambio: agregar-auth-redis                                  │
│   Ubicación: archive/2026-03-08-agregar-auth-redis/           │
│   Specs: ✓ Sincronizadas                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Sincronización de Specs

```
┌─────────────────────────────────────────────────────────────────┐
│              SINCRONIZACIÓN DE DELTA SPECS                      │
└─────────────────────────────────────────────────────────────────┘

DURANTE EL CAMBIO:
═══════════════════════════════════════════════════════════════════

openspec/changes/agregar-auth-redis/specs/auth/spec.md
┌─────────────────────────────────────────────────────────────────┐
│ # Especificación: Autenticación                                │
│                                                                 │
│ ## Endpoints                                                    │
│ + POST /auth/login    (NUEVO)                                  │
│ + POST /auth/logout   (NUEVO)                                  │
│                                                                 │
│ ## Sesiones                                                     │
│ ~ Almacenamiento: Redis (MODIFICADO)                           │
│ ~ TTL: 24 horas (MODIFICADO)                                   │
└─────────────────────────────────────────────────────────────────┘

                         │
                         │ Al archivar
                         ▼

DESPUÉS DE ARCHIVAR:
═══════════════════════════════════════════════════════════════════

openspec/specs/auth/spec.md
┌─────────────────────────────────────────────────────────────────┐
│ # Especificación: Autenticación                                │
│                                                                 │
│ ## Endpoints                                                    │
│ POST /auth/login      ← Agregado                               │
│ POST /auth/logout     ← Agregado                               │
│ GET /auth/verify      (Existente)                              │
│                                                                 │
│ ## Sesiones                                                     │
│ Almacenamiento: Redis ← Actualizado                            │
│ TTL: 24 horas         ← Actualizado                            │
└─────────────────────────────────────────────────────────────────┘

Las delta specs se FUSIONAN con las specs principales.
```

## Comparación de Flujos

```
┌─────────────────────────────────────────────────────────────────┐
│              FLUJO TRADICIONAL vs OPENSPEC                      │
└─────────────────────────────────────────────────────────────────┘

FLUJO TRADICIONAL:
═══════════════════════════════════════════════════════════════════

Idea → Codificar → Problemas → Rehacer → Más problemas → Fix
  │                                                          │
  └──────────────────────────────────────────────────────────┘
                    Ciclo de retrabajos

Documentación: ❌ Inexistente o desactualizada
Decisiones: ❌ Perdidas en Slack/email
Contexto: ❌ Solo en la cabeza del dev
Onboarding: ❌ Difícil para nuevos devs


FLUJO OPENSPEC:
═══════════════════════════════════════════════════════════════════

Idea → Explorar → Proponer → Diseñar → Especificar → Implementar
  │                                                          │
  └──────────────────────────────────────────────────────────┘
              Proceso estructurado y documentado

Documentación: ✓ Automática y actualizada
Decisiones: ✓ Capturadas en design.md
Contexto: ✓ Completo en artefactos
Onboarding: ✓ Fácil con cambios archivados


TIEMPO INVERTIDO:
═══════════════════════════════════════════════════════════════════

Tradicional:
├─ Codificar: 40%
├─ Debuggear: 30%
├─ Rehacer: 20%
└─ Documentar: 10% (si acaso)

OpenSpec:
├─ Planificar: 20%
├─ Codificar: 50%
├─ Debuggear: 15%
├─ Rehacer: 5%
└─ Documentar: 10% (automático)

Resultado: Menos retrabajos, mejor calidad, más predecible
```

## Anatomía de un Cambio

```
┌─────────────────────────────────────────────────────────────────┐
│           ANATOMÍA DE UN CAMBIO OPENSPEC                        │
└─────────────────────────────────────────────────────────────────┘

openspec/changes/agregar-auth-redis/
│
├── .openspec.yaml
│   ┌─────────────────────────────────────────────────────────────┐
│   │ schema: spec-driven                                         │
│   │ created: 2026-03-08T10:30:00Z                              │
│   │ status: in_progress                                         │
│   └─────────────────────────────────────────────────────────────┘
│
├── proposal.md
│   ┌─────────────────────────────────────────────────────────────┐
│   │ # Propuesta: Agregar Autenticación con Redis              │
│   │                                                             │
│   │ ## Objetivo                                                 │
│   │ Implementar autenticación con sesiones en Redis            │
│   │                                                             │
│   │ ## Por qué                                                  │
│   │ Necesitamos sesiones persistentes y escalables             │
│   │                                                             │
│   │ ## Alcance                                                  │
│   │ - Login/logout endpoints                                    │
│   │ - Sesiones en Redis con TTL                                │
│   │                                                             │
│   │ ## No-objetivos                                             │
│   │ - OAuth social (será otro cambio)                          │
│   └─────────────────────────────────────────────────────────────┘
│
├── design.md
│   ┌─────────────────────────────────────────────────────────────┐
│   │ # Diseño: Autenticación con Redis                          │
│   │                                                             │
│   │ ## Arquitectura                                             │
│   │ Cliente → API → Auth Service → Redis                       │
│   │                                                             │
│   │ ## Decisiones                                               │
│   │ - Redis para sesiones (vs in-memory)                       │
│   │ - TTL de 24 horas                                          │
│   │ - JWT para tokens                                           │
│   │                                                             │
│   │ ## Componentes                                              │
│   │ - RedisClient: Wrapper de redis-py                         │
│   │ - AuthService: Lógica de autenticación                     │
│   └─────────────────────────────────────────────────────────────┘
│
├── specs/
│   └── auth/
│       └── spec.md
│           ┌─────────────────────────────────────────────────────┐
│           │ # Especificación: Autenticación                     │
│           │                                                     │
│           │ ## POST /auth/login                                 │
│           │ Request: { email, password }                        │
│           │ Response: { token, expiresAt }                      │
│           │                                                     │
│           │ ## POST /auth/logout                                │
│           │ Request: { token }                                  │
│           │ Response: { success }                               │
│           │                                                     │
│           │ ## Errores                                          │
│           │ - 401: Credenciales inválidas                      │
│           │ - 404: Usuario no existe                            │
│           └─────────────────────────────────────────────────────┘
│
└── tasks.md
    ┌─────────────────────────────────────────────────────────────┐
    │ # Tareas: Agregar Autenticación con Redis                  │
    │                                                             │
    │ - [x] Instalar redis-py                                     │
    │ - [x] Crear RedisClient                                     │
    │ - [x] Implementar get/set con TTL                           │
    │ - [ ] Crear AuthService                                     │
    │ - [ ] Implementar endpoints login/logout                    │
    │ - [ ] Agregar tests                                         │
    └─────────────────────────────────────────────────────────────┘
```

## Mapa Mental de OpenSpec

```
                        OPENSPEC
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    COMANDOS          ARTEFACTOS          CONCEPTOS
        │                  │                  │
    ┌───┴───┐          ┌───┴───┐          ┌───┴───┐
    │       │          │       │          │       │
 explore propose    proposal design    cambio  specs
    │       │          │       │          │       │
  apply  archive    specs   tasks     activo archivado
                                         │
                                    delta specs
```

## Timeline de un Proyecto

```
┌─────────────────────────────────────────────────────────────────┐
│                  TIMELINE DE PROYECTO                           │
└─────────────────────────────────────────────────────────────────┘

Semana 1:
═══════════════════════════════════════════════════════════════════
[agregar-auth-redis]     ████████████ → Archivado
[agregar-user-profile]   ████████ → En progreso

Semana 2:
═══════════════════════════════════════════════════════════════════
[agregar-user-profile]   ████ → Archivado
[agregar-notificaciones] ████████████ → Archivado

Semana 3:
═══════════════════════════════════════════════════════════════════
[refactor-auth-layer]    ████████████████ → Archivado

Semana 4:
═══════════════════════════════════════════════════════════════════
[agregar-payments]       ████████ → En progreso
[fix-session-bug]        ████ → Archivado


RESULTADO:
═══════════════════════════════════════════════════════════════════
openspec/changes/archive/
├── 2026-03-08-agregar-auth-redis/
├── 2026-03-10-agregar-user-profile/
├── 2026-03-15-agregar-notificaciones/
├── 2026-03-20-refactor-auth-layer/
└── 2026-03-25-fix-session-bug/

Cada cambio archivado es documentación viva del proyecto.
```

## Conclusión Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                    OPENSPEC EN UNA IMAGEN                       │
└─────────────────────────────────────────────────────────────────┘

    💡 Idea
     │
     ▼
    🔍 Explorar (opcional)
     │
     ▼
    📝 Proponer
     │  └─ proposal.md (qué/por qué)
     │  └─ design.md (cómo)
     │  └─ specs/ (requisitos)
     │  └─ tasks.md (pasos)
     │
     ▼
    ⚙️  Implementar
     │  └─ Tarea 1 ✓
     │  └─ Tarea 2 ✓
     │  └─ Tarea 3 ✓
     │
     ▼
    📦 Archivar
     │  └─ Sincronizar specs
     │  └─ Mover a archive/
     │
     ▼
    ✅ Completado + Documentado

═══════════════════════════════════════════════════════════════════

BENEFICIOS:
✓ Menos retrabajos
✓ Mejor calidad
✓ Documentación automática
✓ Contexto preservado
✓ Onboarding fácil
✓ Desarrollo predecible
```

---

**Estos diagramas te ayudan a visualizar cómo funciona OpenSpec. Úsalos como referencia mientras trabajas con el sistema.**
