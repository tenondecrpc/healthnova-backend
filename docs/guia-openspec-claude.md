# Guía de OpenSpec con Claude

## ¿Qué es OpenSpec?

OpenSpec es un sistema de desarrollo basado en especificaciones que te ayuda a construir software de manera estructurada y documentada. En lugar de saltar directamente al código, OpenSpec te guía a través de un proceso que incluye:

1. **Propuesta** - Define qué quieres construir y por qué
2. **Diseño** - Planifica cómo lo vas a implementar
3. **Especificaciones** - Documenta los requisitos y comportamientos esperados
4. **Tareas** - Desglosa el trabajo en pasos implementables
5. **Implementación** - Ejecuta las tareas con contexto completo

## Estructura del Proyecto

Después de ejecutar `openspec init`, tu proyecto tendrá esta estructura:

```
tu-proyecto/
├── openspec/
│   ├── config.yaml           # Configuración del proyecto
│   ├── changes/              # Cambios activos
│   │   └── archive/          # Cambios completados
│   └── specs/                # Especificaciones principales
└── .claude/
    ├── commands/opsx/        # Comandos de flujo de trabajo
    └── skills/               # Habilidades de OpenSpec
```

## Configuración Inicial

El archivo `openspec/config.yaml` es donde defines el contexto de tu proyecto:

```yaml
schema: spec-driven

# Contexto del proyecto (opcional pero recomendado)
context: |
  Stack tecnológico: TypeScript, React, Node.js
  Usamos conventional commits
  Dominio: plataforma de e-commerce
  
# Reglas por artefacto (opcional)
rules:
  proposal:
    - Mantén las propuestas bajo 500 palabras
    - Siempre incluye una sección "No-objetivos"
  tasks:
    - Divide las tareas en bloques de máximo 2 horas
```

## Los 4 Comandos Principales

OpenSpec funciona con 4 comandos que representan el ciclo de vida de un cambio:

### 1. `/opsx:explore` - Modo Exploración

**Cuándo usarlo:** Cuando tienes una idea vaga o necesitas pensar antes de comprometerte con una implementación.

**Qué hace:**
- Te ayuda a explorar ideas sin presión
- Investiga el código existente
- Compara opciones
- Visualiza arquitecturas con diagramas ASCII
- NO implementa código (solo piensa)

**Ejemplo de uso:**
```
Usuario: /opsx:explore autenticación en tiempo real

Claude: Autenticación en tiempo real es un espacio amplio. Déjame pensar...

      ESPECTRO DE AUTENTICACIÓN
      ════════════════════════════════════════════

      Básica            Intermedia          Avanzada
          │                   │                 │
          ▼                   ▼                 ▼
      ┌────────┐         ┌────────┐        ┌────────┐
      │  JWT   │         │Session │        │ OAuth2 │
      │Stateless│        │ Redis  │        │  +MFA  │
      └────────┘         └────────┘        └────────┘
          │                   │                 │
       simple             moderado           complejo

      ¿Qué nivel de seguridad necesitas?
```

**Características clave:**
- Es un compañero de pensamiento, no un instructor
- Usa diagramas ASCII liberalmente
- Hace preguntas que surgen naturalmente
- No sigue un script fijo
- Puede leer tu código para fundamentar las discusiones

### 2. `/opsx:propose` - Crear Propuesta

**Cuándo usarlo:** Cuando sabes qué quieres construir y estás listo para formalizarlo.

**Qué hace:**
- Crea un nuevo cambio con nombre en kebab-case
- Genera automáticamente todos los artefactos necesarios:
  - `proposal.md` - Qué y por qué
  - `design.md` - Cómo
  - `specs/` - Requisitos detallados
  - `tasks.md` - Pasos de implementación

**Ejemplo de uso:**
```
Usuario: /opsx:propose agregar-autenticacion-oauth

Claude: Creando cambio: agregar-autenticacion-oauth

✓ Creado proposal.md
✓ Creado design.md  
✓ Creado specs/auth/spec.md
✓ Creado tasks.md

Todos los artefactos creados. Listo para implementación.
Ejecuta /opsx:apply para comenzar a trabajar en las tareas.
```

**Estructura de un cambio:**
```
openspec/changes/agregar-autenticacion-oauth/
├── .openspec.yaml        # Metadatos del cambio
├── proposal.md           # Propuesta: qué y por qué
├── design.md             # Diseño: cómo
├── specs/                # Especificaciones
│   └── auth/
│       └── spec.md
└── tasks.md              # Lista de tareas
```

### 3. `/opsx:apply` - Implementar

**Cuándo usarlo:** Cuando tienes un cambio con tareas definidas y estás listo para codificar.

**Qué hace:**
- Lee todos los artefactos del cambio para tener contexto completo
- Implementa las tareas una por una
- Marca cada tarea como completada
- Mantiene los cambios mínimos y enfocados
- Se pausa si encuentra problemas o ambigüedades

**Ejemplo de uso:**
```
Usuario: /opsx:apply

Claude: Usando cambio: agregar-autenticacion-oauth

## Implementando: agregar-autenticacion-oauth (schema: spec-driven)
Progreso: 0/5 tareas completadas

Trabajando en tarea 1/5: Instalar dependencias de OAuth
[...implementación...]
✓ Tarea completada

Trabajando en tarea 2/5: Crear endpoint de callback
[...implementación...]
✓ Tarea completada
```

**Cuándo se pausa:**
- La tarea no está clara → pide aclaración
- La implementación revela un problema de diseño → sugiere actualizar artefactos
- Encuentra un error o bloqueo → reporta y espera orientación

### 4. `/opsx:archive` - Archivar

**Cuándo usarlo:** Cuando has completado todas las tareas y quieres finalizar el cambio.

**Qué hace:**
- Verifica que todos los artefactos estén completos
- Verifica que todas las tareas estén marcadas como completadas
- Sincroniza las especificaciones delta con las principales (si existen)
- Mueve el cambio a `openspec/changes/archive/YYYY-MM-DD-nombre/`

**Ejemplo de uso:**
```
Usuario: /opsx:archive

Claude: ## Archivo Completo

**Cambio:** agregar-autenticacion-oauth
**Schema:** spec-driven
**Archivado en:** openspec/changes/archive/2026-03-08-agregar-autenticacion-oauth/
**Specs:** ✓ Sincronizadas con specs principales

Todos los artefactos completos. Todas las tareas completas.
```

## Flujo de Trabajo Típico

### Escenario 1: Idea Clara

```
1. /opsx:propose agregar-modo-oscuro
   → Claude genera todos los artefactos

2. /opsx:apply
   → Claude implementa las tareas

3. /opsx:archive
   → Cambio completado y archivado
```

### Escenario 2: Idea Vaga

```
1. /opsx:explore colaboración en tiempo real
   → Exploras opciones, comparas enfoques
   → Decides usar WebSockets con Redis

2. /opsx:propose agregar-websockets-redis
   → Claude genera artefactos basados en la exploración

3. /opsx:apply
   → Implementación

4. /opsx:archive
   → Finalización
```

### Escenario 3: Problema Durante Implementación

```
1. /opsx:apply
   → Tarea 3/7: "Integrar con API externa"
   → Claude descubre que la API requiere autenticación compleja

2. Claude se pausa y sugiere:
   "La implementación revela que necesitamos OAuth2.
   ¿Actualizar design.md o crear un cambio separado?"

3. Decides actualizar design.md
   → Claude actualiza el diseño
   → Continúa con la implementación ajustada
```

## Artefactos Explicados

### proposal.md
Define el QUÉ y el POR QUÉ:
- ¿Qué problema resuelve?
- ¿Por qué es importante?
- ¿Cuál es el alcance?
- ¿Qué NO incluye? (no-objetivos)

### design.md
Define el CÓMO:
- Arquitectura general
- Decisiones técnicas
- Integraciones
- Consideraciones de rendimiento/seguridad

### specs/
Requisitos detallados por capacidad:
- Comportamientos esperados
- Casos de uso
- Validaciones
- Reglas de negocio

### tasks.md
Lista de tareas implementables:
```markdown
- [ ] Tarea 1: Descripción clara y accionable
- [ ] Tarea 2: Otra tarea específica
- [x] Tarea 3: Tarea completada
```

## Consejos y Mejores Prácticas

### 1. Usa el Contexto del Proyecto

En `openspec/config.yaml`, define tu stack y convenciones:

```yaml
context: |
  Stack: Python, FastAPI, PostgreSQL, Redis
  Usamos type hints en todo el código
  Seguimos PEP 8
  Tests con pytest
  Dominio: sistema de salud
```

Esto ayuda a Claude a generar artefactos más precisos.

### 2. Explora Antes de Proponer

Si no estás 100% seguro de tu enfoque, usa `/opsx:explore` primero:
- Compara opciones
- Investiga el código existente
- Visualiza la arquitectura
- Identifica riesgos

### 3. Tareas Pequeñas y Enfocadas

En `tasks.md`, divide el trabajo en tareas de 1-2 horas:

❌ Malo:
```markdown
- [ ] Implementar sistema de autenticación completo
```

✅ Bueno:
```markdown
- [ ] Instalar y configurar dependencias de OAuth
- [ ] Crear modelo de usuario en base de datos
- [ ] Implementar endpoint de login
- [ ] Implementar endpoint de callback
- [ ] Agregar middleware de autenticación
- [ ] Escribir tests de integración
```

### 4. Actualiza Artefactos Durante la Implementación

OpenSpec es fluido, no rígido. Si descubres algo durante `/opsx:apply`:
- Pausa la implementación
- Actualiza `design.md` o `specs/`
- Continúa con el nuevo contexto

### 5. Usa Especificaciones Delta

Las specs en `openspec/changes/<nombre>/specs/` son "delta specs":
- Solo incluyen cambios para este cambio específico
- Se sincronizan con las specs principales al archivar
- Mantienen las specs principales limpias

## Comandos CLI Útiles

```bash
# Listar todos los cambios activos
openspec list

# Ver estado de un cambio específico
openspec status --change nombre-del-cambio

# Ver instrucciones para un artefacto
openspec instructions proposal --change nombre-del-cambio

# Crear un nuevo cambio manualmente
openspec new change nombre-del-cambio
```

## Integración con Claude

OpenSpec está diseñado para trabajar con Claude a través de:

### Skills (Habilidades)
Ubicadas en `.claude/skills/openspec-*/`, estas habilidades permiten a Claude:
- Entender el sistema OpenSpec
- Ejecutar comandos CLI
- Generar artefactos
- Implementar tareas

### Commands (Comandos)
Los comandos `/opsx:*` son atajos que activan las skills correspondientes.

## Solución de Problemas

### "No puedo encontrar el cambio"
```bash
# Lista todos los cambios
openspec list --json
```

### "Los artefactos no se generan"
Verifica que `openspec/config.yaml` existe y tiene el schema correcto:
```yaml
schema: spec-driven
```

### "Claude no implementa las tareas"
Asegúrate de que:
1. El cambio tiene `tasks.md` con tareas definidas
2. Usaste `/opsx:apply` (no solo "implementa esto")
3. Las tareas están en formato checkbox: `- [ ] Descripción`

### "Quiero cambiar el diseño a mitad de implementación"
¡Perfecto! OpenSpec es fluido:
1. Edita `design.md` directamente
2. Continúa con `/opsx:apply`
3. Claude usará el diseño actualizado

## Ejemplo Completo

Vamos a construir una funcionalidad de notificaciones por email:

```
# Paso 1: Explorar (opcional)
Usuario: /opsx:explore sistema de notificaciones por email

Claude: [Explora opciones: SMTP directo vs servicios como SendGrid]
        [Compara pros/contras]
        [Recomienda SendGrid para producción]

# Paso 2: Proponer
Usuario: /opsx:propose agregar-notificaciones-email

Claude: ✓ Creado proposal.md
        ✓ Creado design.md (usando SendGrid)
        ✓ Creado specs/notifications/spec.md
        ✓ Creado tasks.md (6 tareas)

# Paso 3: Revisar artefactos (opcional)
Usuario: Muéstrame el design.md

Claude: [Muestra el diseño]

Usuario: Cambia a usar templates de Jinja2

Claude: ✓ Actualizado design.md

# Paso 4: Implementar
Usuario: /opsx:apply

Claude: Implementando tarea 1/6: Instalar SendGrid SDK
        [Agrega dependencia]
        ✓ Completada
        
        Implementando tarea 2/6: Crear servicio de email
        [Crea email_service.py]
        ✓ Completada
        
        [... continúa hasta tarea 6/6 ...]
        
        ¡Implementación completa! 6/6 tareas completadas.

# Paso 5: Archivar
Usuario: /opsx:archive

Claude: ## Archivo Completo
        Cambio: agregar-notificaciones-email
        Archivado en: openspec/changes/archive/2026-03-08-agregar-notificaciones-email/
        Specs: ✓ Sincronizadas
```

## Recursos Adicionales

- **Documentación oficial:** [openspec.dev](https://openspec.dev)
- **Ejemplos:** Revisa `openspec/changes/archive/` para ver cambios completados
- **Configuración:** Personaliza `openspec/config.yaml` para tu proyecto

## Conclusión

OpenSpec transforma el desarrollo caótico en un proceso estructurado:

1. **Piensa** con `/opsx:explore`
2. **Planifica** con `/opsx:propose`
3. **Construye** con `/opsx:apply`
4. **Finaliza** con `/opsx:archive`

Cada cambio queda documentado, cada decisión tiene contexto, y cada implementación sigue un plan claro.

¡Empieza con un cambio pequeño y experimenta el flujo!
