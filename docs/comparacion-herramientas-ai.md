# Comparación de Herramientas AI para Desarrollo

Guía para entender las diferencias entre OpenSpec, AITMPL, OpenCode y Claude Code, y cómo usarlas juntas.

## Resumen Rápido

| Herramienta | Tipo | Propósito | Dónde se usa |
|-------------|------|-----------|--------------|
| **OpenSpec** | Framework de proceso | Estructura tu desarrollo (propuesta → diseño → implementación) | Cualquier editor/terminal |
| **AITMPL** | Colección de templates | Agents, commands y MCPs para Claude Code | Claude Code (terminal) |
| **OpenCode** | Agente AI completo | Alternativa open-source a Claude Code | Terminal/Desktop/IDE |
| **Claude Code** | Agente AI oficial | Herramienta de Anthropic para desarrollo | Terminal |

## ¿Qué es cada herramienta?

### OpenSpec
**Framework de proceso de desarrollo**

```
Propuesta → Diseño → Especificaciones → Tareas → Implementación → Archivo
```

- No es un agente AI
- Es una metodología estructurada
- Genera documentación automática
- Funciona con cualquier herramienta AI

**Archivos:**
- `openspec/config.yaml`
- `openspec/changes/`
- `.claude/commands/opsx/`

### AITMPL
**Colección de componentes para Claude Code**

- Agents especializados (@aws-architect, @security-auditor)
- Commands slash (/generate-tests, /check-security)
- MCPs (integraciones con GitHub, AWS, etc.)
- Skills reutilizables

**Archivos:**
- `.claude/agents/`
- `.claude/commands/aitmpl/`
- `.claude/settings/mcp.json`

### OpenCode
**Agente AI open-source**

- Alternativa a Claude Code
- Soporta 75+ modelos (Claude, GPT, Gemini, locales)
- Terminal UI nativo
- Arquitectura cliente-servidor
- 2 agents principales: Build y Plan
- 2 subagents: General y Explore

**Instalación:**
```bash
npm i -g opencode-ai@latest
# o
brew install anomalyco/tap/opencode
```

### Claude Code
**Agente AI oficial de Anthropic**

- Herramienta oficial de Anthropic
- Usa modelos Claude
- Terminal UI
- Integración con MCP

## Comparación Detallada

### OpenCode vs Claude Code

| Característica | OpenCode | Claude Code |
|----------------|----------|-------------|
| **Open Source** | ✅ Sí | ❌ No |
| **Modelos** | 75+ (Claude, GPT, Gemini, locales) | Solo Claude |
| **Costo** | Depende del modelo elegido | Depende del plan Claude |
| **LSP Support** | ✅ Built-in | ⚠️ Limitado |
| **Multi-sesión** | ✅ Sí | ⚠️ Limitado |
| **Desktop App** | ✅ Sí (beta) | ❌ No |
| **Arquitectura** | Cliente-servidor | Monolítico |
| **Agents** | Build, Plan, General, Explore | Configurable |
| **Extensibilidad** | ✅ Alta | ✅ Alta (via MCP) |

### OpenSpec vs OpenCode/Claude Code

OpenSpec NO es un agente AI, es complementario:

| Aspecto | OpenSpec | OpenCode/Claude Code |
|---------|----------|----------------------|
| **Tipo** | Framework de proceso | Agente AI |
| **Función** | Estructura el desarrollo | Ejecuta el desarrollo |
| **Documentación** | ✅ Automática | ❌ Manual |
| **Artefactos** | proposal, design, specs, tasks | Código directamente |
| **Historial** | Cambios archivados | Conversaciones |
| **Planificación** | ✅ Estructurada | ⚠️ Ad-hoc |

## Escenarios de Uso

### Escenario 1: Solo OpenCode (sin OpenSpec)

**Cuándo:** Cambios rápidos, prototipos, exploración

```bash
opencode

# En OpenCode
> Agrega un endpoint GET /health
> Implementa autenticación JWT
> Refactoriza el módulo de usuarios
```

**Pros:**
- Rápido
- Directo
- Sin overhead

**Contras:**
- Sin documentación estructurada
- Sin historial de decisiones
- Difícil de revisar después

### Escenario 2: OpenSpec + Claude Code (tu setup actual)

**Cuándo:** Features medianas/grandes, trabajo estructurado

```bash
# En Claude Code
/opsx:explore agregar-pagos-stripe
/opsx:propose agregar-pagos-stripe
/opsx:apply
/opsx:archive
```

**Pros:**
- Proceso estructurado
- Documentación automática
- Historial de decisiones
- Artefactos claros

**Contras:**
- Más overhead
- Requiere disciplina

### Escenario 3: OpenSpec + OpenCode

**Cuándo:** Quieres open-source o usar modelos alternativos

```bash
# Instalar OpenCode
npm i -g opencode-ai@latest

# Configurar para usar OpenSpec
# (requiere configuración manual)
```

**Pros:**
- Open source
- Múltiples modelos
- Proceso estructurado
- Control total

**Contras:**
- Configuración inicial
- OpenSpec no está integrado nativamente

### Escenario 4: OpenSpec + AITMPL + Claude Code (setup completo)

**Cuándo:** Proyectos grandes, equipos, producción

```bash
# En Claude Code con AITMPL
/opsx:explore agregar-pagos-stripe
@aws-architect "Revisa arquitectura"
/opsx:propose agregar-pagos-stripe
/opsx:apply
/generate-tests
/check-security
/opsx:archive
```

**Pros:**
- Máxima productividad
- Herramientas especializadas
- Proceso estructurado
- Documentación completa

**Contras:**
- Más complejo
- Curva de aprendizaje

## ¿Cómo se Acoplaría OpenCode a tu Proyecto?

### Opción A: Reemplazar Claude Code con OpenCode

```
Antes:
OpenSpec + AITMPL + Claude Code

Después:
OpenSpec + OpenCode
```

**Pasos:**

1. **Instalar OpenCode:**
   ```bash
   npm i -g opencode-ai@latest
   ```

2. **Configurar modelo:**
   ```bash
   opencode config
   # Selecciona: Anthropic Claude (o cualquier otro)
   ```

3. **Migrar comandos OpenSpec:**
   
   Los comandos `/opsx:*` NO funcionarán directamente en OpenCode porque son específicos de Claude Code.
   
   Necesitarías:
   - Crear agents personalizados en OpenCode
   - Replicar la funcionalidad de OpenSpec manualmente
   - O usar OpenSpec CLI directamente

4. **Configurar agents para tu stack:**
   
   Crea `.opencode/agents/aws-architect.md`:
   ```markdown
   ---
   description: AWS and CDK architecture expert
   mode: subagent
   model: anthropic/claude-sonnet-4-20250514
   tools:
     write: false
     edit: false
   ---
   
   You are an AWS and CDK expert. Review architectures for:
   - AWS Well-Architected Framework compliance
   - Cost optimization
   - Security best practices
   - Scalability considerations
   ```

**Pros:**
- Open source
- Múltiples modelos
- Más control

**Contras:**
- Pierdes integración nativa con AITMPL
- Pierdes comandos `/opsx:*`
- Requiere reconfiguración

### Opción B: Usar OpenCode en Paralelo

```
Proyecto:
├── OpenSpec (estructura)
├── Claude Code (desarrollo principal con AITMPL)
└── OpenCode (exploración, modelos alternativos)
```

**Cuándo usar cada uno:**

**Claude Code + OpenSpec + AITMPL:**
- Features principales
- Trabajo estructurado
- Cuando necesitas agents especializados

**OpenCode:**
- Exploración rápida
- Probar modelos alternativos (GPT, Gemini, locales)
- Cuando Claude está caído
- Análisis de código (agent Plan)

**Ejemplo de flujo:**

```bash
# 1. Explorar con OpenCode (rápido, modelo local)
opencode
> Analiza la estructura de src/lambda/

# 2. Planificar con Claude Code + OpenSpec
claude-code
/opsx:explore agregar-feature-x

# 3. Implementar con Claude Code + AITMPL
/opsx:propose agregar-feature-x
@aws-architect "Revisa diseño"
/opsx:apply
/generate-tests

# 4. Revisar con OpenCode (modelo diferente para segunda opinión)
opencode
> Revisa el código que acabo de generar
```

### Opción C: Mantener Setup Actual (Recomendado)

```
OpenSpec + AITMPL + Claude Code
```

**Por qué:**
- Ya está configurado
- Funciona bien
- Integración nativa
- Documentación completa

**Cuándo considerar OpenCode:**
- Si Anthropic bloquea tu región
- Si quieres usar modelos locales
- Si necesitas más control
- Si quieres contribuir a open source

## Configuración de OpenCode para TypeScript + CDK

Si decides usar OpenCode, aquí está la configuración recomendada:

### 1. Instalar

```bash
npm i -g opencode-ai@latest
```

### 2. Configurar

Crea `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.3,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "temperature": 0.1,
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    },
    "aws-architect": {
      "description": "AWS and CDK architecture expert",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.2,
      "prompt": "{file:./prompts/aws-architect.txt}",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    },
    "security-auditor": {
      "description": "Security expert for HIPAA compliance",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "temperature": 0.1,
      "prompt": "{file:./prompts/security-auditor.txt}",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    }
  }
}
```

### 3. Crear Prompts

Crea `~/.config/opencode/prompts/aws-architect.txt`:

```
You are an AWS and CDK architecture expert specializing in:
- AWS Well-Architected Framework
- CDK best practices
- Lambda optimization
- DynamoDB design
- API Gateway configuration
- IAM policies
- Cost optimization

Stack context:
- TypeScript
- AWS CDK v2
- Lambda (Node.js 18+)
- DynamoDB
- API Gateway
- Domain: Healthcare (HIPAA compliance required)

Review architectures for:
1. Security and compliance
2. Cost efficiency
3. Scalability
4. Performance
5. Operational excellence
```

Crea `~/.config/opencode/prompts/security-auditor.txt`:

```
You are a security expert specializing in:
- HIPAA compliance
- AWS security best practices
- Application security
- Data protection
- Authentication and authorization

Focus on:
1. HIPAA compliance requirements
2. Data encryption (at rest and in transit)
3. Access control and IAM
4. Audit logging
5. Vulnerability assessment
6. Secure coding practices

Always consider healthcare data sensitivity.
```

### 4. Uso

```bash
# Iniciar OpenCode
opencode

# Usar agent Build (default)
> Agrega endpoint POST /patients

# Cambiar a agent Plan (Tab)
[Tab]
> Analiza la estructura del proyecto

# Invocar subagent
> @aws-architect Revisa esta arquitectura Lambda + DynamoDB

> @security-auditor Verifica cumplimiento HIPAA
```

## Integración OpenCode + OpenSpec (Manual)

OpenCode NO tiene integración nativa con OpenSpec, pero puedes usarlos juntos:

### Flujo Manual

```bash
# 1. Crear cambio OpenSpec
openspec new change agregar-feature-x

# 2. Generar artefactos con OpenCode
opencode
> Lee openspec/changes/agregar-feature-x/
> Genera proposal.md basado en: [descripción]
> Genera design.md con arquitectura AWS
> Genera tasks.md con pasos implementables

# 3. Implementar con OpenCode
> Implementa tarea 1 de tasks.md
> Implementa tarea 2 de tasks.md

# 4. Archivar
openspec status --change agregar-feature-x
mv openspec/changes/agregar-feature-x openspec/changes/archive/2026-03-08-agregar-feature-x
```

### Crear Wrapper Scripts

Puedes crear scripts para simular `/opsx:*`:

`~/bin/opsx-propose`:
```bash
#!/bin/bash
CHANGE_NAME=$1
openspec new change "$CHANGE_NAME"
opencode --prompt "Generate OpenSpec artifacts for change: $CHANGE_NAME"
```

Pero esto es más trabajo que usar Claude Code con integración nativa.

## Recomendación Final

### Para tu proyecto actual (healthnova-backend):

**Mantén tu setup actual:**
```
OpenSpec + AITMPL + Claude Code
```

**Razones:**
1. Ya está configurado y funcionando
2. Integración nativa con OpenSpec
3. AITMPL funciona perfectamente
4. Documentación completa disponible
5. Menos fricción

**Considera OpenCode solo si:**
- Anthropic bloquea tu región
- Quieres experimentar con modelos locales
- Necesitas features específicas de OpenCode
- Quieres contribuir a open source

### Si decides probar OpenCode:

**Úsalo en paralelo:**
- Claude Code para trabajo principal
- OpenCode para exploración y segunda opinión

**No migres completamente** a menos que tengas una razón específica.

## Recursos

- **OpenCode:** [opencode.ai](https://opencode.ai)
- **OpenCode Docs:** [opencode.ai/docs](https://opencode.ai/docs)
- **OpenCode GitHub:** [github.com/anomalyco/opencode](https://github.com/anomalyco/opencode)
- **Claude Code:** Herramienta oficial de Anthropic
- **OpenSpec:** `docs/guia-openspec-claude.md`
- **AITMPL:** `docs/integracion-aitmpl-openspec.md`

---

**Resumen:** OpenCode es una excelente alternativa open-source a Claude Code, pero para tu caso actual, mantener Claude Code + OpenSpec + AITMPL es la mejor opción por su integración nativa y menor fricción.
