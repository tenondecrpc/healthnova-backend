# Referencia Rápida de OpenSpec

## Comandos Principales

| Comando | Cuándo Usar | Qué Hace |
|---------|-------------|----------|
| `/opsx:explore` | Tienes una idea vaga o necesitas pensar | Modo exploración: investiga, compara opciones, visualiza arquitectura |
| `/opsx:propose` | Sabes qué quieres construir | Crea cambio y genera todos los artefactos (proposal, design, specs, tasks) |
| `/opsx:apply` | Tienes tareas definidas y listo para codificar | Implementa las tareas una por una |
| `/opsx:archive` | Completaste todas las tareas | Archiva el cambio y sincroniza specs |

## Comandos CLI

```bash
# Listar cambios activos
openspec list
openspec list --json

# Ver estado de un cambio
openspec status --change <nombre>
openspec status --change <nombre> --json

# Crear nuevo cambio manualmente
openspec new change <nombre>

# Ver instrucciones para artefacto
openspec instructions <artifact-id> --change <nombre>
openspec instructions apply --change <nombre>
```

## Estructura de Directorios

```
proyecto/
├── openspec/
│   ├── config.yaml              # Configuración del proyecto
│   ├── changes/                 # Cambios activos
│   │   ├── mi-cambio/
│   │   │   ├── .openspec.yaml   # Metadatos del cambio
│   │   │   ├── proposal.md      # Qué y por qué
│   │   │   ├── design.md        # Cómo
│   │   │   ├── specs/           # Especificaciones delta
│   │   │   │   └── capability/
│   │   │   │       └── spec.md
│   │   │   └── tasks.md         # Lista de tareas
│   │   └── archive/             # Cambios completados
│   │       └── 2026-03-08-mi-cambio/
│   └── specs/                   # Especificaciones principales
│       └── capability/
│           └── spec.md
└── .claude/
    ├── commands/opsx/           # Comandos de workflow
    └── skills/                  # Skills de OpenSpec
```

## Artefactos

### proposal.md
**Propósito:** Define QUÉ y POR QUÉ

**Secciones típicas:**
- Objetivo
- Motivación / Por qué
- Alcance
- No-objetivos
- Impacto

### design.md
**Propósito:** Define CÓMO

**Secciones típicas:**
- Arquitectura general
- Componentes
- Decisiones técnicas
- Integraciones
- Consideraciones (seguridad, performance, escalabilidad)
- Alternativas consideradas

### specs/
**Propósito:** Requisitos detallados por capacidad

**Contenido típico:**
- Comportamientos esperados
- Casos de uso
- Validaciones
- Reglas de negocio
- Formato de datos
- Códigos de error

### tasks.md
**Propósito:** Lista de tareas implementables

**Formato:**
```markdown
- [ ] Tarea pendiente
- [x] Tarea completada
```

**Buenas prácticas:**
- Tareas de 1-2 horas máximo
- Descripción clara y accionable
- Orden lógico de implementación

## Configuración (config.yaml)

```yaml
schema: spec-driven

# Contexto del proyecto (opcional pero recomendado)
context: |
  Stack tecnológico: TypeScript, React, Node.js, PostgreSQL
  Usamos conventional commits
  Seguimos Airbnb style guide
  Tests con Jest
  Dominio: plataforma de e-commerce
  
# Reglas por artefacto (opcional)
rules:
  proposal:
    - Mantén las propuestas bajo 500 palabras
    - Siempre incluye una sección "No-objetivos"
    - Documenta el impacto en usuarios
  design:
    - Incluye diagramas cuando sea relevante
    - Documenta alternativas consideradas
    - Especifica dependencias externas
  tasks:
    - Divide las tareas en bloques de máximo 2 horas
    - Cada tarea debe ser verificable
    - Incluye tests en tareas separadas
  specs:
    - Usa ejemplos concretos
    - Documenta todos los casos de error
    - Incluye validaciones de datos
```

## Flujos de Trabajo

### Flujo Básico
```
1. /opsx:propose <nombre>
2. /opsx:apply
3. /opsx:archive
```

### Flujo con Exploración
```
1. /opsx:explore <idea>
2. /opsx:propose <nombre>
3. /opsx:apply
4. /opsx:archive
```

### Flujo con Revisión
```
1. /opsx:propose <nombre>
2. [Revisar y ajustar artefactos]
3. /opsx:apply
4. /opsx:archive
```

### Flujo Adaptativo
```
1. /opsx:propose <nombre>
2. /opsx:apply
3. [Pausa por problema de diseño]
4. [Actualizar design.md]
5. /opsx:apply (continuar)
6. /opsx:archive
```

## Atajos y Tips

### Nombres de Cambios
Usa kebab-case:
- ✅ `agregar-autenticacion-oauth`
- ✅ `fix-sesion-timeout-bug`
- ✅ `refactor-auth-layer`
- ❌ `Agregar Autenticación OAuth`
- ❌ `fix_session_bug`

### Tareas Efectivas

❌ Malo (muy grande):
```markdown
- [ ] Implementar sistema de autenticación completo
```

✅ Bueno (específico y pequeño):
```markdown
- [ ] Instalar dependencias de OAuth (passport, passport-google)
- [ ] Crear modelo de usuario en base de datos
- [ ] Implementar endpoint POST /auth/login
- [ ] Implementar endpoint GET /auth/callback
- [ ] Agregar middleware de autenticación
- [ ] Crear tests de integración para flujo OAuth
```

### Exploración Efectiva

Usa `/opsx:explore` cuando:
- No estás seguro del mejor enfoque
- Necesitas comparar opciones (Redis vs Memcached)
- Quieres entender código existente antes de modificar
- Necesitas visualizar arquitectura compleja
- Tienes preguntas sobre trade-offs

NO uses `/opsx:explore` cuando:
- Ya sabes exactamente qué hacer
- Es un cambio trivial
- Solo necesitas implementar algo obvio

### Actualizar Artefactos

Puedes editar artefactos en cualquier momento:

```bash
# Editar directamente
vim openspec/changes/mi-cambio/design.md

# O pedir a Claude
"Actualiza design.md para usar Redis en lugar de Memcached"
```

Claude leerá el diseño actualizado en el próximo `/opsx:apply`.

## Patrones de Uso

### Feature Nueva
```
/opsx:propose agregar-<feature>
```

### Bug Fix
```
/opsx:explore <descripción del bug>
/opsx:propose fix-<bug>
```

### Refactor
```
/opsx:explore <código a refactorizar>
/opsx:propose refactor-<componente>
```

### Integración Externa
```
/opsx:explore integración con <servicio>
/opsx:propose agregar-<servicio>-integration
```

## Solución de Problemas

### "No encuentro mi cambio"
```bash
openspec list --json
```

### "Claude no genera artefactos"
Verifica `openspec/config.yaml`:
```yaml
schema: spec-driven  # Debe estar presente
```

### "Quiero cambiar el diseño a mitad de implementación"
Edita `design.md` directamente y continúa con `/opsx:apply`.

### "Las tareas no están claras"
Edita `tasks.md` para hacerlas más específicas antes de `/opsx:apply`.

### "Quiero pausar la implementación"
Simplemente detén `/opsx:apply`. Puedes continuar después con el mismo comando.

### "Cometí un error en un artefacto"
Edita el archivo directamente o pide a Claude que lo actualice.

## Mejores Prácticas

### 1. Contexto del Proyecto
Siempre configura `context` en `config.yaml`:
```yaml
context: |
  Stack: Python, FastAPI, PostgreSQL
  Estilo: PEP 8, type hints obligatorios
  Tests: pytest con coverage > 80%
  Dominio: sistema de gestión hospitalaria
```

### 2. Cambios Pequeños
Divide features grandes en cambios pequeños:
- ✅ `notification-core`, `notification-email`, `notification-sms`
- ❌ `notification-system-complete`

### 3. Tareas Atómicas
Cada tarea debe ser:
- Pequeña (1-2 horas)
- Específica
- Verificable
- Independiente (cuando sea posible)

### 4. Specs Claras
Incluye en specs:
- Ejemplos concretos
- Todos los casos de error
- Validaciones de datos
- Formato de request/response

### 5. Diseño Documentado
En design.md incluye:
- Diagramas (ASCII art)
- Decisiones técnicas con justificación
- Alternativas consideradas
- Trade-offs

### 6. Exploración Antes de Complejidad
Si el cambio es complejo, usa `/opsx:explore` primero.

### 7. Archiva Regularmente
No acumules cambios completados. Archívalos con `/opsx:archive`.

### 8. Actualiza Durante Implementación
Si descubres algo durante `/opsx:apply`, actualiza los artefactos.

## Atajos de Teclado (en Claude)

```
/opsx:explore    → Modo exploración
/opsx:propose    → Crear propuesta
/opsx:apply      → Implementar
/opsx:archive    → Archivar
```

## Formato de Markdown

### Diagramas ASCII
```
┌─────────────────────────────────────────┐
│              TÍTULO                     │
├─────────────────────────────────────────┤
│                                         │
│   ┌────────┐         ┌────────┐        │
│   │ Comp A │────────▶│ Comp B │        │
│   └────────┘         └────────┘        │
│                                         │
└─────────────────────────────────────────┘
```

### Bloques de Código
````markdown
```python
def ejemplo():
    return "código"
```
````

### Tablas
```markdown
| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Valor 1   | Valor 2   | Valor 3   |
```

### Checkboxes (tasks.md)
```markdown
- [ ] Tarea pendiente
- [x] Tarea completada
```

## Recursos

- **Documentación oficial:** [openspec.dev](https://openspec.dev)
- **Guía completa:** `docs/guia-openspec-claude.md`
- **Ejemplos prácticos:** `docs/ejemplos-openspec.md`
- **Cambios archivados:** `openspec/changes/archive/`

## Cheatsheet de Comandos

```bash
# Inicializar OpenSpec
openspec init

# Listar cambios
openspec list
openspec list --json

# Estado de cambio
openspec status --change <nombre>
openspec status --change <nombre> --json

# Crear cambio
openspec new change <nombre>

# Instrucciones
openspec instructions <artifact> --change <nombre>
openspec instructions apply --change <nombre>

# Ver ayuda
openspec --help
openspec <command> --help
```

## Workflow Completo Ejemplo

```bash
# 1. Explorar (opcional)
/opsx:explore sistema de notificaciones

# 2. Proponer
/opsx:propose agregar-notificaciones-email

# 3. Revisar artefactos generados (opcional)
cat openspec/changes/agregar-notificaciones-email/proposal.md
cat openspec/changes/agregar-notificaciones-email/design.md
cat openspec/changes/agregar-notificaciones-email/tasks.md

# 4. Ajustar si es necesario (opcional)
vim openspec/changes/agregar-notificaciones-email/design.md

# 5. Implementar
/opsx:apply

# 6. Verificar estado
openspec status --change agregar-notificaciones-email

# 7. Archivar
/opsx:archive

# 8. Verificar archivo
ls openspec/changes/archive/
```

## Recordatorios

- ✅ Usa `/opsx:explore` para pensar, no para implementar
- ✅ Divide features grandes en cambios pequeños
- ✅ Mantén tareas pequeñas (1-2 horas)
- ✅ Actualiza artefactos durante implementación si es necesario
- ✅ Archiva cambios completados regularmente
- ✅ Configura `context` en `config.yaml`
- ❌ No implementes código en modo explore
- ❌ No crees cambios gigantes con 50+ tareas
- ❌ No ignores problemas de diseño durante implementación
- ❌ No acumules cambios sin archivar

---

**¡Empieza con un cambio pequeño y experimenta el flujo!**
