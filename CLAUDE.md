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

# Testing (ejecutar desde directorio raiz o del producto)
cd simulador_bateria  # o simulador_temperatura
pytest tests/ -v                                                   # Todos los tests
pytest tests/test_generador_bateria.py -v                          # Un archivo
pytest tests/test_generador_bateria.py::TestGeneradorBateria -v    # Una clase
pytest tests/test_generador_bateria.py::TestGeneradorBateria::test_generar_valor -v  # Test especifico
pytest tests/ --cov=app --cov-report=html                          # Coverage HTML en htmlcov/

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

### ux_termostato

Arquitectura más simple sin Factory/Coordinator:
```
app/
├── configuracion/          # Config manager
├── datos/                  # Modelos de datos
├── general/                # Main window
└── servicios/              # Servicios de red
```

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
**Documentación:** `ux_termostato/docs/HISTORIAS-USUARIO-UX-TERMOSTATO.md`

**Sprint 1 - MVP Básico (35 puntos)**

Semana 1 - Completado: 10/15 puntos
- ✅ US-001: Ver temperatura ambiente (3 pts) - Panel Display con 100% coverage
- ✅ US-002: Ver estado climatizador (5 pts) - Panel Climatizador con 100% coverage
- ✅ US-003: Ver indicadores de alerta (2 pts) - Panel Indicadores con 99% coverage
- ⏭️ **PRÓXIMO: US-007: Encender termostato (3 pts)** - Panel Power
- 🔲 US-008: Apagar termostato (2 pts)

Semana 2 - Pendiente: 0/16 puntos
- 🔲 US-004: Aumentar temperatura (3 pts)
- 🔲 US-005: Disminuir temperatura (3 pts)
- 🔲 US-009: Alerta falla sensor (2 pts)
- 🔲 US-011: Cambiar vista (3 pts)
- 🔲 US-013: Configurar IP (3 pts)
- 🔲 US-015: Estado conexión (2 pts)

**Paneles implementados:**
- `presentacion/paneles/display/` - Display LCD principal
- `presentacion/paneles/climatizador/` - Indicadores calor/reposo/frío
- `presentacion/paneles/indicadores/` - LEDs de alerta (sensor, batería)

**Paneles pendientes:**
- `control_temp/` - Botones subir/bajar temperatura
- `selector_vista/` - Toggle ambiente/deseada
- `power/` - Botón encender/apagar
- `estado_footer/` - Info de estado
- `conexion/` - Config IP/puerto

**Capas pendientes:**
- `app/dominio/` - EstadoTermostato, ComandoTermostato
- `app/comunicacion/` - ServidorEstado, ClienteComandos
- `app/factory.py` - ComponenteFactoryUX
- `app/coordinator.py` - UXCoordinator

### simulador_temperatura - Completo ✅
Coverage: ~95%+, Quality gates: ✅

### simulador_bateria - Completo ✅
Coverage: 96%, Quality gates: ✅

## Important Notes

- **Siempre leer CLAUDE.md cuando cambies de producto** - simulador_temperatura, simulador_bateria y ux_termostato tienen sutiles diferencias
- **ux_termostato en desarrollo:** Revisar "Development Status" arriba para conocer el estado actual y próximas tareas
- **Tests requieren PyQt6** - configurado en pytest.ini con `qt_api = pyqt6`
- **Venv en .venv** (no venv) - ya está en .gitignore
- **Documentación detallada** en `{producto}/docs/arquitectura.md` para cada simulador
- **Coverage objetivo**: ~95%+ según estándares del proyecto
- **Pylint puede quejarse de PyQt6** - usar `# pylint: disable=...` solo si es falso positivo de PyQt
