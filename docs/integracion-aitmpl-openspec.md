mponentes:**
   ```bash
   npx claude-code-templates@latest
   ```

4. **Configura MCPs para AWS:**
   Edita `.claude/settings/mcp.json` con tus credenciales

---

**¡Ahora tienes OpenSpec (estructura) + AITMPL (herramientas) trabajando juntos en Claude Code!**
e-code-templates](https://github.com/davila7/claude-code-templates)
- **OpenSpec Docs:** `docs/guia-openspec-claude.md`

## Próximos Pasos

1. **Instala componentes básicos:**
   ```bash
   npx claude-code-templates@latest --agent development-team/backend-developer --yes
   npx claude-code-templates@latest --command testing/generate-tests --yes
   ```

2. **Prueba el flujo integrado:**
   ```bash
   /opsx:propose test-integracion-aitmpl
   /generate-tests
   /opsx:apply
   /opsx:archive
   ```

3. **Explora más co"Command not found" en Claude Code

Verifica que los comandos estén en `.claude/commands/`:
```bash
ls -la .claude/commands/
```

### "Agent not responding"

Verifica que los agents estén instalados:
```bash
ls -la .claude/agents/
```

### MCPs no funcionan

Ejecuta health check:
```bash
npx claude-code-templates@latest --health-check
```

## Recursos

- **AITMPL Website:** [aitmpl.com](https://www.aitmpl.com)
- **AITMPL Docs:** [docs.aitmpl.com](https://docs.aitmpl.com)
- **AITMPL GitHub:** [github.com/davila7/claud             # Verificar
/opsx:archive                    # Finalizar
```

### Refactor
```bash
/opsx:explore refactor-<X>       # Planear
@code-reviewer "revisa X"        # Revisar código actual
/opsx:propose refactor-<X>       # Proponer
/opsx:apply                      # Implementar
/optimize-bundle                 # Optimizar
/opsx:archive                    # Finalizar
```

### Revisión de Código
```bash
@code-reviewer "revisa src/lambda/core/"
/check-security
/generate-docs
```

## Troubleshooting

### llo de Feature
```bash
/opsx:propose <nombre>           # Crear estructura
@backend-developer "ayuda con X" # Consultar experto
/opsx:apply                      # Implementar
/generate-tests                  # Tests automáticos
/opsx:archive                    # Finalizar
```

### Bug Fix
```bash
/opsx:explore <bug>              # Investigar
@security-auditor "analiza X"    # Si es de seguridad
/opsx:propose fix-<bug>          # Proponer fix
/opsx:apply                      # Implementar
/check-security      Stack

Para AWS CDK, configura el MCP de AWS en `.claude/settings/mcp.json`:

```json
{
  "mcpServers": {
    "aws": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-aws"],
      "env": {
        "AWS_PROFILE": "tu-perfil",
        "AWS_REGION": "us-east-1"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "tu-token"
      }
    }
  }
}
```

## Comandos Rápidos para tu Día a Día

### Desarroepetitivas
- MCPs para integraciones externas

### 3. Combina Ambos

```
OpenSpec (Estructura) + AITMPL (Herramientas) = Flujo Óptimo
```

**Ejemplo:**
```bash
# OpenSpec: Estructura el cambio
/opsx:propose agregar-autenticacion-oauth

# AITMPL: Valida la arquitectura
@aws-architect "Revisa el diseño de OAuth con Cognito"

# OpenSpec: Implementa
/opsx:apply

# AITMPL: Genera tests
/generate-tests

# AITMPL: Verifica seguridad
/check-security

# OpenSpec: Archiva
/opsx:archive
```

### 4. Configura MCPs para tu
npx claude-code-templates@latest --health-check
```

### 4. Plugin Dashboard

Ver y gestionar todos los plugins instalados:

```bash
npx claude-code-templates@latest --plugins
```

## Mejores Prácticas

### 1. Usa OpenSpec para Estructura

OpenSpec es tu **framework de proceso**:
- Define QUÉ construir (proposal)
- Define CÓMO construir (design)
- Define PASOS (tasks)

### 2. Usa AITMPL para Herramientas

AITMPL son tus **herramientas especializadas**:
- Agents para expertise específico
- Commands para tareas rtu uso de Claude Code:

```bash
npx claude-code-templates@latest --analytics
```

Esto abre un dashboard con:
- Sesiones activas
- Uso de tokens
- Métricas de rendimiento
- Historial de comandos

### 2. Conversation Monitor

Ver respuestas de Claude en tiempo real (útil para debugging):

```bash
# Local
npx claude-code-templates@latest --chats

# Remoto (con Cloudflare Tunnel)
npx claude-code-templates@latest --chats --tunnel
```

### 3. Health Check

Verificar que todo está configurado correctamente:

```bashfeature-name>`
2. Revisar artefactos generados
3. Ajustar si es necesario

## Fase 3: Implementación
1. `/opsx:apply`
2. `/generate-tests` - Generar tests automáticamente
3. `/check-security` - Verificar seguridad
4. `@code-reviewer` - Revisar código

## Fase 4: Optimización
1. `/optimize-bundle` - Optimizar código
2. `/generate-docs` - Generar documentación

## Fase 5: Finalización
1. `/opsx:archive`
2. Commit y push a GitHub
```

## Herramientas Adicionales de AITMPL

### 1. Analytics Dashboard

Monitorea evisión de seguridad con /check-security
    - Tareas de máximo 2 horas
```

### 2. Crear Workflow Personalizado

Crea `.claude/workflows/feature-completo.md`:

```markdown
---
name: Feature Completo
description: Workflow completo para nueva feature con OpenSpec + AITMPL
---

# Workflow: Feature Completo

## Fase 1: Exploración
1. `/opsx:explore <feature-name>`
2. `@aws-architect` - Validar arquitectura AWS
3. `@security-auditor` - Revisar implicaciones de seguridad

## Fase 2: Propuesta
1. `/opsx:propose <AITMPL
  Agents disponibles: backend-developer, aws-architect, security-auditor
  Commands: /generate-tests, /check-security, /optimize-bundle
  MCPs: GitHub, AWS

rules:
  proposal:
    - Incluir consideraciones de seguridad (HIPAA compliance)
    - Documentar costos de AWS
    - Especificar límites de Lambda
  design:
    - Usar patrones de AWS Well-Architected
    - Incluir diagramas de arquitectura
    - Documentar políticas IAM
  tasks:
    - Incluir generación de tests con /generate-tests
    - Incluir rdeveloper   # Experto en backend TypeScript
@aws-architect       # Experto en AWS/CDK
@security-auditor    # Experto en seguridad
@code-reviewer       # Revisor de código
```

## Configuración Específica para tu Proyecto

### 1. Actualizar openspec/config.yaml

```yaml
schema: spec-driven

context: |
  Stack: TypeScript, AWS CDK, Lambda, DynamoDB, API Gateway
  Framework: AWS CDK v2
  Runtime: Node.js 18+
  Tests: Jest
  Linting: ESLint + Prettier
  Dominio: Sistema de salud (HealthNova)
  
  # Integraciones 
# 7. Archivar
/opsx:archive
```

## Comandos Combinados

### OpenSpec (Estructura)
```bash
/opsx:explore    # Explorar ideas
/opsx:propose    # Crear propuesta estructurada
/opsx:apply      # Implementar tareas
/opsx:archive    # Archivar cambio
```

### AITMPL (Herramientas)
```bash
/generate-tests      # Generar tests automáticamente
/optimize-bundle     # Optimizar código
/check-security      # Auditoría de seguridad
/generate-docs       # Generar documentación
```

### Agents (Especialistas)
```bash
@backend-r
/opsx:propose refactor-auth-layer

# 4. Implementar
/opsx:apply

# 5. Optimizar bundle
/optimize-bundle

# 6. Archivar
/opsx:archive
```

### Escenario 3: Bug Fix con Security Audit

```bash
# 1. Investigar bug
/opsx:explore fix-session-vulnerability

# 2. Auditoría de seguridad
@security-auditor "Analiza vulnerabilidades en sesiones"

# 3. Proponer fix
/opsx:propose fix-session-vulnerability

# 4. Implementar
/opsx:apply

# 5. Verificar seguridad
/check-security

# 6. Generar documentación
/generate-docs
itectura de pagos con Lambda y DynamoDB"

# 3. Proponer con OpenSpec
/opsx:propose agregar-endpoint-pagos

# 4. Generar tests automáticamente
/generate-tests

# 5. Implementar con OpenSpec
/opsx:apply

# 6. Revisar seguridad antes de archivar
/check-security

# 7. Archivar
/opsx:archive
```

### Escenario 2: Refactor con Code Review

```bash
# 1. Explorar código existente
/opsx:explore refactor-auth-layer

# 2. Pedir revisión de código
@code-reviewer "Revisa src/lambda/core/authorizer/"

# 3. Proponer refacto  # ← Nuevo: Hooks de AITMPL
│   └── settings/
│       └── mcp.json         # ← Actualizado: MCPs de AITMPL
├── openspec/                # ← Existente: OpenSpec
│   ├── config.yaml
│   ├── changes/
│   └── specs/
└── docs/                    # ← Existente: Documentación
```

## Flujo de Trabajo Integrado

### Escenario 1: Nueva Feature con OpenSpec + AITMPL

```bash
# 1. Explorar con OpenSpec
/opsx:explore agregar-endpoint-pagos

# 2. Usar agent de AWS para validar arquitectura
@aws-architect "Revisa esta arqucurity-auditor/
│   ├── commands/
│   │   ├── opsx/            # ← Existente: OpenSpec
│   │   │   ├── explore.md
│   │   │   ├── propose.md
│   │   │   ├── apply.md
│   │   │   └── archive.md
│   │   └── aitmpl/          # ← Nuevo: Commands de AITMPL
│   │       ├── generate-tests.md
│   │       ├── optimize-bundle.md
│   │       └── check-security.md
│   ├── skills/
│   │   ├── openspec-*/      # ← Existente: OpenSpec skills
│   │   └── aitmpl-*/        # ← Nuevo: AITMPL skills
│   ├── hooks/             esql-integration --yes
```

### 4. Hooks para Automatización

```bash
# Validación pre-commit
npx claude-code-templates@latest --hook git/pre-commit-validation --yes

# Acciones post-completion
npx claude-code-templates@latest --hook workflow/post-completion-actions --yes
```

## Estructura Resultante

Después de instalar AITMPL, tu proyecto tendrá:

```
healthnova-backend/
├── .claude/
│   ├── agents/              # ← Nuevo: Agents de AITMPL
│   │   ├── backend-developer/
│   │   ├── aws-architect/
│   │   └── seemplates@latest --command security/check-security --yes

# Generar documentación
npx claude-code-templates@latest --command documentation/generate-docs --yes
```

### 3. MCPs para Integraciones

```bash
# GitHub (para PRs, issues, etc.)
npx claude-code-templates@latest --mcp development/github-integration --yes

# AWS (para CDK y servicios)
npx claude-code-templates@latest --mcp cloud/aws-integration --yes

# PostgreSQL/DynamoDB (si usas bases de datos)
npx claude-code-templates@latest --mcp database/postgr@latest --agent infrastructure/aws-architect --yes

# Security Auditor
npx claude-code-templates@latest --agent security/security-auditor --yes

# Code Reviewer
npx claude-code-templates@latest --agent development-tools/code-reviewer --yes
```

### 2. Commands Útiles

```bash
# Generar tests automáticamente
npx claude-code-templates@latest --command testing/generate-tests --yes

# Optimizar bundle
npx claude-code-templates@latest --command performance/optimize-bundle --yes

# Revisar seguridad
npx claude-code-tpecíficos para tu stack
npx claude-code-templates@latest \
  --agent development-team/backend-developer \
  --agent infrastructure/aws-architect \
  --command testing/generate-tests \
  --command performance/optimize-bundle \
  --mcp development/github-integration \
  --yes
```

## Componentes Recomendados para tu Stack

### 1. Agents Esenciales

```bash
# Backend TypeScript Developer
npx claude-code-templates@latest --agent development-team/backend-developer --yes

# AWS/CDK Architect
npx claude-code-templatesmplates@latest
```

Esto te mostrará un menú para seleccionar componentes.

### Opción 2: Instalación Directa

```bash
# Instalar componentes es* - Configuraciones optimizadas de Claude Code
- 🪝 **Hooks** - Automatizaciones y triggers
- 🎨 **Skills** - Capacidades reutilizables

## Tu Stack Actual

```
Backend TypeScript + AWS CDK
    ↓
OpenSpec (ya instalado)
    ↓
Claude Code (terminal)
    ↓
+ AITMPL (a integrar)
```

## Instalación de AITMPL

### Opción 1: Instalación Interactiva (Recomendada)

```bash
# Navega a tu proyecto
cd /Users/tenonde/Projects/personal/healthnova/healthnova-backend

# Ejecuta el instalador interactivo
npx claude-code-temo combinar AITMPL (Claude Code Templates) con tu flujo de OpenSpec para maximizar tu productividad en terminal.

## ¿Qué es AITMPL?

[AITMPL](https://www.aitmpl.com) es una colección de componentes para Claude Code que incluye:

- 🤖 **Agents** - Especialistas en dominios específicos (security auditor, React optimizer, etc.)
- ⚡ **Commands** - Comandos slash personalizados (`/generate-tests`, `/optimize-bundle`)
- 🔌 **MCPs** - Integraciones con servicios externos (GitHub, PostgreSQL, AWS)
- ⚙️ **Settings*# Integración de AITMPL con OpenSpec en Claude Code (Terminal)

Esta guía te muestra có