# Propuesta de Diseño: Sistema de Tracking de Tiempo para Historias de Usuario

**Proyecto:** ISSE_Simuladores
**Fecha:** 2026-01-18
**Autor:** Victor Valotto
**Versión:** 1.0

---

## Tabla de Contenidos

1. [Arquitectura General](#1-arquitectura-general)
2. [Estructura de Datos (JSON)](#2-estructura-de-datos-json)
3. [Comandos Slash](#3-comandos-slash)
4. [Integración con el Skill implement-us](#4-integración-con-el-skill-implement-us)
5. [Reportes Generados](#5-reportes-generados)
6. [Módulo Python: TimeTracker](#6-módulo-python-timetracker)
7. [Plan de Implementación del Sistema](#7-plan-de-implementación-del-sistema)
8. [Ejemplo de Flujo Completo](#8-ejemplo-de-flujo-completo)
9. [Ventajas del Diseño Propuesto](#9-ventajas-del-diseño-propuesto)

---

## Contexto

Este documento describe el diseño de un sistema de tracking de tiempo para medir la duración real de implementación de Historias de Usuario usando el skill `/implement-us`.

### Objetivos

- **Tracking automático** de eventos por tarea individual
- **Métricas completas**: tiempo total, efectivo vs pausado, varianzas
- **Sin interacción** salvo pausas manuales
- **Almacenamiento JSON** local
- **Reportes** markdown detallados y dashboard JSON para análisis

---

## 1. Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│  /implement-us US-XXX                                   │
│  ↓                                                       │
│  ┌─────────────────────────────────────────┐            │
│  │ TimeTracker (módulo central)            │            │
│  │  - Registra eventos automáticamente     │            │
│  │  - Calcula métricas                     │            │
│  │  - Genera reportes                      │            │
│  └─────────────────────────────────────────┘            │
│           ↓                                              │
│  .claude/tracking/US-XXX-tracking.json   (datos raw)    │
│  docs/reports/US-XXX-tracking-report.md  (reporte)      │
│  .claude/metrics/summary.json            (agregado)     │
└─────────────────────────────────────────────────────────┘
```

### Componentes

1. **TimeTracker** - Módulo Python central que gestiona el tracking
2. **Comandos slash** - Interfaz para pausas y consultas manuales
3. **Generadores de reportes** - Markdown detallado y JSON agregado
4. **Integración con skill** - Hooks automáticos en cada fase/tarea

---

## 2. Estructura de Datos (JSON)

**Archivo: `.claude/tracking/US-XXX-tracking.json`**

```json
{
  "metadata": {
    "us_id": "US-001",
    "us_title": "Ver temperatura ambiente",
    "us_points": 3,
    "producto": "ux_termostato",
    "tracking_version": "1.0"
  },

  "timeline": {
    "started_at": "2026-01-18T10:00:00.000Z",
    "completed_at": "2026-01-18T13:45:30.000Z",
    "total_elapsed_seconds": 13530,
    "effective_seconds": 12300,
    "paused_seconds": 1230
  },

  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Validación de Contexto",
      "started_at": "2026-01-18T10:00:00.000Z",
      "completed_at": "2026-01-18T10:02:15.000Z",
      "elapsed_seconds": 135,
      "status": "completed",
      "auto_approved": true
    },
    {
      "phase_number": 1,
      "phase_name": "Generación de Escenarios BDD",
      "started_at": "2026-01-18T10:02:15.000Z",
      "completed_at": "2026-01-18T10:15:00.000Z",
      "elapsed_seconds": 765,
      "status": "completed",
      "auto_approved": false,
      "user_approval_time_seconds": 120
    },
    {
      "phase_number": 3,
      "phase_name": "Implementación Guiada por Tareas",
      "started_at": "2026-01-18T10:20:00.000Z",
      "completed_at": "2026-01-18T12:30:00.000Z",
      "elapsed_seconds": 7800,
      "status": "completed",
      "tasks": [
        {
          "task_id": "task_001",
          "task_name": "Implementar DisplayModelo",
          "task_type": "modelo",
          "estimated_minutes": 10,
          "started_at": "2026-01-18T10:20:00.000Z",
          "completed_at": "2026-01-18T10:28:30.000Z",
          "elapsed_seconds": 510,
          "actual_minutes": 8.5,
          "variance_minutes": -1.5,
          "file_created": "app/presentacion/paneles/display/modelo.py",
          "status": "completed"
        },
        {
          "task_id": "task_002",
          "task_name": "Implementar DisplayVista",
          "task_type": "vista",
          "estimated_minutes": 20,
          "started_at": "2026-01-18T10:28:30.000Z",
          "completed_at": "2026-01-18T10:50:00.000Z",
          "elapsed_seconds": 1290,
          "actual_minutes": 21.5,
          "variance_minutes": 1.5,
          "file_created": "app/presentacion/paneles/display/vista.py",
          "status": "completed"
        }
      ]
    }
  ],

  "pauses": [
    {
      "pause_id": "pause_001",
      "started_at": "2026-01-18T11:00:00.000Z",
      "resumed_at": "2026-01-18T11:15:00.000Z",
      "duration_seconds": 900,
      "reason": "Reunión de equipo"
    },
    {
      "pause_id": "pause_002",
      "started_at": "2026-01-18T12:00:00.000Z",
      "resumed_at": "2026-01-18T12:05:30.000Z",
      "duration_seconds": 330,
      "reason": "Pausa café"
    }
  ],

  "quality_metrics": {
    "pylint_score": 9.2,
    "cc_average": 2.1,
    "mi_average": 78.5,
    "coverage_percent": 97.3,
    "total_tests": 15,
    "tests_passed": 15,
    "tests_failed": 0
  },

  "summary": {
    "total_tasks": 12,
    "total_phases": 9,
    "estimated_total_minutes": 135,
    "actual_total_minutes": 205,
    "variance_minutes": 70,
    "variance_percent": 51.8,
    "files_created": 10,
    "lines_of_code": 487,
    "test_lines_of_code": 1823,
    "test_to_code_ratio": 3.74
  }
}
```

### Campos Clave

- **timeline**: Timestamps absolutos de inicio/fin y totales
- **phases**: Array de las 9 fases del skill con sus tasks anidadas
- **pauses**: Pausas manuales con razón y duración
- **quality_metrics**: Métricas de calidad del código (Fase 7)
- **summary**: Agregaciones y cálculos finales

---

## 3. Comandos Slash

### 3.1. Comandos Automáticos (integrados en el skill)

El skill `implement-us` invocará automáticamente:

- `TimeTracker.start_tracking(us_id)` - Al inicio de Fase 0
- `TimeTracker.start_phase(phase_num)` - Al inicio de cada fase
- `TimeTracker.end_phase(phase_num)` - Al finalizar cada fase
- `TimeTracker.start_task(task_id, task_name)` - Al inicio de cada tarea
- `TimeTracker.end_task(task_id)` - Al finalizar cada tarea
- `TimeTracker.end_tracking()` - Al completar Fase 9

### 3.2. Comandos Manuales (usuario invoca)

#### `/track-pause [razón]`

Pausa el tracking actual. Registra timestamp y razón opcional.

**Uso:**
```bash
/track-pause Reunión de equipo
/track-pause Pausa café
```

**Comportamiento:**
- Detiene el reloj efectivo
- Crea entrada en array `pauses`
- Respuesta: "⏸️  Tracking pausado. Duración actual: Xh Ymin"

---

#### `/track-resume`

Reanuda el tracking. Calcula duración de la pausa.

**Uso:**
```bash
/track-resume
```

**Comportamiento:**
- Reanuda el reloj efectivo
- Cierra la pausa actual con `resumed_at` y `duration_seconds`
- Respuesta: "▶️  Tracking reanudado. Pausa: Xmin"

---

#### `/track-status`

Muestra estado actual del tracking.

**Uso:**
```bash
/track-status
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  TRACKING STATUS - US-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Progreso: Fase 3/9 (Implementación)
📋 Tarea actual: DisplayControlador (tarea 3/12)

⏰ Tiempos:
   • Inicio:      10:00:00
   • Transcurrido: 2h 15min
   • Efectivo:    2h 00min
   • Pausado:     15min
   • Estado:      ⏸️  EN PAUSA (desde hace 5min)

📈 Estimado vs Real:
   • Plan:        2h 15min
   • Real:        2h 00min
   • Varianza:    -15min (-11%)

✅ Completadas: 2/12 tareas
```

---

#### `/track-report [us_id]`

Genera reporte inmediato (sin esperar a finalizar la US).

**Uso:**
```bash
/track-report US-001
```

**Comportamiento:**
- Lee `.claude/tracking/US-001-tracking.json`
- Genera reporte markdown en `docs/reports/US-001-tracking-report.md`
- Muestra resumen en terminal

---

#### `/track-history [filtros]`

Muestra historial de USs trackeadas con métricas agregadas.

**Uso:**
```bash
/track-history --last 5
/track-history --producto ux_termostato
/track-history --desde 2026-01-01
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 HISTORIAL DE TRACKING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

US-001 | Ver temperatura ambiente      | 3pts | 3h 25min | +52%  | 2026-01-18
US-002 | Ver estado climatizador       | 5pts | 5h 06min | +27%  | 2026-01-17
US-003 | Ver indicadores de alerta     | 2pts | 2h 41min | +19%  | 2026-01-16

📈 Promedios:
   • Tiempo por punto: 1h 08min
   • Varianza promedio: +32%
   • Velocity: 3.3 puntos/día
```

---

## 4. Integración con el Skill `implement-us`

### 4.1. Modificaciones al Skill

**Archivo: `.claude/skills/implement-us.md`**

Agregar al inicio del proceso:

```markdown
### Fase 0: Validación de Contexto

**ANTES DE INICIAR:**
1. Iniciar tracking automático:
   ```python
   tracker = TimeTracker(us_id, us_title, us_points, producto)
   tracker.start_tracking()
   tracker.start_phase(0, "Validación de Contexto")
   ```

2. Verificar que existe la historia de usuario...
   [... resto de la fase ...]

**AL FINALIZAR:**
```python
tracker.end_phase(0, auto_approved=True)
```
```

**Ejemplo Fase 3 (Implementación) - Tracking de tareas:**

```markdown
### Fase 3: Implementación Guiada por Tareas

**AL INICIO:**
```python
tracker.start_phase(3, "Implementación Guiada por Tareas")
```

**POR CADA TAREA:**

1. **Iniciar tracking de tarea:**
   ```python
   tracker.start_task(
       task_id=f"task_{task_number:03d}",
       task_name="Implementar DisplayModelo",
       task_type="modelo",  # modelo, vista, controlador, test
       estimated_minutes=10
   )
   ```

2. **Mostrar contexto y código propuesto**
   [... proceso normal ...]

3. **Al completar la tarea:**
   ```python
   tracker.end_task(
       task_id=f"task_{task_number:03d}",
       file_created="app/presentacion/paneles/display/modelo.py"
   )
   ```

4. **Actualizar plan INMEDIATAMENTE**
   - Marcar checkbox de tarea completada
   - Actualizar contador de progreso

**AL FINALIZAR:**
```python
tracker.end_phase(3)
```
```

### 4.2. Configuración

**Archivo: `.claude/skills/implement-us-config.json`**

Agregar sección de tracking:

```json
{
  "tracking": {
    "enabled": true,
    "auto_start": true,
    "auto_pause_on_error": true,
    "track_user_approval_time": true,
    "storage_path": ".claude/tracking",
    "metrics_path": ".claude/metrics",
    "generate_reports": true,
    "report_formats": ["markdown", "json"]
  },

  "quality_gates": {
    "pylint_min": 8.0,
    "cc_max": 10,
    "mi_min": 20,
    "coverage_min": 95.0
  },

  "workflow": {
    "checkpoint_approval": true,
    "auto_run_tests": true,
    "generate_bdd": true,
    "generate_plan": true,
    "generate_report": true,
    "update_changelog": true
  }
}
```

---

## 5. Reportes Generados

### 5.1. Reporte Markdown Detallado

**Archivo: `docs/reports/US-XXX-tracking-report.md`**

```markdown
# Reporte de Tracking: US-001 - Ver temperatura ambiente

**Fecha:** 2026-01-18
**Producto:** ux_termostato
**Puntos:** 3
**Estado:** ✅ COMPLETADO

---

## 📊 Resumen Ejecutivo

| Métrica | Estimado | Real | Varianza |
|---------|----------|------|----------|
| **Tiempo total** | 2h 15min | 3h 25min | +1h 10min (+52%) |
| **Tiempo efectivo** | - | 3h 05min | - |
| **Pausas** | - | 20min | - |
| **Tareas** | 12 | 12 | 0 |
| **Archivos creados** | 10 | 10 | 0 |

---

## ⏱️ Timeline de Fases

```
Fase 0: Validación        ████░░░░░░  2min   [10:00 - 10:02]
Fase 1: BDD              ████████░░ 13min   [10:02 - 10:15]
Fase 2: Plan             ██████░░░░  5min   [10:15 - 10:20]
Fase 3: Implementación   ████████████ 2h 10min [10:20 - 12:30]
Fase 4: Tests Unitarios  ██████████░ 25min  [12:30 - 12:55]
Fase 5: Tests Integración ████████░░ 15min  [12:55 - 13:10]
Fase 6: BDD Validación   ██████░░░░  8min   [13:10 - 13:18]
Fase 7: Quality Gates    ████████░░ 12min   [13:18 - 13:30]
Fase 8: Documentación    ██████░░░░  7min   [13:30 - 13:37]
Fase 9: Reporte Final    ████░░░░░░  3min   [13:37 - 13:40]
```

**Tiempo efectivo total:** 3h 05min
**Pausas:** 20min (2 pausas)

---

## 📋 Breakdown por Tarea (Fase 3)

| # | Tarea | Tipo | Estimado | Real | Varianza |
|---|-------|------|----------|------|----------|
| 1 | DisplayModelo | modelo | 10min | 8.5min | -1.5min (-15%) |
| 2 | DisplayVista | vista | 20min | 21.5min | +1.5min (+7.5%) |
| 3 | DisplayControlador | controlador | 15min | 18min | +3min (+20%) |
| 4 | tests/test_display_modelo.py | test | 15min | 22min | +7min (+47%) |
| 5 | tests/test_display_vista.py | test | 20min | 28min | +8min (+40%) |
| ... | ... | ... | ... | ... | ... |

**Total Fase 3:** 1h 55min estimado → 2h 10min real (+15min, +13%)

---

## ⏸️ Pausas Registradas

| # | Inicio | Fin | Duración | Razón |
|---|--------|-----|----------|-------|
| 1 | 11:00 | 11:15 | 15min | Reunión de equipo |
| 2 | 12:00 | 12:05 | 5min | Pausa café |

**Total pausado:** 20min

---

## 📈 Análisis de Varianza

### Tareas con mayor desviación:

1. **tests/test_display_vista.py** (+8min, +40%)
   - Estimado: 20min
   - Real: 28min
   - Posible causa: Mayor cobertura de edge cases

2. **tests/test_display_modelo.py** (+7min, +47%)
   - Estimado: 15min
   - Real: 22min
   - Posible causa: Tests de inmutabilidad más complejos

### Fases con mayor desviación:

1. **Fase 3: Implementación** (+15min, +13%)
2. **Fase 4: Tests Unitarios** (+5min, +20%)

---

## 💡 Insights y Recomendaciones

1. **Tests requieren ~40% más tiempo del estimado**
   - Ajustar estimaciones futuras para tasks de testing
   - Ratio actual: 1.4x lo estimado

2. **Implementación MVC fue eficiente**
   - Modelo, Vista, Controlador muy cerca de lo estimado
   - Patrón bien establecido

3. **Ratio test/código: 3.74:1**
   - 1823 líneas de tests vs 487 de código
   - Excelente cobertura

---
**Generado automáticamente por TimeTracker v1.0**
**Fecha:** 2026-01-18 13:40:00
```

### 5.2. Dashboard JSON Agregado

**Archivo: `.claude/metrics/summary.json`**

```json
{
  "project": "ISSE_Simuladores",
  "producto": "ux_termostato",
  "generated_at": "2026-01-18T13:40:00.000Z",

  "sprint_summary": {
    "sprint_name": "Sprint 1 - MVP Básico",
    "total_us": 3,
    "completed_us": 3,
    "total_points": 10,
    "total_estimated_hours": 8.5,
    "total_actual_hours": 11.2,
    "variance_percent": 31.8
  },

  "user_stories": [
    {
      "us_id": "US-001",
      "title": "Ver temperatura ambiente",
      "points": 3,
      "estimated_hours": 2.25,
      "actual_hours": 3.42,
      "variance_percent": 52.0,
      "completed_at": "2026-01-18T13:40:00.000Z"
    },
    {
      "us_id": "US-002",
      "title": "Ver estado climatizador",
      "points": 5,
      "estimated_hours": 4.0,
      "actual_hours": 5.1,
      "variance_percent": 27.5,
      "completed_at": "2026-01-17T16:30:00.000Z"
    },
    {
      "us_id": "US-003",
      "title": "Ver indicadores de alerta",
      "points": 2,
      "estimated_hours": 2.25,
      "actual_hours": 2.68,
      "variance_percent": 19.1,
      "completed_at": "2026-01-16T14:20:00.000Z"
    }
  ],

  "metrics_by_phase": {
    "phase_0": { "avg_minutes": 2.3, "std_dev": 0.5 },
    "phase_1": { "avg_minutes": 11.7, "std_dev": 2.1 },
    "phase_2": { "avg_minutes": 5.0, "std_dev": 0.8 },
    "phase_3": { "avg_minutes": 126.3, "std_dev": 15.2 },
    "phase_4": { "avg_minutes": 23.7, "std_dev": 3.1 },
    "phase_5": { "avg_minutes": 14.3, "std_dev": 1.8 },
    "phase_6": { "avg_minutes": 7.7, "std_dev": 1.2 },
    "phase_7": { "avg_minutes": 11.0, "std_dev": 1.5 },
    "phase_8": { "avg_minutes": 6.3, "std_dev": 1.0 },
    "phase_9": { "avg_minutes": 3.0, "std_dev": 0.5 }
  },

  "metrics_by_task_type": {
    "modelo": { "avg_minutes": 9.2, "count": 3 },
    "vista": { "avg_minutes": 21.8, "count": 3 },
    "controlador": { "avg_minutes": 17.3, "count": 3 },
    "test_unitario": { "avg_minutes": 24.5, "count": 9 },
    "test_integracion": { "avg_minutes": 14.3, "count": 3 }
  },

  "quality_trends": {
    "pylint_avg": 9.53,
    "cc_avg": 1.87,
    "mi_avg": 81.2,
    "coverage_avg": 98.7,
    "test_to_code_ratio_avg": 3.92
  },

  "velocity": {
    "points_per_day": 5.0,
    "hours_per_point": 1.12,
    "tasks_per_day": 6.0
  }
}
```

---

## 6. Módulo Python: TimeTracker

**Ubicación: `.claude/tracking/time_tracker.py`**

### 6.1. Clases de Datos

```python
"""
TimeTracker - Sistema de tracking de tiempo para implementación de USs.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict
import json


@dataclass
class Task:
    """Representa una tarea individual."""
    task_id: str
    task_name: str
    task_type: str  # modelo, vista, controlador, test
    estimated_minutes: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    elapsed_seconds: int = 0
    file_created: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed


@dataclass
class Phase:
    """Representa una fase del skill."""
    phase_number: int
    phase_name: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    elapsed_seconds: int = 0
    status: str = "pending"
    tasks: List[Task] = field(default_factory=list)
    auto_approved: bool = True
    user_approval_time_seconds: int = 0


@dataclass
class Pause:
    """Representa una pausa manual."""
    pause_id: str
    started_at: datetime
    resumed_at: Optional[datetime] = None
    duration_seconds: int = 0
    reason: str = ""
```

### 6.2. Clase Principal

```python
class TimeTracker:
    """Gestor central de tracking de tiempo."""

    def __init__(self, us_id: str, us_title: str, us_points: int, producto: str):
        self.us_id = us_id
        self.us_title = us_title
        self.us_points = us_points
        self.producto = producto

        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        self.phases: List[Phase] = []
        self.pauses: List[Pause] = []

        self.current_phase: Optional[Phase] = None
        self.current_task: Optional[Task] = None
        self.current_pause: Optional[Pause] = None

        self.storage_path = Path(f".claude/tracking/{us_id}-tracking.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def start_tracking(self):
        """Inicia el tracking (al invocar /implement-us)."""
        self.started_at = datetime.now(timezone.utc)
        self._save()

    def start_phase(self, phase_number: int, phase_name: str):
        """Inicia una fase."""
        phase = Phase(
            phase_number=phase_number,
            phase_name=phase_name,
            started_at=datetime.now(timezone.utc),
            status="in_progress"
        )
        self.phases.append(phase)
        self.current_phase = phase
        self._save()

    def end_phase(self, phase_number: int, auto_approved: bool = True):
        """Finaliza una fase."""
        phase = self._get_phase(phase_number)
        if phase:
            phase.completed_at = datetime.now(timezone.utc)
            phase.elapsed_seconds = (
                phase.completed_at - phase.started_at
            ).total_seconds()
            phase.status = "completed"
            phase.auto_approved = auto_approved
            self.current_phase = None
            self._save()

    def start_task(
        self,
        task_id: str,
        task_name: str,
        task_type: str,
        estimated_minutes: float
    ):
        """Inicia una tarea dentro de la fase actual."""
        if not self.current_phase:
            raise ValueError("No hay fase activa")

        task = Task(
            task_id=task_id,
            task_name=task_name,
            task_type=task_type,
            estimated_minutes=estimated_minutes,
            started_at=datetime.now(timezone.utc),
            status="in_progress"
        )
        self.current_phase.tasks.append(task)
        self.current_task = task
        self._save()

    def end_task(self, task_id: str, file_created: Optional[str] = None):
        """Finaliza una tarea."""
        if not self.current_phase:
            raise ValueError("No hay fase activa")

        task = self._get_task(task_id)
        if task:
            task.completed_at = datetime.now(timezone.utc)
            task.elapsed_seconds = (
                task.completed_at - task.started_at
            ).total_seconds()
            task.status = "completed"
            task.file_created = file_created
            self.current_task = None
            self._save()

    def pause(self, reason: str = ""):
        """Pausa el tracking (invocado por /track-pause)."""
        if self.current_pause:
            raise ValueError("Ya hay una pausa activa")

        pause = Pause(
            pause_id=f"pause_{len(self.pauses) + 1:03d}",
            started_at=datetime.now(timezone.utc),
            reason=reason
        )
        self.pauses.append(pause)
        self.current_pause = pause
        self._save()

    def resume(self):
        """Reanuda el tracking (invocado por /track-resume)."""
        if not self.current_pause:
            raise ValueError("No hay pausa activa")

        self.current_pause.resumed_at = datetime.now(timezone.utc)
        self.current_pause.duration_seconds = (
            self.current_pause.resumed_at - self.current_pause.started_at
        ).total_seconds()
        self.current_pause = None
        self._save()

    def end_tracking(self):
        """Finaliza el tracking (al completar Fase 9)."""
        self.completed_at = datetime.now(timezone.utc)
        self._save()
        self.generate_reports()

    def get_status(self) -> Dict:
        """Retorna estado actual para /track-status."""
        if not self.started_at:
            return {"status": "not_started"}

        now = datetime.now(timezone.utc)
        elapsed = (now - self.started_at).total_seconds()
        paused = sum(p.duration_seconds for p in self.pauses if p.resumed_at)

        if self.current_pause:
            paused += (now - self.current_pause.started_at).total_seconds()

        effective = elapsed - paused

        return {
            "status": "paused" if self.current_pause else "running",
            "started_at": self.started_at.isoformat(),
            "elapsed_seconds": int(elapsed),
            "effective_seconds": int(effective),
            "paused_seconds": int(paused),
            "current_phase": self.current_phase.phase_name if self.current_phase else None,
            "current_task": self.current_task.task_name if self.current_task else None,
            "completed_tasks": sum(
                len([t for t in p.tasks if t.status == "completed"])
                for p in self.phases
            ),
            "total_tasks": sum(len(p.tasks) for p in self.phases)
        }

    def generate_reports(self):
        """Genera reportes markdown y JSON."""
        from .report_generator import generate_markdown_report, update_metrics_dashboard

        # Reporte markdown detallado
        report_path = Path(f"docs/reports/{self.us_id}-tracking-report.md")
        generate_markdown_report(self, report_path)

        # Dashboard JSON agregado
        metrics_path = Path(".claude/metrics/summary.json")
        update_metrics_dashboard(self, metrics_path)

    def _save(self):
        """Guarda estado actual a JSON."""
        data = self._to_dict()
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _to_dict(self) -> Dict:
        """Convierte el tracker a diccionario JSON-serializable."""
        # Implementar serialización completa
        pass

    def _get_phase(self, phase_number: int) -> Optional[Phase]:
        """Obtiene una fase por número."""
        return next((p for p in self.phases if p.phase_number == phase_number), None)

    def _get_task(self, task_id: str) -> Optional[Task]:
        """Obtiene una tarea por ID."""
        if not self.current_phase:
            return None
        return next((t for t in self.current_phase.tasks if t.task_id == task_id), None)
```

### 6.3. Módulo de Generación de Reportes

**Ubicación: `.claude/tracking/report_generator.py`**

```python
"""
Generadores de reportes para TimeTracker.
"""
from pathlib import Path
from typing import Dict
import json


def generate_markdown_report(tracker, output_path: Path):
    """Genera reporte markdown detallado."""
    # Implementar generación de markdown
    # - Tabla resumen ejecutivo
    # - Timeline ASCII de fases
    # - Breakdown por tarea
    # - Pausas
    # - Quality metrics
    # - Análisis de varianzas
    # - Insights
    pass


def update_metrics_dashboard(tracker, metrics_path: Path):
    """Actualiza dashboard JSON agregado."""
    # Cargar summary.json existente (o crear nuevo)
    # Agregar nueva US al array
    # Recalcular agregaciones (promedios, totales)
    # Actualizar velocity
    # Guardar
    pass


def format_duration(seconds: int) -> str:
    """Formatea segundos a 'Xh Ymin'."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes}min"


def calculate_variance_percent(estimated: float, actual: float) -> float:
    """Calcula varianza porcentual."""
    if estimated == 0:
        return 0.0
    return ((actual - estimated) / estimated) * 100
```

---

## 7. Plan de Implementación del Sistema

### Fase 1: Core TimeTracker (4-6 horas)

- [ ] Crear estructura de directorios `.claude/tracking/`
- [ ] Implementar dataclasses (Task, Phase, Pause)
- [ ] Implementar clase TimeTracker con métodos básicos
- [ ] Implementar persistencia JSON (_save, _to_dict)
- [ ] Implementar métodos de consulta (_get_phase, _get_task)
- [ ] Tests unitarios del tracker (pytest)

**Archivos:**
- `.claude/tracking/__init__.py`
- `.claude/tracking/time_tracker.py`
- `tests/test_time_tracker.py`

---

### Fase 2: Integración con Skill (3-4 horas)

- [ ] Modificar `.claude/skills/implement-us.md` con hooks de tracking
- [ ] Agregar tracking en Fase 0-9 (start_phase, end_phase)
- [ ] Agregar tracking de tareas en Fase 3
- [ ] Actualizar `.claude/skills/implement-us-config.json`
- [ ] Tests de integración skill + tracker

**Archivos modificados:**
- `.claude/skills/implement-us.md`
- `.claude/skills/implement-us-config.json`

---

### Fase 3: Comandos Manuales (2-3 horas)

- [ ] Implementar comando `/track-pause`
- [ ] Implementar comando `/track-resume`
- [ ] Implementar comando `/track-status` con formato
- [ ] Implementar comando `/track-report`
- [ ] Implementar comando `/track-history`
- [ ] Documentar comandos en CLAUDE.md

**Archivos:**
- `.claude/commands/track.py` (o integrar en skill)
- Actualizar `CLAUDE.md`

---

### Fase 4: Generadores de Reportes (4-5 horas)

- [ ] Implementar `generate_markdown_report()`
  - [ ] Tabla resumen ejecutivo
  - [ ] Timeline ASCII de fases
  - [ ] Breakdown por tarea
  - [ ] Sección de pausas
  - [ ] Quality metrics
  - [ ] Análisis de varianzas
  - [ ] Insights automatizados
- [ ] Implementar `update_metrics_dashboard()`
  - [ ] Agregar nueva US
  - [ ] Calcular promedios por fase
  - [ ] Calcular promedios por tipo de tarea
  - [ ] Actualizar velocity
- [ ] Funciones auxiliares de formato

**Archivos:**
- `.claude/tracking/report_generator.py`
- `tests/test_report_generator.py`

---

### Fase 5: Testing y Documentación (2-3 horas)

- [ ] Tests end-to-end de flujo completo
- [ ] Tests de comandos slash
- [ ] Tests de generación de reportes
- [ ] Documentar en README.md cómo usar tracking
- [ ] Actualizar CLAUDE.md con sección de tracking
- [ ] Ejemplos de uso en docs/

**Archivos:**
- `tests/test_tracking_integration.py`
- Actualizar `README.md`
- Actualizar `CLAUDE.md`
- `docs/ejemplos-tracking.md`

---

**Total estimado: 15-21 horas**

---

## 8. Ejemplo de Flujo Completo

### Sesión típica de implementación

```bash
# ═══════════════════════════════════════════════════════════
# Usuario inicia implementación
# ═══════════════════════════════════════════════════════════

$ /implement-us US-004

Claude:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Implementador de Historia de Usuario
⏱️  Tracking iniciado automáticamente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Historia: US-004 - Aumentar temperatura
📦 Producto: ux_termostato
⭐ Prioridad: Alta
🎯 Puntos: 3

━━━ Fase 0: Validación de Contexto ━━━

✅ Historia encontrada en docs/HISTORIAS-USUARIO-UX-TERMOSTATO.md
✅ Arquitectura de referencia: ADR-003
✅ Estándares: CLAUDE.md
✅ Tests configurados: conftest.py

━━━ Fase 1: Generación de Escenarios BDD ━━━

Generando escenarios basados en criterios de aceptación...

[Muestra escenarios generados]

¿Aprobar escenarios BDD? (yes/no/edit)

# ═══════════════════════════════════════════════════════════
# Usuario aprueba y continúa trabajando
# ═══════════════════════════════════════════════════════════

User: yes

Claude:
✅ Escenarios guardados en tests/features/US-004-aumentar-temperatura.feature

━━━ Fase 2: Plan de Implementación ━━━

[Muestra plan detallado con estimaciones]

¿Aprobar plan? (yes/no/edit)

User: yes

━━━ Fase 3: Implementación Tarea 1/12 ━━━

📋 Implementar ControlTempModelo

[Muestra código propuesto]

¿Implementar? (yes/no/edit)

User: yes

✅ Archivo creado: app/presentacion/paneles/control_temp/modelo.py
⏭️  Siguiente tarea: Implementar ControlTempVista...

# ═══════════════════════════════════════════════════════════
# Usuario tiene una reunión (PAUSA MANUAL)
# ═══════════════════════════════════════════════════════════

$ /track-pause Reunión de equipo

Claude:
⏸️  Tracking pausado
   Duración actual: 1h 25min (efectivo: 1h 20min)

# ═══════════════════════════════════════════════════════════
# Usuario regresa 20 minutos después
# ═══════════════════════════════════════════════════════════

$ /track-resume

Claude:
▶️  Tracking reanudado
   Pausa registrada: 20min (Reunión de equipo)
   Continuando con tarea 4/12: Implementar ControlTempControlador

# ═══════════════════════════════════════════════════════════
# Usuario quiere ver el progreso
# ═══════════════════════════════════════════════════════════

$ /track-status

Claude:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  TRACKING STATUS - US-004
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Progreso: Fase 4/9 (Tests Unitarios)
📋 Tarea actual: test_control_temp_vista.py (tarea 8/12)

⏰ Tiempos:
   • Inicio:       14:00:00
   • Transcurrido: 2h 35min
   • Efectivo:     2h 15min
   • Pausado:      20min
   • Estado:       ▶️  EN CURSO

📈 Estimado vs Real:
   • Plan:        3h 00min
   • Proyección:  3h 30min (+30min, +17%)

✅ Completadas: 7/12 tareas

# ═══════════════════════════════════════════════════════════
# Continúa el proceso hasta finalizar Fase 9
# ═══════════════════════════════════════════════════════════

[... implementación continúa ...]

Claude:
━━━ Fase 9: Reporte Final ━━━

✅ US-004 completada exitosamente

📊 Reportes generados:
   • docs/reports/US-004-tracking-report.md
   • .claude/metrics/summary.json actualizado

🎯 Resumen Final:
   • Estimado:    3h 00min
   • Real:        3h 42min
   • Varianza:    +42min (+23%)
   • Tareas:      12/12 ✅
   • Quality:     APROBADO ✅
   • Coverage:    98.2%
   • Pylint:      9.5/10

💡 Insight: Los tests tomaron 35% más tiempo del estimado.
   Considerar ajustar estimaciones para próximas USs.

¿Deseas revisar el reporte completo? (/track-report US-004)
```

---

## 9. Ventajas del Diseño Propuesto

### ✅ Automatización

- **Sin interacción constante**: El tracking ocurre transparentemente
- **Solo pausas manuales**: El usuario controla interrupciones explícitamente
- **Integración nativa**: Hooks directos en el skill, no requiere invocación manual

### ✅ Granularidad

- **Por tarea individual**: Máximo nivel de detalle
- **12+ tareas por US**: Permite identificar cuellos de botella específicos
- **Timestamps precisos**: Inicio/fin de cada task, no aproximaciones

### ✅ Métricas Completas

- **Tiempo total**: Inicio a commit (incluye pausas)
- **Tiempo efectivo**: Excluye pausas, es el tiempo real de trabajo
- **Tiempo por fase**: Distribución de esfuerzo en las 9 fases
- **Varianzas**: Estimado vs real por tarea, fase y total

### ✅ Almacenamiento Simple

- **JSON puro**: Fácil de parsear, versionar, compartir
- **Portable**: Se puede copiar entre máquinas
- **Versionable**: Opcionalmente committear tracking/*.json a git
- **Queryable**: Con jq o scripts Python

### ✅ Reportes Ricos

- **Markdown legible**: Para humanos, con tablas y gráficos ASCII
- **JSON estructurado**: Para análisis programático
- **Dashboard agregado**: Métricas históricas de todas las USs
- **Insights automatizados**: Detección de patrones y recomendaciones

### ✅ No Invasivo

- **Sin cambios estructurales**: Solo agrega hooks, no modifica arquitectura
- **Opt-in vía config**: Se puede deshabilitar fácilmente
- **Sin dependencias extra**: Solo stdlib de Python
- **Compatible**: Funciona con el flujo actual del skill

### ✅ Extensible

- **Nuevas métricas**: Fácil agregar campos a JSON
- **Nuevos reportes**: Nuevos formatos sin cambiar tracker
- **Integraciones**: Hooks para Jira, Slack, webhooks
- **Análisis histórico**: Con summary.json se puede generar gráficos

### ✅ Análisis Histórico

- **Velocity**: Puntos por día, horas por punto
- **Tendencias**: Mejora en estimaciones con el tiempo
- **Benchmarks**: Comparar USs similares
- **Calibración**: Ajustar estimaciones futuras basado en histórico

---

## Próximos Pasos

1. **Revisar y aprobar** esta propuesta
2. **Priorizar fases** de implementación (¿todas o MVP primero?)
3. **Asignar tiempo** para desarrollo
4. **Definir criterios de éxito** para validar el sistema

**Pregunta:** ¿Querés implementar todo el sistema o empezar con un MVP (Fases 1-2)?

---

**Fin del documento**
