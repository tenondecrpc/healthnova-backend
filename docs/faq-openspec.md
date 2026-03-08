# Preguntas Frecuentes sobre OpenSpec

## Conceptos Básicos

### ¿Qué es OpenSpec?

OpenSpec es un sistema de desarrollo basado en especificaciones que estructura tu proceso de desarrollo en fases claras: exploración, propuesta, diseño, especificación, tareas e implementación. Te ayuda a pensar antes de codificar y mantiene todo documentado.

### ¿Por qué usar OpenSpec en lugar de solo codificar?

**Ventajas:**
- Documentación automática de decisiones
- Contexto completo para cada cambio
- Menos retrabajos por falta de planificación
- Historial de por qué se hicieron las cosas
- Facilita onboarding de nuevos desarrolladores
- Mejor para features complejas

**Cuándo NO usar OpenSpec:**
- Cambios triviales (typos, ajustes de estilo)
- Prototipos rápidos desechables
- Experimentos de una sola vez

### ¿OpenSpec reemplaza a Git?

No. OpenSpec y Git son complementarios:
- **Git:** Control de versiones del código
- **OpenSpec:** Estructura del proceso de desarrollo y documentación

Usa ambos juntos. Los cambios de OpenSpec se commitean a Git.

### ¿Necesito usar todos los comandos siempre?

No. El flujo mínimo es:
```
/opsx:propose → /opsx:apply → /opsx:archive
```

Usa `/opsx:explore` solo cuando necesites pensar o investigar primero.

## Comandos

### ¿Cuándo debo usar `/opsx:explore`?

Usa explore cuando:
- Tienes una idea vaga
- No estás seguro del mejor enfoque
- Necesitas comparar opciones
- Quieres entender código existente
- El problema es complejo

NO uses explore cuando:
- Ya sabes exactamente qué hacer
- Es un cambio trivial
- Solo quieres implementar algo obvio

### ¿Puedo usar `/opsx:apply` sin `/opsx:propose`?

No. Necesitas crear el cambio primero con `/opsx:propose` para generar los artefactos (proposal, design, tasks).

### ¿Qué pasa si interrumpo `/opsx:apply`?

Puedes pausar en cualquier momento. Las tareas completadas quedan marcadas con `[x]`. Cuando ejecutes `/opsx:apply` de nuevo, continuará desde donde lo dejaste.

### ¿Puedo ejecutar `/opsx:apply` múltiples veces?

Sí. Es útil para:
- Implementar en sesiones (pausar y continuar)
- Revisar cambios antes de continuar
- Ajustar el diseño y continuar

### ¿Debo archivar inmediatamente después de completar?

No es obligatorio, pero es recomendado para mantener el workspace limpio. Puedes dejar cambios activos si planeas hacer ajustes pronto.

## Artefactos

### ¿Qué es un "artefacto"?

Un artefacto es un documento generado por OpenSpec:
- `proposal.md` - Qué y por qué
- `design.md` - Cómo
- `specs/` - Requisitos detallados
- `tasks.md` - Lista de tareas

### ¿Puedo editar los artefactos manualmente?

¡Sí! Puedes editar cualquier artefacto en cualquier momento:
```bash
vim openspec/changes/mi-cambio/design.md
```

O pedir a Claude que lo actualice:
```
"Actualiza design.md para usar PostgreSQL en lugar de MySQL"
```

### ¿Qué son las "delta specs"?

Las delta specs son especificaciones específicas de un cambio, ubicadas en:
```
openspec/changes/<nombre>/specs/
```

Solo contienen cambios para ese cambio específico. Al archivar, se sincronizan con las specs principales en:
```
openspec/specs/
```

### ¿Cuándo debo actualizar specs principales vs delta specs?

- **Delta specs:** Durante un cambio activo
- **Specs principales:** Después de archivar (sincronización automática)

No edites specs principales manualmente mientras trabajas en un cambio.

### ¿Qué pasa si no genero todos los artefactos?

`/opsx:apply` requiere que ciertos artefactos existan (típicamente `tasks.md`). Si faltan, Claude te pedirá completarlos primero.

## Tareas

### ¿Cómo deben ser las tareas en tasks.md?

**Buenas tareas:**
- Pequeñas (1-2 horas)
- Específicas y accionables
- Verificables
- En orden lógico

**Ejemplo:**
```markdown
- [ ] Instalar dependencia redis (pip install redis)
- [ ] Crear clase RedisClient en src/cache/redis_client.py
- [ ] Implementar método get() con manejo de errores
- [ ] Implementar método set() con TTL
- [ ] Agregar tests unitarios para RedisClient
- [ ] Actualizar documentación de cache
```

### ¿Puedo agregar tareas durante la implementación?

Sí. Si descubres trabajo adicional durante `/opsx:apply`:
1. Pausa la implementación
2. Agrega las nuevas tareas a `tasks.md`
3. Continúa con `/opsx:apply`

### ¿Qué hago si una tarea es muy grande?

Edita `tasks.md` y divídela en tareas más pequeñas antes de continuar con `/opsx:apply`.

### ¿Puedo cambiar el orden de las tareas?

Sí, pero hazlo antes de que Claude las implemente. Una vez que una tarea está marcada como `[x]`, no la reordenes.

## Cambios

### ¿Cuántos cambios puedo tener activos?

Técnicamente ilimitados, pero es mejor mantener pocos cambios activos (1-3) para no perder foco.

### ¿Puedo trabajar en múltiples cambios en paralelo?

Sí, pero especifica cuál quieres usar:
```
/opsx:apply cambio-1
/opsx:apply cambio-2
```

### ¿Cómo nombro mis cambios?

Usa kebab-case descriptivo:

**Buenos nombres:**
- `agregar-autenticacion-oauth`
- `fix-sesion-timeout-bug`
- `refactor-auth-layer`
- `integrar-stripe-payments`

**Malos nombres:**
- `cambio1`
- `fix`
- `nueva-feature`
- `Agregar OAuth` (no kebab-case)

### ¿Puedo renombrar un cambio?

Sí, pero manualmente:
```bash
mv openspec/changes/nombre-viejo openspec/changes/nombre-nuevo
```

También actualiza `.openspec.yaml` dentro del directorio.

### ¿Qué pasa si elimino un cambio por error?

Si está en Git, puedes recuperarlo:
```bash
git checkout openspec/changes/mi-cambio
```

Si no está en Git y lo eliminaste, se perdió. Por eso es importante commitear regularmente.

## Archivo

### ¿Qué hace `/opsx:archive`?

1. Verifica que artefactos y tareas estén completos
2. Sincroniza delta specs con specs principales (si existen)
3. Mueve el cambio a `openspec/changes/archive/YYYY-MM-DD-nombre/`

### ¿Puedo archivar un cambio incompleto?

Sí, pero Claude te advertirá. Confirma que quieres proceder.

### ¿Puedo desarchivar un cambio?

Sí, manualmente:
```bash
mv openspec/changes/archive/2026-03-08-mi-cambio openspec/changes/mi-cambio
```

### ¿Debo commitear cambios archivados a Git?

Sí. Los cambios archivados son documentación valiosa del historial del proyecto.

### ¿Qué pasa con las specs al archivar?

Las delta specs en `openspec/changes/<nombre>/specs/` se sincronizan con las specs principales en `openspec/specs/`. Claude te preguntará si quieres sincronizar.

## Configuración

### ¿Qué va en openspec/config.yaml?

```yaml
schema: spec-driven  # Requerido

context: |           # Opcional pero recomendado
  Stack: Python, FastAPI, PostgreSQL
  Estilo: PEP 8
  Tests: pytest
  Dominio: e-commerce

rules:               # Opcional
  proposal:
    - Mantén propuestas bajo 500 palabras
  tasks:
    - Tareas de máximo 2 horas
```

### ¿Debo configurar context?

Es altamente recomendado. El contexto ayuda a Claude a generar artefactos más precisos y relevantes para tu proyecto.

### ¿Puedo tener diferentes configs por cambio?

No. `config.yaml` es global para el proyecto. Pero puedes agregar contexto específico en el `proposal.md` de cada cambio.

### ¿Qué schemas están disponibles?

Por defecto: `spec-driven`

Puedes crear schemas personalizados, pero eso es avanzado. Empieza con `spec-driven`.

## Integración con Claude

### ¿Necesito Claude para usar OpenSpec?

OpenSpec es una herramienta CLI que funciona independientemente, pero está diseñada para trabajar con Claude. Los comandos `/opsx:*` son específicos de Claude.

### ¿Qué son las "skills" en .claude/skills/?

Las skills son capacidades que Claude puede usar para interactuar con OpenSpec:
- `openspec-explore` - Modo exploración
- `openspec-propose` - Crear propuestas
- `openspec-apply-change` - Implementar
- `openspec-archive-change` - Archivar

### ¿Puedo usar OpenSpec sin las skills?

Sí, usando los comandos CLI directamente:
```bash
openspec new change mi-cambio
openspec status --change mi-cambio
```

Pero pierdes la integración fluida con Claude.

### ¿Claude puede ver mis cambios archivados?

Sí, si le pides explícitamente:
```
"Muéstrame el diseño del cambio archivado 2026-03-08-agregar-oauth"
```

## Problemas Comunes

### "openspec: command not found"

OpenSpec CLI no está instalado. Instálalo según la documentación oficial.

### "No such file or directory: openspec/config.yaml"

No has inicializado OpenSpec. Ejecuta:
```bash
openspec init
```

### Claude no genera artefactos correctamente

Verifica que `openspec/config.yaml` existe y tiene:
```yaml
schema: spec-driven
```

### Las tareas no se marcan como completadas

Claude debe actualizar `tasks.md` cambiando `- [ ]` a `- [x]`. Si no lo hace, edítalo manualmente.

### "Change already exists"

Ya existe un cambio con ese nombre. Opciones:
1. Usar otro nombre
2. Continuar el cambio existente
3. Archivar el existente primero

### No puedo archivar: "Target already exists"

Ya existe un archivo con ese nombre y fecha. Opciones:
1. Renombrar el archivo existente
2. Esperar al día siguiente (fecha diferente)
3. Eliminar el archivo existente si es duplicado

## Mejores Prácticas

### ¿Cuándo debo crear un nuevo cambio vs continuar uno existente?

**Nuevo cambio:**
- Feature diferente
- Bug diferente
- Alcance claramente separado

**Continuar existente:**
- Ajustes al mismo feature
- Tareas adicionales relacionadas
- Fixes a la implementación actual

### ¿Debo crear un cambio para cada bug fix?

Para bugs significativos: sí.
Para typos o ajustes triviales: no, solo commitea directamente.

### ¿Cómo manejo features muy grandes?

Divide en múltiples cambios pequeños:

❌ Un cambio gigante:
```
sistema-notificaciones-completo (50 tareas)
```

✅ Múltiples cambios pequeños:
```
notification-core (8 tareas)
notification-email (6 tareas)
notification-sms (5 tareas)
notification-push (7 tareas)
```

### ¿Debo commitear a Git después de cada tarea?

No necesariamente. Commitea cuando:
- Completas un grupo lógico de tareas
- Terminas una sesión de trabajo
- Completas el cambio entero

### ¿Cómo manejo cambios urgentes?

Para hotfixes urgentes:
1. Opción rápida: Commitea directamente sin OpenSpec
2. Opción documentada: Usa OpenSpec pero salta explore:
   ```
   /opsx:propose fix-critical-bug
   /opsx:apply
   /opsx:archive
   ```

## Casos de Uso Específicos

### ¿Cómo uso OpenSpec para refactoring?

```
1. /opsx:explore <código a refactorizar>
   → Mapea código existente
   → Identifica problemas
   → Propone estructura nueva

2. /opsx:propose refactor-<componente>
   → Genera plan de refactor

3. /opsx:apply
   → Implementa paso a paso

4. /opsx:archive
```

### ¿Cómo uso OpenSpec para integraciones externas?

```
1. /opsx:explore integración con <servicio>
   → Investiga API
   → Compara opciones
   → Identifica límites y costos

2. /opsx:propose agregar-<servicio>-integration
   → Documenta decisiones
   → Define tareas

3. /opsx:apply
4. /opsx:archive
```

### ¿Cómo uso OpenSpec en equipo?

1. Cada desarrollador crea sus propios cambios
2. Commitean cambios activos a Git en branches
3. Archivan al completar
4. Merge a main incluye cambios archivados

**Estructura en Git:**
```
feature/agregar-oauth
  ├── código
  └── openspec/changes/agregar-oauth/

main (después de merge)
  ├── código
  └── openspec/changes/archive/2026-03-08-agregar-oauth/
```

### ¿Cómo documento decisiones arquitectónicas?

Usa `/opsx:explore` para discutir y luego captura en `design.md`:

```
/opsx:explore arquitectura de microservicios vs monolito

[Discusión con Claude]

"Captura esta decisión en un cambio"

/opsx:propose decision-arquitectura-monolito

[design.md documenta la decisión y justificación]
```

## Avanzado

### ¿Puedo crear mis propios schemas?

Sí, pero es avanzado. Requiere definir:
- Artefactos personalizados
- Dependencias entre artefactos
- Templates
- Instrucciones

Empieza con `spec-driven` y considera schemas personalizados solo si tienes necesidades muy específicas.

### ¿Puedo automatizar OpenSpec con CI/CD?

Sí. Puedes:
- Validar que cambios tengan artefactos completos
- Verificar que tareas estén marcadas como completadas
- Generar reportes de cambios

Ejemplo:
```bash
# En CI
openspec status --change $CHANGE_NAME --json | jq '.artifacts[] | select(.status != "done")'
```

### ¿Puedo integrar OpenSpec con otras herramientas?

Sí. OpenSpec usa archivos Markdown y YAML estándar. Puedes:
- Parsear con scripts
- Generar documentación con MkDocs
- Integrar con Jira/Linear
- Crear dashboards

### ¿Hay plugins o extensiones?

OpenSpec es extensible a través de:
- Schemas personalizados
- Skills de Claude personalizadas
- Scripts que usan la CLI

## Recursos

- **Guía completa:** `docs/guia-openspec-claude.md`
- **Ejemplos prácticos:** `docs/ejemplos-openspec.md`
- **Referencia rápida:** `docs/referencia-rapida-openspec.md`
- **Documentación oficial:** [openspec.dev](https://openspec.dev)

## ¿Más Preguntas?

Si tienes una pregunta que no está aquí:
1. Revisa la documentación oficial
2. Pregunta a Claude directamente
3. Experimenta con un cambio pequeño

¡La mejor forma de aprender OpenSpec es usándolo!
