# Documentación de OpenSpec

Bienvenido a la documentación completa de OpenSpec con Claude. Esta guía está diseñada para programadores que están iniciando en el mundo de las especificaciones y el desarrollo estructurado.

## 📚 Documentos Disponibles

### 1. [Guía de OpenSpec con Claude](./guia-openspec-claude.md)
**Empieza aquí si eres nuevo en OpenSpec**

Guía completa que cubre:
- ¿Qué es OpenSpec y por qué usarlo?
- Estructura del proyecto
- Los 4 comandos principales (`explore`, `propose`, `apply`, `archive`)
- Artefactos explicados (proposal, design, specs, tasks)
- Flujos de trabajo típicos
- Consejos y mejores prácticas
- Ejemplo completo paso a paso

**Ideal para:** Primera lectura, entender conceptos fundamentales

### 2. [Ejemplos Prácticos](./ejemplos-openspec.md)
**Lee esto después de la guía principal**

Ejemplos reales de uso:
- Agregar una nueva API endpoint
- Refactorizar código existente
- Integrar servicios externos (AWS Rekognition)
- Fix de bugs complejos
- Features grandes divididas en cambios pequeños
- Actualizar diseño durante implementación
- Patrones comunes de uso

**Ideal para:** Aprender con ejemplos concretos, ver patrones en acción

### 3. [Referencia Rápida](./referencia-rapida-openspec.md)
**Consulta rápida cuando ya conoces OpenSpec**

Cheatsheet con:
- Tabla de comandos principales
- Comandos CLI
- Estructura de directorios
- Formato de artefactos
- Flujos de trabajo
- Atajos y tips
- Mejores prácticas
- Solución de problemas

**Ideal para:** Consulta rápida, recordar sintaxis, resolver dudas puntuales

### 4. [Preguntas Frecuentes (FAQ)](./faq-openspec.md)
**Consulta cuando tengas dudas específicas**

Respuestas a preguntas comunes:
- Conceptos básicos
- Uso de comandos
- Manejo de artefactos
- Gestión de tareas
- Cambios y archivo
- Configuración
- Integración con Claude
- Problemas comunes
- Casos de uso específicos

**Ideal para:** Resolver dudas específicas, troubleshooting

### 5. [Diagramas y Visualizaciones](./diagramas-openspec.md)
**Guía visual para entender OpenSpec**

Diagramas ASCII que muestran:
- Ciclo de vida de un cambio
- Estructura de directorios
- Flujo de comandos
- Relación entre artefactos
- Sincronización de specs
- Comparación con flujo tradicional
- Timeline de proyecto

**Ideal para:** Aprendizaje visual, entender flujos, referencia rápida

## 🚀 Ruta de Aprendizaje Recomendada

### Nivel 1: Principiante (Día 1)
1. Lee la [Guía de OpenSpec](./guia-openspec-claude.md) completa
2. Revisa los [Diagramas](./diagramas-openspec.md) para visualizar el flujo
3. Ejecuta `openspec init` en un proyecto de prueba
4. Crea tu primer cambio simple:
   ```
   /opsx:propose mi-primer-cambio
   /opsx:apply
   /opsx:archive
   ```

### Nivel 2: Intermedio (Semana 1)
1. Lee los [Ejemplos Prácticos](./ejemplos-openspec.md)
2. Experimenta con `/opsx:explore` para una idea compleja
3. Crea un cambio real en tu proyecto
4. Configura `context` en `openspec/config.yaml`

### Nivel 3: Avanzado (Mes 1)
1. Divide una feature grande en múltiples cambios
2. Actualiza artefactos durante implementación
3. Usa la [Referencia Rápida](./referencia-rapida-openspec.md) como consulta
4. Consulta el [FAQ](./faq-openspec.md) para casos específicos

## 🎯 Casos de Uso por Documento

### "Quiero entender qué es OpenSpec"
→ [Guía de OpenSpec](./guia-openspec-claude.md) - Sección "¿Qué es OpenSpec?"
→ [Diagramas](./diagramas-openspec.md) - "Ciclo de Vida de un Cambio"

### "Quiero ver un ejemplo completo"
→ [Guía de OpenSpec](./guia-openspec-claude.md) - Sección "Ejemplo Completo"
→ [Ejemplos Prácticos](./ejemplos-openspec.md) - Cualquier ejemplo

### "¿Cómo uso el comando X?"
→ [Referencia Rápida](./referencia-rapida-openspec.md) - Sección "Comandos Principales"
→ [Diagramas](./diagramas-openspec.md) - "Flujo de Comandos"

### "¿Cuándo debo usar /opsx:explore?"
→ [FAQ](./faq-openspec.md) - Sección "¿Cuándo debo usar /opsx:explore?"

### "¿Cómo manejo features grandes?"
→ [Ejemplos Prácticos](./ejemplos-openspec.md) - Ejemplo 5
→ [FAQ](./faq-openspec.md) - Sección "¿Cómo manejo features muy grandes?"

### "¿Cómo escribo buenas tareas?"
→ [Referencia Rápida](./referencia-rapida-openspec.md) - Sección "Tareas Efectivas"
→ [FAQ](./faq-openspec.md) - Sección "¿Cómo deben ser las tareas?"

### "Tengo un error o problema"
→ [Referencia Rápida](./referencia-rapida-openspec.md) - Sección "Solución de Problemas"
→ [FAQ](./faq-openspec.md) - Sección "Problemas Comunes"

### "Quiero visualizar el flujo"
→ [Diagramas](./diagramas-openspec.md) - Todos los diagramas

## 📖 Estructura de la Documentación

```
docs/
├── README.md                          # Este archivo (índice)
├── guia-openspec-claude.md           # Guía completa (EMPIEZA AQUÍ)
├── ejemplos-openspec.md              # Ejemplos prácticos
├── referencia-rapida-openspec.md     # Cheatsheet
├── faq-openspec.md                   # Preguntas frecuentes
└── diagramas-openspec.md             # Visualizaciones y diagramas
```

## 🔗 Enlaces Rápidos

### Comandos Principales
- `/opsx:explore` - Modo exploración (pensar, investigar)
- `/opsx:propose` - Crear propuesta con artefactos
- `/opsx:apply` - Implementar tareas
- `/opsx:archive` - Archivar cambio completado

### Archivos Clave
- `openspec/config.yaml` - Configuración del proyecto
- `openspec/changes/<nombre>/proposal.md` - Qué y por qué
- `openspec/changes/<nombre>/design.md` - Cómo
- `openspec/changes/<nombre>/tasks.md` - Lista de tareas
- `openspec/changes/<nombre>/specs/` - Especificaciones

### Comandos CLI
```bash
openspec init                          # Inicializar OpenSpec
openspec list                          # Listar cambios
openspec status --change <nombre>      # Ver estado
openspec new change <nombre>           # Crear cambio
```

## 💡 Tips Rápidos

1. **Empieza pequeño:** Tu primer cambio debe ser simple
2. **Configura contexto:** Agrega tu stack en `config.yaml`
3. **Explora cuando dudes:** Usa `/opsx:explore` para ideas complejas
4. **Tareas pequeñas:** 1-2 horas máximo por tarea
5. **Archiva regularmente:** No acumules cambios completados
6. **Actualiza artefactos:** Si descubres algo durante implementación
7. **Divide features grandes:** Múltiples cambios pequeños > un cambio gigante
8. **Usa diagramas:** Visualiza el flujo para entender mejor

## 🆘 Ayuda Rápida

### "No sé por dónde empezar"
```
1. Lee la guía completa
2. Revisa los diagramas
3. Ejecuta: openspec init
4. Crea un cambio simple: /opsx:propose mi-primer-cambio
5. Implementa: /opsx:apply
6. Archiva: /opsx:archive
```

### "Tengo un error"
1. Revisa [Solución de Problemas](./referencia-rapida-openspec.md#solución-de-problemas)
2. Consulta [Problemas Comunes](./faq-openspec.md#problemas-comunes)
3. Pregunta a Claude directamente

### "Quiero un ejemplo específico"
Busca en [Ejemplos Prácticos](./ejemplos-openspec.md):
- Ejemplo 1: API Endpoint
- Ejemplo 2: Refactor
- Ejemplo 3: Integración Externa
- Ejemplo 4: Bug Fix
- Ejemplo 5: Feature Grande
- Ejemplo 6: Actualización de Diseño

### "Quiero ver el flujo visualmente"
Revisa [Diagramas](./diagramas-openspec.md):
- Ciclo de vida completo
- Flujo de comandos
- Relación entre artefactos
- Comparación con flujo tradicional

## 🎓 Recursos Adicionales

- **Documentación oficial:** [openspec.dev](https://openspec.dev)
- **Cambios archivados:** `openspec/changes/archive/` (ejemplos reales de tu proyecto)
- **Skills de Claude:** `.claude/skills/openspec-*/` (implementación técnica)
- **Comandos de Claude:** `.claude/commands/opsx/` (definiciones de comandos)

## 📝 Contribuir a la Documentación

Si encuentras errores o quieres agregar ejemplos:
1. Edita los archivos Markdown directamente
2. Commitea los cambios
3. Comparte con tu equipo

## 🌟 Filosofía de OpenSpec

> "Piensa antes de codificar. Documenta mientras construyes. Aprende de lo que hiciste."

OpenSpec no es solo una herramienta, es una forma de trabajar que:
- Reduce retrabajos
- Mejora la calidad
- Facilita la colaboración
- Preserva el conocimiento
- Hace el desarrollo más predecible

## 🚦 Próximos Pasos

1. **Si eres nuevo:** Lee la [Guía Completa](./guia-openspec-claude.md)
2. **Si quieres visualizar:** Revisa los [Diagramas](./diagramas-openspec.md)
3. **Si ya leíste la guía:** Crea tu primer cambio
4. **Si ya usaste OpenSpec:** Explora los [Ejemplos Prácticos](./ejemplos-openspec.md)
5. **Si tienes dudas:** Consulta el [FAQ](./faq-openspec.md)
6. **Si necesitas referencia rápida:** Usa el [Cheatsheet](./referencia-rapida-openspec.md)

---

**¡Bienvenido al mundo de OpenSpec! Empieza con un cambio pequeño y experimenta el flujo.**

¿Preguntas? Pregunta a Claude: "Explícame [concepto] de OpenSpec"
