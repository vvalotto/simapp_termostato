# Ecosistema de Claude Code

## Visión General

Claude Code es un **agente de desarrollo autónomo** que opera desde la terminal con acceso al sistema de archivos y capacidad de ejecutar comandos. Su ecosistema se compone de siete componentes principales que extienden y controlan sus capacidades.

```
┌─────────────────────────────────────────────────────────┐
│                    TU TERMINAL                          │
│                                                         │
│   Vos ──► /comando ──► CLAUDE CODE (agente principal)   │
│                              │                          │
│                              ▼                          │
│                    ┌─────────────────┐                  │
│                    │    SKILLS       │ ◄── Consulta     │
│                    │ (cómo hacerlo)  │     antes de     │
│                    └─────────────────┘     actuar       │
│                              │                          │
│                              ▼                          │
│           ┌─────────┬───────┴───────┬─────────┐        │
│           ▼         ▼               ▼         ▼        │
│      Subagente  Subagente      Subagente   (tareas)    │
│                              │                          │
│                              ▼                          │
│                    ┌─────────────────┐                  │
│                    │     HOOKS       │ ◄── Se disparan  │
│                    │ (automatización)│     en eventos   │
│                    └─────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

---

## Resumen de Componentes

| Componente | Pregunta que responde |
|------------|----------------------|
| **CLAUDE.md** | ¿Qué debe saber Claude sobre este proyecto? |
| **Slash Commands** | ¿Cómo le doy instrucciones rápidas? |
| **Skills** | ¿Cómo sabe hacer bien algo específico? |
| **Hooks** | ¿Cómo automatizo acciones en el flujo? |
| **Subagentes** | ¿Cómo delega tareas complejas? |
| **MCP** | ¿Cómo se conecta con servicios externos? |
| **Modos de permisos** | ¿Cuánta autonomía le doy? |

---

## 1. CLAUDE.md — La Memoria del Proyecto

### Qué es
Archivo markdown que Claude Code **lee automáticamente** al iniciar sesión en un directorio. Funciona como instrucciones persistentes que no hay que repetir.

### Ubicación (jerárquica, se combinan)
```
~/.claude/CLAUDE.md          → Global (todos los proyectos)
~/proyecto/CLAUDE.md         → Raíz del proyecto
~/proyecto/src/CLAUDE.md     → Específico de subcarpeta
```

### Contenido típico
- Descripción y propósito del proyecto
- Stack tecnológico y versiones
- Convenciones de código
- Arquitectura y estructura de carpetas
- Comandos frecuentes (build, test, deploy)
- Reglas críticas ("nunca modificar X sin confirmación")

### Comandos relacionados
- `/init` → Genera o mejora el CLAUDE.md analizando el proyecto
- `#` → Agrega instrucciones al CLAUDE.md durante la conversación

### Ejemplo
```markdown
# ISSE Termostato - Contexto del Proyecto

## Descripción
Sistema de control termostático para dispositivo médico. 
Debe cumplir IEC 62304 Clase B.

## Stack
- Lenguaje: C (C99)
- Microcontrolador: STM32F103
- RTOS: FreeRTOS 10.4

## Convenciones
- Prefijos: `drv_` para drivers, `app_` para aplicación
- Funciones públicas en PascalCase, privadas en snake_case

## Reglas críticas
- NUNCA modificar `/drivers/safety_monitor.c` sin confirmación
- Todo código nuevo debe tener test unitario asociado

## Comandos útiles
- Build: `cmake --build build/`
- Tests: `ctest --test-dir build/`
```

---

## 2. Slash Commands — Interfaz de Control Rápido

### Qué son
Comandos invocados con `/` que ejecutan acciones frecuentes o flujos predefinidos sin escribir prompts largos.

### Tipos

| Tipo | Ejemplos |
|------|----------|
| **Built-in** | `/help`, `/init`, `/compact`, `/clear`, `/config`, `/cost` |
| **Personalizados** | Los que vos creás |

### Ubicación
```
~/.claude/commands/          → Globales
./proyecto/.claude/commands/ → Del proyecto
```

El nombre del archivo `.md` se convierte en el comando:
```
.claude/commands/review.md  →  /review
```

### Estructura
```markdown
# .claude/commands/compliance-check.md

Realiza verificación de cumplimiento IEC 62304:

1. Identificar archivos modificados con `git diff`
2. Clasificar según módulo
3. Verificar trazabilidad
4. Generar reporte en `/docs/compliance_reports/`
```

### Argumentos
Usar `$ARGUMENTS` o placeholders numerados (`$1`, `$2`):

```markdown
# .claude/commands/fix-issue.md

Analiza y corrige el issue de GitHub: $ARGUMENTS

1. Usar `gh issue view $ARGUMENTS` para ver detalles
2. Implementar corrección
3. Crear commit descriptivo
```

**Uso:** `/fix-issue 42`

### Nota importante
El slash command es un **prompt**, no un script. Claude interpreta las instrucciones y decide qué ejecutar. Si necesitás ejecución directa sin intervención de Claude, usá **Hooks**.

---

## 3. Skills — Conocimiento Especializado

### Qué son
Carpetas con instrucciones y mejores prácticas que Claude consulta antes de ejecutar ciertas tareas. Le enseñan *cómo hacer bien* algo específico.

### Diferencia con Slash Commands

| Aspecto | Slash Command | Skill |
|---------|---------------|-------|
| Estructura | Un solo archivo `.md` | Carpeta con `SKILL.md` + archivos de soporte |
| Invocación | Solo manual | Manual o automática |
| Contenido | Qué hacer | Cómo hacerlo bien |

### Ubicación
```
~/.claude/skills/           → Globales
.claude/skills/             → Del proyecto
/mnt/skills/public/         → Built-in de Anthropic
```

### Estructura
```
.claude/skills/
└── iec62304-design-doc/
    ├── SKILL.md           → Instrucciones principales (requerido)
    ├── templates/         → Plantillas
    ├── examples/          → Ejemplos de output
    └── checklists/        → Material de referencia
```

### Anatomía de SKILL.md
```markdown
---
name: iec62304-design-doc
description: Genera documentación de diseño conforme a IEC 62304. 
             Usar para documentar módulos o preparar auditorías.
---

# Documentación de Diseño IEC 62304

## Antes de generar
1. Leer plantilla en `templates/`
2. Revisar ejemplo en `examples/`

## Estructura obligatoria
1. Identificación (ID, versión, fecha)
2. Propósito y alcance
3. Arquitectura
4. Diseño detallado
5. Verificación

## Output
Usar plantilla `templates/software_design_spec.md`
```

### Control de invocación (frontmatter)

| Campo | Efecto |
|-------|--------|
| `disable-model-invocation: true` | Solo el usuario puede invocarlo |
| `user-invocable: false` | Solo Claude puede usarlo (no aparece como `/comando`) |

---

## 4. Hooks — Automatización por Eventos

### Qué son
Scripts que se ejecutan **automáticamente** cuando ocurren ciertos eventos. A diferencia de slash commands, no requieren invocación manual.

### Diferencia clave

| Aspecto | Slash Command | Hook |
|---------|---------------|------|
| Quién dispara | Vos, manualmente | Un evento, automáticamente |
| Claude decide | Sí | No, ejecución directa |

### Eventos disponibles

| Hook | Cuándo se dispara |
|------|-------------------|
| `PreToolUse` | Antes de que Claude use una herramienta |
| `PostToolUse` | Después de que Claude usa una herramienta |
| `Notification` | Cuando Claude envía una notificación |
| `Stop` | Cuando Claude termina de responder |

### Configuración
En `.claude/settings.json` o `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(*.c)",
        "hooks": [
          {
            "type": "command",
            "command": "clang-format -i $file"
          },
          {
            "type": "command",
            "command": "cppcheck --enable=warning $file"
          }
        ]
      }
    ]
  }
}
```

### Variables disponibles
- `$file` → Ruta del archivo afectado

### Ejemplo: Log de cambios críticos
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write(src/drivers/safety_monitor.c)",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date): Modificación en safety_monitor.c\" >> ./logs/critical_changes.log"
          }
        ]
      }
    ]
  }
}
```

### Cuándo usar cada uno

| Necesidad | Solución |
|-----------|----------|
| Correr tests cuando yo diga | Slash command |
| Formatear automáticamente al guardar | Hook |
| Trackear tiempo manualmente | Slash command |
| Loguear cada modificación automáticamente | Hook |

---

## 5. Subagentes — Delegación Especializada

### Qué son
Instancias separadas de Claude con contexto aislado, system prompt propio, y herramientas restringidas. Permiten delegar tareas a "especialistas".

### Características

| Aspecto | Detalle |
|---------|---------|
| Contexto | Ventana propia, aislada de la conversación principal |
| System prompt | Instrucciones específicas de su rol |
| Herramientas | Solo las que vos definís |
| Modelo | Configurable (Sonnet, Haiku, etc.) |

### Por qué usarlos
1. **Evitar contaminación de contexto** — Explorar 50 archivos no llena tu conversación principal
2. **Especialización** — Prompts específicos producen mejores resultados
3. **Paralelismo** — Múltiples análisis simultáneos

### Ubicación
```
~/.claude/agents/          → Globales
.claude/agents/            → Del proyecto
```

### Estructura
```markdown
# .claude/agents/safety-auditor.md
---
name: safety-auditor
description: Audita código embebido para cumplimiento IEC 62304.
tools: Read, Grep, Glob
model: sonnet
---

Sos un auditor especializado en software médico IEC 62304.

## Alcance
- Verificar manejo de errores en paths críticos
- Identificar condiciones de carrera
- Validar rangos de entrada

## Output
- Clasificación de riesgo (Alto/Medio/Bajo)
- Referencia a requisito afectado
- Recomendación de mitigación
```

### Invocación

**Automática:** Claude decide basándose en la `description`.
```
Vos: "Revisá la seguridad del módulo de temperatura"
Claude: (detecta que es auditoría → delega a safety-auditor)
```

**Explícita:**
```
Vos: "Usá el subagente safety-auditor para analizar el driver SPI"
```

### Flujo de ejecución
```
Agente principal recibe tarea compleja
            │
            ▼
    Delega a subagentes especializados
            │
     ┌──────┼──────┐
     ▼      ▼      ▼
   Sub-A  Sub-B  Sub-C  (trabajan en paralelo)
     │      │      │
     └──────┼──────┘
            │
            ▼
    Agente principal integra resultados
```

### Restricción
Los subagentes **no pueden crear otros subagentes**. Jerarquía de un solo nivel.

### Subagentes built-in

| Subagente | Función |
|-----------|---------|
| **Plan** | Planificación de tareas complejas |
| **Explore** | Exploración de codebase (usa Haiku) |

---

## 6. MCP (Model Context Protocol) — Conectores Externos

### Qué es
Protocolo que permite a Claude Code conectarse con servicios externos: GitHub, Jira, Confluence, bases de datos, APIs, SonarQube, Figma, etc.

### Analogía
Son como drivers o plugins que extienden las capacidades más allá del sistema de archivos local.

### Ejemplo de uso
Conexiones con Atlassian, repositorios GitMCP, SonarQube para análisis de calidad.

---

## 7. Modos de Permisos — Control de Autonomía

### Qué es
Configuración que controla cuánta autonomía tiene Claude Code: desde pedir confirmación para cada acción hasta ejecutar de forma completamente autónoma.

### Analogía
Como configurar un CI/CD: modo "solo mostrar qué haría" vs "deployar directo a producción".

---

## Tabla Comparativa Final

| Componente | Qué es | Dónde vive | Quién lo invoca |
|------------|--------|------------|-----------------|
| **CLAUDE.md** | Memoria del proyecto | `./CLAUDE.md` | Automático al iniciar |
| **Slash Command** | Prompt reutilizable | `.claude/commands/` | Vos, con `/comando` |
| **Skill** | Conocimiento + archivos de soporte | `.claude/skills/` | Vos o Claude |
| **Hook** | Script automático | `.claude/settings.json` | Evento del sistema |
| **Subagente** | Instancia especializada | `.claude/agents/` | Vos o Claude |
| **MCP** | Conector externo | Configuración | Claude cuando necesita |
| **Permisos** | Nivel de autonomía | Settings | Vos configurás |

---

## Flujo de Decisión: ¿Qué usar?

```
¿Necesito que Claude sepa algo siempre?
    └─► CLAUDE.md

¿Quiero ejecutar un flujo cuando yo diga?
    └─► Slash Command

¿Necesito templates, ejemplos, archivos de soporte?
    └─► Skill

¿Quiero que algo pase automáticamente ante un evento?
    └─► Hook

¿La tarea requiere análisis aislado o especializado?
    └─► Subagente

¿Necesito conectar con un servicio externo?
    └─► MCP
```

---

*Documento generado como material de referencia y divulgación.*
*Basado en documentación oficial de Anthropic y mejores prácticas de la comunidad.*
