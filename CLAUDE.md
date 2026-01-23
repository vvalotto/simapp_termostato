# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema HIL (Hardware-in-the-Loop) con tres aplicaciones PyQt6 que simulan sensores y UI para testing del sistema ISSE_Termostato en Raspberry Pi.

```
Desktop (Mac/PC)                         Raspberry Pi
┌─────────────────────┐                  ┌─────────────────────┐
│ simulador_temperatura│──── :12000 ────►│                     │
│ simulador_bateria    │──── :11000 ────►│   ISSE_Termostato   │
│ ux_termostato        │◄─── :14001/02 ──│                     │
│                      │──── :13000/14000►│                     │
└─────────────────────┘                  └─────────────────────┘
```

## Commands

### Skills Personalizados

**`/implement-us US-XXX`** - Implementar Historia de Usuario
- Proceso completo en `.claude/skills/implement-us.md`
- Incluye: BDD → Plan → MVC → Tests → Quality → Docs
- Usar cuando el usuario solicite "implementa US-XXX"

```bash
# Setup
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configurar RASPBERRY_IP

# Ejecutar simuladores
python simulador_temperatura/run.py
python simulador_bateria/run.py
python ux_termostato/run.py

# Quality (ejecutar desde directorio del producto)
pylint app/                                              # Linting
python quality/scripts/calculate_metrics.py app          # Generar métricas CC/MI
python quality/scripts/validate_gates.py quality/reports/quality_*.json  # Validar umbrales
```

## Quality Gates

Cada producto debe cumplir:
- **Complejidad Ciclomática (CC)** promedio ≤ 10
- **Índice de Mantenibilidad (MI)** promedio > 20
- **Pylint Score** ≥ 8.0

Los scripts están en `compartido/quality/scripts/` y se copian a cada producto.

## Architecture

### Simuladores (temperatura y bateria) - MVC + Factory/Coordinator

Ambos simuladores usan arquitectura idéntica:

```
run.py                      # AplicacionSimulador (lifecycle)
app/
├── factory.py              # ComponenteFactory - crea todos los componentes
├── coordinator.py          # SimuladorCoordinator - conecta signals PyQt
├── configuracion/          # ConfigManager, ConfigSimulador*, constantes
├── dominio/                # Generador*, Estado* (lógica de negocio pura)
├── comunicacion/           # Cliente*, ServicioEnvio* (TCP via EphemeralSocketClient)
└── presentacion/
    ├── ui_compositor.py    # Composición del layout principal
    └── paneles/            # Cada panel tiene: modelo.py, vista.py, controlador.py
        ├── conexion/       # Config IP/puerto
        ├── control/        # Slider voltaje/temperatura
        ├── estado/         # Contadores envíos exitosos/fallidos
        └── grafico/        # (solo temperatura) Panel de gráfica pyqtgraph
```

**Diferencias clave entre simuladores:**
- `simulador_temperatura`: Tiene panel gráfico y modo automático (variación senoidal)
- `simulador_bateria`: Solo modo manual (slider), sin panel gráfico

**Flujo de signals PyQt:**
```
Generador ──valor_generado──► ServicioEnvio ──TCP──► RPi
    │                              │
    └──voltaje_cambiado────►  CtrlEstado ──actualiza──► Vista
                                   │
                                   └──registra_envio──► UI (contadores)
```

**Patrón Factory/Coordinator:**
- `factory.py` crea componentes independientes con configuración consistente
- `coordinator.py` conecta señales PyQt entre componentes, evitando dependencias circulares
- Permite lazy initialization del servicio de envío (se crea al conectar)

### ux_termostato - MVC + Factory/Coordinator

**Principio arquitectural:** UX Desktop es un **cliente sin estado** - no persiste configuración ni datos históricos.

Siguiendo la arquitectura de referencia de los simuladores:

```
run.py                      # AplicacionUX (lifecycle)
app/
├── factory.py              # ComponenteFactoryUX - crea todos los componentes
├── coordinator.py          # UXCoordinator - conecta signals PyQt
├── configuracion/          # ConfigManager, ConfigUX, constantes
├── dominio/                # EstadoTermostato, ComandoTermostato (lógica pura)
├── comunicacion/           # ServidorEstado, ClienteComandos (TCP bidireccional)
└── presentacion/
    ├── ui_principal.py     # Ventana principal (lifecycle, menú)
    ├── ui_compositor.py    # Composición del layout principal
    └── paneles/            # Cada panel tiene: modelo.py, vista.py, controlador.py
        ├── display/        # Display LCD temperatura
        ├── climatizador/   # Indicadores calor/reposo/frío
        ├── indicadores/    # LEDs alerta (sensor, batería)
        ├── power/          # Botón encender/apagar
        ├── control_temp/   # Botones subir/bajar temperatura
        ├── selector_vista/ # (pendiente) Toggle ambiente/deseada
        ├── conexion/       # (pendiente) Config IP/puerto
        └── estado_footer/  # (pendiente) Info estado/conexión
```

**Diferencia con simuladores:**
- **Comunicación bidireccional**: Recibe estado (puerto 14001) y envía comandos (14000)
- **Sin generador**: No simula datos, solo renderiza estado recibido del RPi
- **Sin persistencia**: Estado es efímero, pertenece al RPi

### compartido/

Código reutilizable entre productos:
- `networking/`:
  - `EphemeralSocketClient` - patrón "conectar→enviar→cerrar" para clientes
  - `BaseSocketClient` - cliente base con soporte async
  - `BaseSocketServer` - servidor TCP con threading
- `widgets/`:
  - `ConfigPanel` - panel de configuración IP/puerto con validación
  - `LedIndicator` - indicador LED (rojo/verde) para estados
  - `LogViewer` - visor de logs con colores
  - `StatusIndicator` - indicador de estado con texto
  - `ValidationFeedback` - feedback visual para validación
- `estilos/`:
  - `ThemeProvider` - tema oscuro consistente
  - `ThemeColors` - constantes de colores
- `quality/scripts/`:
  - `calculate_metrics.py` - calcula CC/MI con radon
  - `validate_gates.py` - valida métricas vs umbrales
  - `generate_report.py` - genera reportes de calidad

## Communication Protocol

| Puerto | Dirección | Formato | Uso |
|--------|-----------|---------|-----|
| 12000 | Desktop → RPi | `<float>\n` | Temperatura simulada (-40 a 85°C) |
| 11000 | Desktop → RPi | `<float>\n` | Voltaje batería (0.0-5.0V) |
| 13000 | Desktop → RPi | `aumentar\|disminuir` | Seteo temperatura |
| 14000 | Desktop → RPi | `ambiente\|deseada` | Selector display |
| 14001 | RPi → Desktop | `<etiqueta>: <valor>` | Visualizador temperatura |
| 14002 | RPi → Desktop | `<float>` | Visualizador batería |

**Patrón de conexión:** Efímero (connect → send → close por mensaje)

## Configuration

Dos niveles de configuración:

1. **config.json** (root): Valores por defecto, versionado en git
   - IP Raspberry (default: 127.0.0.1)
   - Puertos de comunicación
   - Parámetros de simulación (rangos, intervalos)

2. **.env** (root): Overrides locales, NO versionado
   - `RASPBERRY_IP` - IP del RPi real
   - `PUERTO_TEMPERATURA`, `PUERTO_BATERIA`, etc.
   - `DEBUG` - modo debug

Los simuladores leen config.json y sobrescriben con variables de .env si existen.

## Testing Patterns

Tests en `tests/` con pytest y pytest-qt:

**Estructura de fixtures** (`conftest.py`):
```python
# Nivel 1: QApplication (base)
@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])

# Nivel 2: Configuración
@pytest.fixture
def config():
    return ConfigSimuladorBateria(...)

# Nivel 3: Modelos
@pytest.fixture
def modelo(config):
    return PanelEstadoModelo(...)

# Nivel 4: Componentes completos
@pytest.fixture
def controlador(modelo, vista):
    return PanelEstadoControlador(modelo, vista)
```

**Organización de tests:**
```python
class TestCreacion:
    """Tests de creación e inicialización"""

class TestMetodos:
    """Tests de métodos públicos"""

class TestSignals:
    """Tests de señales PyQt"""

class TestIntegracion:
    """Tests de integración entre componentes"""
```

**Mocking de red:**
- TCP: `unittest.mock.patch` sobre `EphemeralSocketClient.send`
- Señales: `pytest-qt` con `qtbot.waitSignal()`

## Key Design Patterns

1. **MVC (Model-View-Controller)**: Cada panel UI
   - Modelo: dataclass inmutable, solo datos
   - Vista: QWidget, solo UI, sin lógica
   - Controlador: QObject, conecta modelo↔vista, emite señales

2. **Factory**: Centraliza creación de componentes con config consistente

3. **Coordinator**: Conecta señales entre componentes sin acoplamiento

4. **Compositor**: Ensambla vistas en layout, sin lógica de negocio

5. **Observer**: PyQt signals/slots para desacoplamiento

## Workflow: Implementación de Historias de Usuario

**IMPORTANTE:** Para ux_termostato, seguir este proceso estricto para cada Historia de Usuario.

### Invocación del Skill /implement-us

**Cuando el usuario escriba:** `/implement-us US-XXX` o `implementa US-XXX`

**Claude debe:**
1. Reconocer esto como solicitud de implementación de Historia de Usuario
2. Leer el proceso completo de `.claude/skills/implement-us.md`
3. Ejecutar las 9 fases documentadas paso a paso
4. Seguir la configuración de `.claude/skills/implement-us-config.json`

**Archivos clave del skill:**
- `.claude/skills/implement-us.md` - Proceso completo (9 fases)
- `.claude/skills/implement-us-config.json` - Configuración (quality gates, paths)
- `.claude/templates/` - Templates para BDD, plan, tests, reportes

### Proceso de Implementación (9 Fases)

Las fases están detalladas en `.claude/skills/implement-us.md`. Resumen:

**Estructura de archivos:**
```
ux_termostato/
├── docs/plans/US-XXX-plan.md           # Plan detallado con checklist
├── docs/reports/US-XXX-report.md       # Reporte final (opcional)
└── tests/features/US-XXX-*.feature     # Escenarios BDD (Gherkin)
```

### Paso 1: Escenarios BDD (Gherkin)
- Crear archivo `tests/features/US-XXX-nombre.feature`
- Definir escenarios que validen criterios de aceptación
- Formato Gherkin: Given/When/Then
- Referencia: `tests/features/US-001-ver-temperatura-ambiente.feature`

### Paso 2: Plan Detallado
- Crear archivo `docs/plans/US-XXX-plan.md`
- Incluir:
  - Info de la HU (título, puntos, prioridad)
  - Componentes a implementar (MVC completo)
  - Tasks con estimaciones (modelo, vista, controlador, tests)
  - Checklist de progreso actualizable
  - Quality gates
  - Lecciones aprendidas (post-implementación)
- Referencia: `docs/plans/US-001-plan.md`

### Paso 3: Implementación MVC
**Orden recomendado:**
1. Modelo (dataclass inmutable)
2. Vista (QWidget puro, sin lógica)
3. Controlador (QObject, conecta modelo↔vista)
4. `__init__.py` (exports)

**Actualizar plan:** Marcar cada tarea completada ✅

### Paso 4: Tests Unitarios
Para cada componente MVC:
- `tests/test_{panel}_modelo.py`
  - TestCreacion, TestInmutabilidad, TestValidacion
- `tests/test_{panel}_vista.py`
  - TestCreacion, TestActualizacion, TestEstilos
- `tests/test_{panel}_controlador.py`
  - TestCreacion, TestMetodos, TestSignals

**Actualizar conftest.py:** Agregar fixtures reutilizables

### Paso 5: Tests de Integración
- `tests/test_{panel}_integracion.py`
- Validar flujo completo: modelo → controlador → vista
- Simular recepción de datos desde servidor

### Paso 6: Implementar Steps BDD
- Implementar steps con pytest-bdd
- Ejecutar escenarios: `pytest tests/features/US-XXX-*.feature`
- Validar que todos los escenarios pasan

### Paso 7: Quality Gates
Validar que se cumple:
- **Coverage:** ≥ 95% (`pytest --cov=app --cov-report=html`)
- **Pylint:** ≥ 8.0 (`pylint app/presentacion/paneles/{panel}/`)
- **CC:** ≤ 10 promedio (`radon cc ...`)
- **MI:** > 20 (`radon mi ...`)

Generar reporte: `quality/reports/US-XXX-quality.json`

### Paso 8: Git Workflow
```bash
# Crear rama
git checkout -b development/simulador-ux-US-XXX

# Commits incrementales
git commit -m "feat(US-XXX): implementar modelo {Panel}"
git commit -m "feat(US-XXX): implementar vista {Panel}"
git commit -m "feat(US-XXX): implementar controlador {Panel}"
git commit -m "test(US-XXX): agregar tests unitarios"
git commit -m "test(US-XXX): agregar tests BDD"

# Push y PR
git push origin development/simulador-ux-US-XXX
# Crear PR → main
```

### Paso 9: Finalización
- Actualizar plan con resultados finales
- Documentar lecciones aprendidas
- Actualizar `CLAUDE.md` sección "Development Status"
- Merge PR a main

### Ejemplo de Referencia Completo

**US-001** (Display LCD) y **US-002** (Climatizador) son implementaciones de referencia:
- 100% coverage
- Pylint 10.00/10
- CC < 2, MI > 80
- Ratio tests/código: ~5:1

Ver `docs/plans/US-001-plan.md` para estructura exacta del plan.

## Development Status

### ux_termostato - En Desarrollo Activo

**Arquitectura:** MVC + Factory/Coordinator (siguiendo ADR-003)
**Documentación:** `ux_termostato/docs/HISTORIAS-USUARIO-UX-TERMOSTATO.md` (v2.2 - Actualizado 2026-01-23)
**Principio:** Cliente sin estado - No persiste datos, solo renderiza estado del RPi

**Total:** 16 historias, 61 puntos (9 completadas, 10 deestimadas, 7 pendientes)

---

#### ✅ COMPLETADAS (9 historias, 35 puntos)

**Paneles de Visualización:**
- ✅ US-001: Ver temperatura ambiente (3 pts)
  - Panel Display LCD, 100% coverage, Pylint 10/10
- ✅ US-002: Ver estado climatizador (5 pts)
  - Panel Climatizador (calor/frío/reposo), 100% coverage, Pylint 10/10
- ✅ US-003: Ver indicadores de alerta (2 pts)
  - Panel Indicadores LED (sensor/batería), 99% coverage, Pylint 9.66/10

**Control de Temperatura:**
- ✅ US-004: Aumentar temperatura (3 pts)
  - Panel ControlTemp, botón subir, 100% coverage
- ✅ US-005: Disminuir temperatura (3 pts)
  - Panel ControlTemp, botón bajar, 100% coverage
  - Métricas: Pylint 10/10, CC 1.58, MI 75.43

**Control de Encendido:**
- ✅ US-007: Encender termostato (3 pts)
  - Panel Power, botón power, 100% coverage, Pylint 10/10

**Refactorización:**
- ✅ US-006: Refactorizar panel ControlTemp (6 pts)
  - Fusión exitosa US-004 + US-005 en panel único

**Arquitectura - Capa de Dominio:**
- ✅ US-020: Capa de Dominio (5 pts)
  - `dominio/estado_termostato.py`: EstadoTermostato (dataclass inmutable)
  - `dominio/comandos.py`: ComandoPower, ComandoSetTemp, ComandoSetModoDisplay
  - Validaciones completas, serialización JSON, 100% coverage

**Arquitectura - Capa de Comunicación:**
- ✅ US-021: Capa de Comunicación (5 pts)
  - `comunicacion/servidor_estado.py`: ServidorEstado (recibe JSON del RPi, puerto 14001)
  - `comunicacion/cliente_comandos.py`: ClienteComandos (envía comandos al RPi, puerto 14000)
  - Comunicación bidireccional TCP, 34 tests, 95% coverage, Pylint 10/10, CC 1.85, MI 96.00
  - Análisis de diseño: 9.8/10 (cohesión alta, acoplamiento bajo, SOLID completo)

---

#### ❌ DESESTIMADAS (10 historias, 28 puntos)

**Redundancia funcional (US-003 ya cubre):**
- ❌ US-009: Alerta falla sensor (2 pts) - LEDs ya implementados
- ❌ US-010: Alerta batería baja (2 pts) - LEDs ya implementados

**Fuera de scope (desktop es cliente sin estado):**
- ❌ US-018: Persistir configuración (3 pts) - Estado pertenece al RPi
- ❌ US-019: Histórico temperatura (5 pts) - Datos históricos pertenecen al RPi

**Funcionalidad básica ya cubierta:**
- ❌ US-008: Apagar termostato (2 pts) - US-007 cubre toggle on/off
- ❌ US-012: Ver temperatura deseada (2 pts) - US-001 ya muestra ambas

**No críticas para MVP:**
- ❌ US-014: Logs de eventos (5 pts)
- ❌ US-016: Modo manual/auto (3 pts)
- ❌ US-017: Programar horarios (5 pts)

---

#### 🔲 PENDIENTES (7 historias, 26 puntos)

**Sprint 2 - Paneles Finales (3 historias, 8 pts)**
- 🔲 US-011: Cambiar vista display (3 pts)
  - Panel SelectorVista: toggle ambiente/deseada
- 🔲 US-013: Configurar IP Raspberry (3 pts)
  - Panel Conexión: IP/puerto del RPi
- 🔲 US-015: Ver estado conexión (2 pts)
  - Panel EstadoFooter: indicador conectado/desconectado

**Sprint 3 - Arquitectura e Integración (4 historias, 18 pts)**
- 🔲 US-022: Factory + Coordinator (5 pts)
  - `factory.py`: ComponenteFactoryUX crea todos los componentes
  - `coordinator.py`: UXCoordinator conecta señales entre capas
- 🔲 US-023: Compositor UI (3 pts)
  - `presentacion/ui_compositor.py`: ensambla layout de paneles
- 🔲 US-024: Ventana Principal (5 pts)
  - `presentacion/ui_principal.py`: main window, menú, lifecycle
- 🔲 US-025: Entry Point (5 pts)
  - `run.py`: configuración, factory, coordinator, ventana principal

---

#### 📊 Planificación

**2 Sprints restantes:**
- ✅ Sprint 1 (10 pts): COMPLETADO - US-020 Capa de Dominio + US-021 Capa de Comunicación
- Sprint 2 (8 pts): Paneles finales (US-011, US-013, US-015)
- Sprint 3 (18 pts): Arquitectura e integración (US-022 a US-025)

**Dependencias críticas:**
- ✅ US-020 completada - Capa de dominio (EstadoTermostato y Comandos)
- ✅ US-021 completada - Capa de comunicación (ServidorEstado y ClienteComandos)
- US-022 a US-024 tienen dependencias secuenciales
- US-025 es último, integra todo

**Directorios implementados:**
```
app/
├── factory.py              ✅ Creado (vacío, pendiente US-022)
├── coordinator.py          ✅ Creado (vacío, pendiente US-022)
├── configuracion/          ✅ Existente
├── dominio/                ✅ Completado (US-020)
│   ├── estado_termostato.py    - EstadoTermostato dataclass
│   └── comandos.py             - ComandoPower, ComandoSetTemp, ComandoSetModoDisplay
├── comunicacion/           ✅ Completado (US-021)
│   ├── servidor_estado.py      - ServidorEstado (recibe JSON del RPi)
│   └── cliente_comandos.py     - ClienteComandos (envía comandos al RPi)
└── presentacion/
    ├── ui_principal.py     ✅ Creado (vacío, pendiente US-024)
    ├── ui_compositor.py    ✅ Creado (vacío, pendiente US-023)
    └── paneles/
        ├── display/        ✅ Completado (US-001)
        ├── climatizador/   ✅ Completado (US-002)
        ├── indicadores/    ✅ Completado (US-003)
        ├── power/          ✅ Completado (US-007)
        ├── control_temp/   ✅ Completado (US-004, US-005, US-006)
        ├── selector_vista/ 🔲 Pendiente (US-011)
        ├── conexion/       🔲 Pendiente (US-013)
        └── estado_footer/  🔲 Pendiente (US-015)
```

### simulador_temperatura - Completo ✅
Coverage: ~95%+, Quality gates: ✅

### simulador_bateria - Completo ✅
Coverage: 96%, Quality gates: ✅

---

## Tracking de Tiempo

El sistema de tracking automático mide el tiempo real de implementación de Historias de Usuario durante la ejecución del skill `/implement-us`.

### Sistema Automático

El tracking se inicia y finaliza automáticamente:
- **Inicio:** Al invocar `/implement-us US-XXX`
- **Fin:** Al completar la Fase 9 (Reporte Final)
- **Granularidad:** Por tarea individual (modelo, vista, controlador, tests)
- **Almacenamiento:** `.claude/tracking/US-XXX-tracking.json`

### Comandos Manuales

#### `/track-pause [razón]`

Pausa el tracking actual. Útil durante reuniones o interrupciones.

```bash
/track-pause Reunión de equipo
/track-pause Almuerzo
/track-pause
```

**Respuesta:**
```
⏸️  Tracking pausado
   Duración actual: 1h 25min
```

---

#### `/track-resume`

Reanuda el tracking después de una pausa.

```bash
/track-resume
```

**Respuesta:**
```
▶️  Tracking reanudado
   Pausa: 20min
```

---

#### `/track-status`

Muestra el estado actual del tracking.

```bash
/track-status
```

**Respuesta:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️  TRACKING STATUS - US-004
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Progreso: Fase 3/9 (Implementación)
📋 Tarea actual: DisplayControlador (tarea 3/12)

⏰ Tiempos:
   • Inicio:       14:00:00
   • Transcurrido: 2h 15min
   • Efectivo:     2h 00min
   • Pausado:      15min
   • Estado:       ▶️  EN CURSO

✅ Completadas: 2/12 tareas
```

---

#### `/track-report [us_id]`

Genera un reporte inmediato de una US específica o de la activa.

```bash
/track-report              # Reporte de la US activa
/track-report US-001       # Reporte de US-001
```

**Respuesta:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 REPORTE DE TRACKING - US-001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Historia: Ver temperatura ambiente
🎯 Puntos: 3
📦 Producto: ux_termostato
⏱️  Estado: ✅ COMPLETADO

━━━ Tiempos ━━━

• Total:     3h 25min
• Efectivo:  3h 05min
• Pausado:   20min

━━━ Progreso ━━━

• Fases completadas: 9/9
• Tareas completadas: 12/12

━━━ Estimaciones ━━━

• Estimado: 135 min
• Real:     205 min
• Varianza: +51.9%

━━━ Archivos ━━━

• Tracking: .claude/tracking/US-001-tracking.json
• Reporte:  docs/reports/US-001-tracking-report.md (generado al finalizar)
```

---

#### `/track-history [--last N] [--producto X] [--desde YYYY-MM-DD]`

Muestra historial de todas las USs trackeadas con filtros opcionales.

```bash
/track-history                           # Todas las USs
/track-history --last 5                  # Últimas 5 USs
/track-history --producto ux_termostato  # Solo ux_termostato
/track-history --desde 2026-01-01        # Desde fecha
```

**Respuesta:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 HISTORIAL DE TRACKING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ US-003 | Ver indicadores de alerta      | 2pts |   2h 41min |   +19% | 2026-01-16
✅ US-002 | Ver estado climatizador        | 5pts |   5h 06min |   +27% | 2026-01-17
✅ US-001 | Ver temperatura ambiente       | 3pts |   3h 25min |   +52% | 2026-01-18
🔄 US-004 | Aumentar temperatura           | 3pts |   1h 30min |    +0% | 2026-01-18

📈 Promedios:
   • Tiempo por punto: 1.1h
   • Varianza promedio: +33%
   • Total USs: 4
   • Total puntos: 13
```

---

### Archivos Generados

Al finalizar la implementación de una US, se generan automáticamente:

1. **Tracking JSON** (`.claude/tracking/US-XXX-tracking.json`)
   - Datos raw con timestamps de cada fase y tarea
   - Pausas registradas
   - Métricas de calidad

2. **Reporte Markdown** (`docs/reports/US-XXX-tracking-report.md`)
   - Resumen ejecutivo
   - Timeline de fases con gráficos ASCII
   - Breakdown por tarea
   - Análisis de varianzas (estimado vs real)
   - Insights y recomendaciones

3. **Dashboard JSON** (`.claude/metrics/summary.json`)
   - Agregación de todas las USs implementadas
   - Métricas por fase y tipo de tarea
   - Velocity (puntos/día, horas/punto)
   - Tendencias de calidad

### Uso con Python

Los comandos pueden invocarse programáticamente:

```python
from .claude.tracking.commands import (
    track_pause,
    track_resume,
    track_status,
    track_report,
    track_history
)

# Pausar
result = track_pause("Reunión")
print(result["message"])

# Consultar estado
result = track_status()
print(result["message"])

# Resumir
result = track_resume()
print(result["message"])

# Generar reporte
result = track_report("US-001")
print(result["message"])

# Ver historial
result = track_history(last=5, producto="ux_termostato")
print(result["message"])
```

### Configuración

El tracking se configura en `.claude/skills/implement-us-config.json`:

```json
{
  "tracking": {
    "enabled": true,
    "auto_start": true,
    "track_user_approval_time": true,
    "generate_reports": true,
    "report_formats": ["markdown", "json"]
  }
}
```

---

## Important Notes

- **Siempre leer CLAUDE.md cuando cambies de producto** - simulador_temperatura, simulador_bateria y ux_termostato tienen sutiles diferencias
- **ux_termostato en desarrollo:** Revisar "Development Status" arriba para conocer el estado actual y próximas tareas
- **Tests requieren PyQt6** - configurado en pytest.ini con `qt_api = pyqt6`
- **Venv en .venv** (no venv) - ya está en .gitignore
- **Documentación detallada** en `{producto}/docs/arquitectura.md` para cada simulador
- **Coverage objetivo**: ~95%+ según estándares del proyecto
- **Pylint puede quejarse de PyQt6** - usar `# pylint: disable=...` solo si es falso positivo de PyQt
