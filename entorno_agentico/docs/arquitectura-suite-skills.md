# Arquitectura de Suite de Skills - Reingeniería de implement-us

**Fecha:** 2026-01-19
**Autor:** Victor Valotto
**Versión:** 1.0
**Estado:** Diseño Propuesto

---

## 1. Contexto

Rediseño del skill monolítico `/implement-us` en una suite modular de skills componibles que permitan workflows flexibles.

### 1.1 Precondiciones del Proyecto

1. El trabajo está dirigido por **tickets** (tareas o historias de usuario)
2. Existe una **definición de Arquitectura de referencia** y criterios de diseño

### 1.2 Objetivo

Transformar las 9 fases secuenciales de `/implement-us` en skills atómicos que:
- Se ejecuten independientemente
- Compartan estado mediante archivos JSON
- Se compongan en workflows configurables (YAML)
- Tracken tiempo automáticamente
- Resuelvan dependencias automáticamente

---

## 2. Decisiones de Diseño

| Aspecto | Decisión | Opción Elegida |
|---------|----------|----------------|
| **Granularidad** | ¿Cómo dividir el skill? | **A) Por fase** (9 skills atómicos) |
| **Comunicación** | ¿Cómo comparten datos? | **A) Estado compartido** (`.claude/state/`) |
| **Workflows** | ¿Shortcuts predefinidos? | **B) Configurables en YAML** |
| **Tracking** | ¿Cómo trackear tiempo? | **B) Automático por skill** |
| **Dependencias** | ¿Validar orden de ejecución? | **C) Auto-ejecución** |
| **Alcance /implement** | ¿Qué implementa? | **A) TODO** (todos los componentes) |
| **Caso de uso principal** | ¿Qué optimizar? | **Feature completa** (como `/implement-us` actual) |
| **Preferencia usuario** | ¿Automático o manual? | **Workflows automáticos** |
| **Flexibilidad vs simplicidad** | ¿Cuántos skills? | **Balance** (5-7 skills clave) |
| **Compatibilidad** | ¿Mantener `/implement-us`? | **No, reemplazar completamente** |

---

## 3. Arquitectura Propuesta

### 3.1 Estructura de Directorios

```
.claude/
├── skills/
│   ├── core/                           # Skills atómicos (9 fases)
│   │   ├── validate-context.md         # Fase 0
│   │   ├── generate-bdd.md             # Fase 1
│   │   ├── generate-plan.md            # Fase 2
│   │   ├── implement-components.md     # Fase 3
│   │   ├── test-unit.md                # Fase 4
│   │   ├── test-integration.md         # Fase 5
│   │   ├── validate-bdd.md             # Fase 6
│   │   ├── validate-quality.md         # Fase 7
│   │   ├── update-docs.md              # Fase 8
│   │   └── generate-report.md          # Fase 9
│   │
│   ├── workflows/                      # Workflows predefinidos (YAML)
│   │   ├── full-feature.yaml           # Feature completa (9 fases)
│   │   ├── quick-fix.yaml              # Bugfix rápido (sin BDD/plan)
│   │   ├── plan-only.yaml              # Solo validar + planificar
│   │   ├── implement-only.yaml         # Solo implementar
│   │   └── test-only.yaml              # Solo testing
│   │
│   └── config/
│       ├── skill-config.json           # Config global de skills
│       └── workflow-engine.json        # Config del motor de workflows
│
├── state/                              # Estado compartido por US
│   ├── US-001-context.json
│   ├── US-002-context.json
│   └── ...
│
├── context/                            # Outputs intermedios de skills
│   ├── US-001-validation.json
│   ├── US-001-bdd.json
│   ├── US-001-plan.json
│   └── ...
│
└── tracking/                           # Tracking de tiempo
    ├── US-001-tracking.json
    ├── US-002-tracking.json
    └── ...
```

---

## 4. Separación de Documentación

### 4.1 Filosofía: Localización de Documentación

La documentación de la suite de skills debe estar **separada** de la documentación específica del proyecto para mantener modularidad y reutilización.

### 4.2 Estructura Propuesta

```
/CLAUDE.md                          # Proyecto ISSE_Simuladores
                                    # (arquitectura MVC, PyQt6, simuladores)
                                    # Hace referencia a ↓

/.claude/
├── SKILLS.md                       # 🆕 Documentación de la suite de skills
│                                   # (genérica, reutilizable)
├── skills/
│   ├── core/
│   ├── workflows/
│   └── config/
└── ...
```

### 4.3 Contenido de `/CLAUDE.md` (raíz del proyecto)

Sigue siendo específico del proyecto, pero agrega una sección de referencia a la suite:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema HIL (Hardware-in-the-Loop) con tres aplicaciones PyQt6...

[... contenido actual del proyecto ...]

---

## Skills Suite

Este proyecto utiliza una **suite de skills modular** para la implementación de Historias de Usuario.

**Documentación completa:** `.claude/SKILLS.md`

### Uso Rápido

```bash
# Implementar feature completa
/workflow full-feature US-001

# Bugfix rápido
/workflow quick-fix US-008

# Skill individual
/validate-context US-001
/generate-plan US-001
```

**Para detalles de la arquitectura de skills, workflows configurables, y estado compartido, ver `.claude/SKILLS.md`**
```

### 4.4 Contenido de `/.claude/SKILLS.md` (nuevo, genérico)

Documentación completa de la suite de skills, independiente del proyecto específico:

```markdown
# Skills Suite - Documentación

**Versión:** 1.0
**Fecha:** 2026-01-19

Esta suite de skills proporciona un framework modular para implementación asistida de tickets/historias de usuario.

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Prerequisitos del Proyecto](#prerequisitos)
3. [Arquitectura](#arquitectura)
4. [Skills Atómicos](#skills-atómicos)
5. [Workflows](#workflows)
6. [Estado Compartido](#estado-compartido)
7. [Tracking de Tiempo](#tracking)
8. [Uso](#uso)
9. [Configuración](#configuración)
10. [Extensibilidad](#extensibilidad)

---

## Introducción

La suite de skills descompone el proceso de implementación en **9 fases atómicas** que pueden ejecutarse independientemente o componerse en **workflows configurables**.

### Filosofía de Diseño

- **Modularidad**: Cada skill hace una cosa y la hace bien
- **Composabilidad**: Skills se combinan en workflows
- **Estado explícito**: El progreso se guarda en JSON
- **Tracking automático**: Tiempo medido sin intervención
- **Dependencias automáticas**: Los prerequisitos se resuelven solos

---

## Prerequisitos del Proyecto

Para usar esta suite, tu proyecto debe cumplir:

### 1. Tickets/Historias de Usuario

- Documentadas en archivos Markdown o gestor (Jira, etc.)
- Formato esperado:
  ```markdown
  # US-001: Título

  Como [rol]
  Quiero [acción]
  Para [beneficio]

  ## Criterios de Aceptación
  - [ ] Criterio 1
  - [ ] Criterio 2
  ```

### 2. Arquitectura de Referencia

- Documentada en `docs/arquitectura.md`, `docs/ADR-*.md`, o sección en `CLAUDE.md`
- Define: patrones, convenciones, estructura de directorios

### 3. Estándares de Calidad

- Quality gates configurados (Pylint, coverage, CC, MI)
- Herramientas instaladas (pytest, pylint, radon, etc.)

[... resto de la documentación de skills, workflows, etc ...]
```

### 4.5 Beneficios de esta Separación

| Aspecto | Beneficio |
|---------|-----------|
| **Modularidad** | La suite es reutilizable en otros proyectos |
| **Claridad** | Cada CLAUDE.md tiene un propósito claro |
| **Mantenibilidad** | Cambios en la suite no afectan docs del proyecto |
| **Portabilidad** | Puedes copiar `.claude/` a otro proyecto y funciona |
| **Versionado** | La suite puede evolucionar independientemente |

### 4.6 Flujo de Lectura para Claude

1. Claude lee `/CLAUDE.md` primero (contexto del proyecto)
2. Si detecta uso de skills, lee `/.claude/SKILLS.md` (suite genérica)
3. Los skills individuales leen ambos para contexto completo

---

## 5. Sistema de Estado Compartido

### 4.1 Archivo de Contexto: `.claude/state/US-XXX-context.json`

```json
{
  "metadata": {
    "us_id": "US-001",
    "us_title": "Ver temperatura ambiente",
    "us_points": 3,
    "producto": "ux_termostato",
    "workflow": "full-feature",
    "created_at": "2026-01-19T10:00:00Z",
    "updated_at": "2026-01-19T11:30:00Z",
    "status": "in_progress"
  },

  "phases": {
    "validate_context": {
      "skill": "validate-context",
      "status": "completed",
      "started_at": "2026-01-19T10:00:00Z",
      "completed_at": "2026-01-19T10:02:00Z",
      "auto_approved": true,
      "outputs": {
        "validation_file": ".claude/context/US-001-validation.json",
        "has_user_story": true,
        "has_architecture": true,
        "has_standards": true
      }
    },

    "generate_bdd": {
      "skill": "generate-bdd",
      "status": "completed",
      "started_at": "2026-01-19T10:02:00Z",
      "completed_at": "2026-01-19T10:07:00Z",
      "auto_approved": false,
      "outputs": {
        "feature_file": "tests/features/US-001-ver-temperatura.feature",
        "scenarios_count": 3
      }
    },

    "generate_plan": {
      "skill": "generate-plan",
      "status": "completed",
      "started_at": "2026-01-19T10:07:00Z",
      "completed_at": "2026-01-19T10:12:00Z",
      "auto_approved": false,
      "outputs": {
        "plan_file": "docs/plans/US-001-plan.md",
        "components": [
          {"name": "DisplayModelo", "type": "modelo", "estimated_minutes": 10},
          {"name": "DisplayVista", "type": "vista", "estimated_minutes": 30},
          {"name": "DisplayControlador", "type": "controlador", "estimated_minutes": 40}
        ],
        "total_estimated_minutes": 135
      }
    },

    "implement_components": {
      "skill": "implement-components",
      "status": "in_progress",
      "started_at": "2026-01-19T10:15:00Z",
      "completed_at": null,
      "auto_approved": false,
      "outputs": {
        "files_created": [
          "app/presentacion/paneles/display/modelo.py",
          "app/presentacion/paneles/display/vista.py"
        ],
        "current_component": "DisplayControlador",
        "progress": "2/3"
      }
    },

    "test_unit": {"skill": "test-unit", "status": "pending"},
    "test_integration": {"skill": "test-integration", "status": "pending"},
    "validate_bdd": {"skill": "validate-bdd", "status": "pending"},
    "validate_quality": {"skill": "validate-quality", "status": "pending"},
    "update_docs": {"skill": "update-docs", "status": "pending"},
    "generate_report": {"skill": "generate-report", "status": "pending"}
  },

  "dependencies": {
    "generate_bdd": ["validate_context"],
    "generate_plan": ["validate_context", "generate_bdd"],
    "implement_components": ["generate_plan"],
    "test_unit": ["implement_components"],
    "test_integration": ["test_unit"],
    "validate_bdd": ["test_integration"],
    "validate_quality": ["validate_bdd"],
    "update_docs": ["validate_quality"],
    "generate_report": ["update_docs"]
  },

  "tracking": {
    "tracking_file": ".claude/tracking/US-001-tracking.json",
    "total_elapsed_seconds": 5400,
    "effective_seconds": 5100,
    "paused_seconds": 300
  }
}
```

### 4.2 Estados Posibles

- `pending` - No iniciado
- `in_progress` - En ejecución
- `completed` - Completado exitosamente
- `failed` - Falló con error
- `skipped` - Saltado (workflow lo permite)

---

## 6. Skills Atómicos

### 6.1 Skill: validate-context (Fase 0)

**Comando:** `/validate-context US-001`

**Propósito:** Validar prerequisitos (US, arquitectura, estándares)

**Prerequisitos:** Ninguno (primer skill)

**Proceso:**
1. Crear archivo de estado compartido si no existe
2. Inicializar tracking automático
3. Buscar historia de usuario
4. Validar arquitectura de referencia
5. Validar estándares de calidad
6. Generar reporte de validación
7. Actualizar estado compartido
8. Registrar tracking

**Outputs:**
- `.claude/state/US-001-context.json` (creado/actualizado)
- `.claude/context/US-001-validation.json`

**Duración típica:** 2-5 minutos

---

### 6.2 Skill: generate-bdd (Fase 1)

**Comando:** `/generate-bdd US-001`

**Propósito:** Generar escenarios BDD en formato Gherkin

**Prerequisitos:** `validate-context` completado

**Proceso:**
1. Leer estado compartido
2. Verificar dependencias (auto-ejecuta si falta)
3. Leer criterios de aceptación de la US
4. Generar escenarios Given/When/Then
5. Escribir archivo `.feature`
6. Solicitar aprobación del usuario
7. Actualizar estado compartido
8. Registrar tracking

**Outputs:**
- `tests/features/US-001-{nombre}.feature`
- `.claude/context/US-001-bdd.json`

**Duración típica:** 10-15 minutos

---

### 6.3 Skill: generate-plan (Fase 2)

**Comando:** `/generate-plan US-001`

**Propósito:** Generar plan de implementación detallado

**Prerequisitos:** `validate-context`, `generate-bdd` completados

**Proceso:**
1. Leer estado compartido
2. Verificar dependencias
3. Analizar US según arquitectura de referencia
4. Identificar componentes a crear (MVC, servicios, etc.)
5. Generar checklist de tareas con estimaciones
6. Escribir plan en Markdown
7. Solicitar aprobación del usuario
8. Actualizar estado compartido
9. Registrar tracking

**Outputs:**
- `docs/plans/US-001-plan.md`
- `.claude/context/US-001-plan.json`

**Duración típica:** 15-20 minutos

---

### 6.4 Skill: implement-components (Fase 3)

**Comando:** `/implement-components US-001`

**Propósito:** Implementar todos los componentes del plan

**Prerequisitos:** `generate-plan` completado

**Proceso:**
1. Leer estado compartido
2. Verificar dependencias
3. Cargar plan de implementación
4. Por cada componente:
   - Mostrar contexto
   - Generar código base
   - Solicitar aprobación
   - Escribir archivo
   - Actualizar progreso
   - Registrar tarea en tracking
5. Actualizar estado compartido
6. Registrar tracking de fase

**Outputs:**
- Archivos de código (modelos, vistas, controladores, servicios)
- `.claude/context/US-001-implementation.json`

**Duración típica:** 60-120 minutos

---

### 6.5 Skill: test-unit (Fase 4)

**Comando:** `/test-unit US-001`

**Propósito:** Implementar y ejecutar tests unitarios

**Prerequisitos:** `implement-components` completado

**Proceso:**
1. Leer estado compartido
2. Verificar dependencias
3. Por cada componente implementado:
   - Generar tests unitarios
   - Ejecutar tests
   - Validar coverage
4. Actualizar estado compartido
5. Registrar tracking

**Outputs:**
- Archivos de tests unitarios
- Reporte de coverage
- `.claude/context/US-001-test-unit.json`

**Duración típica:** 30-60 minutos

---

### 6.6 Skill: test-integration (Fase 5)

**Comando:** `/test-integration US-001`

**Propósito:** Implementar y ejecutar tests de integración

**Prerequisitos:** `test-unit` completado

**Outputs:**
- Archivos de tests de integración
- `.claude/context/US-001-test-integration.json`

**Duración típica:** 20-30 minutos

---

### 6.7 Skill: validate-bdd (Fase 6)

**Comando:** `/validate-bdd US-001`

**Propósito:** Ejecutar escenarios BDD y validar que pasan

**Prerequisitos:** `test-integration` completado

**Outputs:**
- Reporte de ejecución BDD
- `.claude/context/US-001-bdd-results.json`

**Duración típica:** 10-15 minutos

---

### 6.8 Skill: validate-quality (Fase 7)

**Comando:** `/validate-quality US-001`

**Propósito:** Validar quality gates (Pylint, CC, MI, Coverage)

**Prerequisitos:** `validate-bdd` completado

**Proceso:**
1. Ejecutar Pylint
2. Calcular métricas (CC, MI con radon)
3. Validar coverage
4. Comparar vs umbrales
5. Generar reporte JSON

**Outputs:**
- `quality/reports/US-001-quality.json`
- `.claude/context/US-001-quality.json`

**Duración típica:** 5-10 minutos

---

### 6.9 Skill: update-docs (Fase 8)

**Comando:** `/update-docs US-001`

**Propósito:** Actualizar documentación (plan, arquitectura, CHANGELOG)

**Prerequisitos:** `validate-quality` completado

**Outputs:**
- Plan actualizado con resultados reales
- CHANGELOG.md actualizado
- Arquitectura actualizada (si aplica)

**Duración típica:** 5-10 minutos

---

### 6.10 Skill: generate-report (Fase 9)

**Comando:** `/generate-report US-001`

**Propósito:** Generar reporte final de implementación

**Prerequisitos:** `update-docs` completado

**Proceso:**
1. Leer estado compartido completo
2. Leer tracking completo
3. Generar reporte en Markdown
4. Finalizar tracking
5. Marcar US como completada

**Outputs:**
- `docs/reports/US-001-report.md`
- `docs/reports/US-001-tracking-report.md` (opcional)

**Duración típica:** 5 minutos

---

## 7. Workflows Configurables

### 7.1 Workflow: Full Feature

**Archivo:** `.claude/skills/workflows/full-feature.yaml`

```yaml
name: "full-feature"
version: "1.0"
description: "Implementación completa de feature con BDD, tests y quality gates"

config:
  tracking_enabled: true
  auto_track: true
  stop_on_error: true
  allow_skip: false

steps:
  - id: "validate"
    skill: "validate-context"
    phase: 0
    description: "Validar contexto (US, arquitectura, estándares)"
    required: true
    auto_approve: true
    timeout_minutes: 5
    on_error: "stop"

  - id: "bdd"
    skill: "generate-bdd"
    phase: 1
    description: "Generar escenarios BDD (Gherkin)"
    required: true
    auto_approve: false
    depends_on: ["validate"]
    timeout_minutes: 15
    on_error: "stop"

  - id: "plan"
    skill: "generate-plan"
    phase: 2
    description: "Generar plan de implementación detallado"
    required: true
    auto_approve: false
    depends_on: ["validate", "bdd"]
    timeout_minutes: 20
    on_error: "stop"

  - id: "implement"
    skill: "implement-components"
    phase: 3
    description: "Implementar componentes (MVC completo)"
    required: true
    auto_approve: false
    depends_on: ["plan"]
    timeout_minutes: 120
    on_error: "stop"
    params:
      mode: "guided"

  - id: "test_unit"
    skill: "test-unit"
    phase: 4
    description: "Implementar y ejecutar tests unitarios"
    required: true
    auto_approve: true
    depends_on: ["implement"]
    timeout_minutes: 60
    on_error: "stop"
    params:
      target_coverage: 95

  - id: "test_integration"
    skill: "test-integration"
    phase: 5
    description: "Implementar y ejecutar tests de integración"
    required: true
    auto_approve: true
    depends_on: ["test_unit"]
    timeout_minutes: 30
    on_error: "stop"

  - id: "validate_bdd"
    skill: "validate-bdd"
    phase: 6
    description: "Ejecutar escenarios BDD"
    required: true
    auto_approve: true
    depends_on: ["test_integration"]
    timeout_minutes: 15
    on_error: "stop"

  - id: "quality"
    skill: "validate-quality"
    phase: 7
    description: "Validar quality gates (Pylint, CC, MI, Coverage)"
    required: true
    auto_approve: true
    depends_on: ["validate_bdd"]
    timeout_minutes: 10
    on_error: "stop"
    params:
      gates:
        - pylint
        - coverage
        - cyclomatic_complexity
        - maintainability_index

  - id: "docs"
    skill: "update-docs"
    phase: 8
    description: "Actualizar documentación"
    required: true
    auto_approve: true
    depends_on: ["quality"]
    timeout_minutes: 10
    on_error: "warn"

  - id: "report"
    skill: "generate-report"
    phase: 9
    description: "Generar reporte final"
    required: true
    auto_approve: true
    depends_on: ["docs"]
    timeout_minutes: 5
    on_error: "warn"
```

---

### 7.2 Workflow: Quick Fix

**Archivo:** `.claude/skills/workflows/quick-fix.yaml`

```yaml
name: "quick-fix"
version: "1.0"
description: "Bugfix rápido sin BDD ni plan formal"

config:
  tracking_enabled: true
  auto_track: true
  stop_on_error: false
  allow_skip: true

steps:
  - id: "validate"
    skill: "validate-context"
    phase: 0
    required: true
    auto_approve: true

  - id: "implement"
    skill: "implement-components"
    phase: 3
    required: true
    auto_approve: false
    depends_on: ["validate"]
    params:
      mode: "auto"

  - id: "test"
    skill: "test-unit"
    phase: 4
    required: true
    auto_approve: true
    depends_on: ["implement"]
    params:
      target_coverage: 85

  - id: "quality"
    skill: "validate-quality"
    phase: 7
    required: true
    auto_approve: true
    depends_on: ["test"]
    params:
      gates:
        - pylint
        - coverage
```

---

### 7.3 Workflow: Plan Only

**Archivo:** `.claude/skills/workflows/plan-only.yaml`

```yaml
name: "plan-only"
version: "1.0"
description: "Solo validación y planificación, sin implementación"

steps:
  - id: "validate"
    skill: "validate-context"
    phase: 0
    auto_approve: true

  - id: "bdd"
    skill: "generate-bdd"
    phase: 1
    auto_approve: false
    depends_on: ["validate"]

  - id: "plan"
    skill: "generate-plan"
    phase: 2
    auto_approve: false
    depends_on: ["validate", "bdd"]
```

---

## 8. Invocación

### 8.1 Ejecutar Workflow Completo

```bash
# Reemplaza el actual /implement-us
/workflow full-feature US-001

# Equivalente a ejecutar:
# /validate-context US-001
# /generate-bdd US-001
# /generate-plan US-001
# /implement-components US-001
# /test-unit US-001
# /test-integration US-001
# /validate-bdd US-001
# /validate-quality US-001
# /update-docs US-001
# /generate-report US-001
```

### 8.2 Ejecutar Workflow Rápido

```bash
/workflow quick-fix US-008
```

### 8.3 Ejecutar Skills Individuales (Manual)

```bash
# Validar contexto
/validate-context US-001

# Generar plan (auto-ejecuta validate-context si falta)
/generate-plan US-001

# Implementar componentes (auto-ejecuta prerequisitos)
/implement-components US-001

# Validar calidad
/validate-quality US-001
```

### 8.4 Comandos de Tracking (mantienen compatibilidad)

```bash
/track-pause Reunión de equipo
/track-resume
/track-status
/track-report US-001
/track-history --last 5
```

---

## 9. Resolución Automática de Dependencias

Cuando se ejecuta un skill, el sistema:

1. **Lee el estado compartido** (`.claude/state/US-XXX-context.json`)
2. **Verifica dependencias** según el grafo:
   ```
   validate_context
        ↓
   generate_bdd
        ↓
   generate_plan
        ↓
   implement_components
        ↓
   test_unit
        ↓
   test_integration
        ↓
   validate_bdd
        ↓
   validate_quality
        ↓
   update_docs
        ↓
   generate_report
   ```
3. **Ejecuta prerequisitos faltantes** automáticamente
4. **Muestra al usuario** qué se está ejecutando:
   ```
   /implement-components US-001

   ℹ️  Ejecutando prerequisitos faltantes:
      1. /validate-context US-001 ✓
      2. /generate-bdd US-001 (esperando aprobación...)
      3. /generate-plan US-001 (esperando aprobación...)

   ✓ Prerequisitos completos. Iniciando implementación...
   ```

---

## 10. Ventajas del Diseño

### 10.1 Flexibilidad
- Ejecutar solo las fases necesarias (ej: solo testing)
- Crear workflows custom por tipo de proyecto
- Iterar en pasos individuales

### 10.2 Reusabilidad
- Skills atómicos reutilizables en diferentes contextos
- Workflows compartibles entre proyectos
- Estado persistente permite pausar/reanudar

### 10.3 Transparencia
- Estado siempre visible en JSON
- Tracking automático por fase
- Trazabilidad completa del proceso

### 10.4 Mantenibilidad
- Cada skill es independiente
- Fácil agregar/modificar fases
- Testing individual de skills

### 10.5 Compatibilidad
- `/workflow full-feature` replica `/implement-us`
- Comandos de tracking sin cambios
- Migración suave desde versión actual

---

## 11. Próximos Pasos

### 11.1 Fase de Implementación

1. **Motor de Workflows** (Priority: High)
   - Engine que lee YAML y ejecuta skills
   - Resolución de dependencias
   - Manejo de errores y rollback

2. **Sistema de Estado** (Priority: High)
   - Lectura/escritura de `.claude/state/`
   - Validación de schemas JSON
   - Sincronización con tracking

3. **Skills Atómicos** (Priority: Medium)
   - Documentar los 9 skills en detalle
   - Crear templates por skill
   - Implementar lógica core de cada skill

4. **Tracking Integration** (Priority: Medium)
   - Integrar TimeTracker con estado compartido
   - Auto-inicio/fin de tracking por skill
   - Reportes multi-skill

5. **Testing** (Priority: Low)
   - Unit tests del workflow engine
   - Tests de resolución de dependencias
   - Tests de estado compartido

### 11.2 Documentación

1. Actualizar CLAUDE.md con nueva arquitectura
2. Crear guía de migración desde `/implement-us`
3. Documentar cada skill atómico en detalle
4. Crear ejemplos de workflows custom

### 11.3 Validación

1. Implementar US-008 usando el nuevo sistema
2. Comparar tiempo vs `/implement-us` actual
3. Recolectar feedback de usabilidad
4. Iterar sobre el diseño

---

## 12. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Complejidad aumenta | Alto | Mantener workflows simples por default |
| Estado compartido se corrompe | Alto | Validación estricta de schemas JSON |
| Dependencias circulares | Medio | Grafo acíclico estricto |
| Performance (muchos I/O) | Bajo | Caché en memoria del estado |
| Curva de aprendizaje | Medio | Workflows predefinidos + docs claras |

---

## 13. Métricas de Éxito

- **Reducción de tiempo**: Quick-fix 50% más rápido que full-feature
- **Flexibilidad**: 3+ workflows custom creados por usuarios
- **Adopción**: 100% de nuevas USs usan el nuevo sistema
- **Calidad**: Mantener coverage ≥95%, Pylint ≥8.0
- **Tracking**: Datos de tiempo 100% precisos y automáticos

---

## Apéndices

### A. Comparación con Versión Actual

| Aspecto | `/implement-us` (actual) | Suite de Skills (propuesto) |
|---------|-------------------------|------------------------------|
| Comandos | 1 monolítico | 9 atómicos + workflows |
| Flexibilidad | Baja | Alta |
| Reusabilidad | Baja | Alta |
| Estado | Implícito | Explícito (JSON) |
| Tracking | Integrado | Integrado + granular |
| Workflows | Fijo | Configurables (YAML) |
| Dependencias | Secuencial fijo | Auto-resolución |

### B. Ejemplo de Estado Completo

Ver sección 4.1 para el ejemplo completo de `.claude/state/US-XXX-context.json`

### C. Referencias

- Documento de trabajo: `docs/trabajo efimero/registro-de-trabajo.md`
- Skill actual: `.claude/skills/implement-us.md`
- Config actual: `.claude/skills/implement-us-config.json`
- Tracking actual: `.claude/tracking/time_tracker.py`
