# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ISSE_Simuladores is a Hardware-in-the-Loop (HIL) testing system comprising three PyQt6 desktop applications that communicate with the ISSE_Termostato embedded system running on Raspberry Pi.

## Architecture

```
Desktop Simulators (Mac/PC) ←→ TCP/IP ←→ Raspberry Pi (ISSE_Termostato)

Three Products:
├── simulador_temperatura/ → Client TCP (sends float values)
├── simulador_bateria/     → Client TCP (sends float values)
└── ux_termostato/         → Server (receives JSON state), Client (sends JSON commands)

Shared code:
└── compartido/            → Base socket classes, PyQt6 widgets, dark theme styles
```

**Communication Protocol:**
- Simulators → Raspberry: Plain text `<float>\n` (e.g., `23.5\n`)
- Raspberry → UX: JSON state object (temp_actual, temp_deseada, estado_climatizador, nivel_bateria)
- UX → Raspberry: JSON commands (set_temp_deseada, power on/off, set_modo_display)

**Ports (configured in config.json and .env):**
- 12000: temperatura, 11000: bateria, 13000: seteo_temperatura
- 14000: selector_temperatura, 14001: visualizador_temperatura, 14002: visualizador_bateria

## Commands

### Installation
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your Raspberry Pi IP
```

### Running Applications
```bash
python simulador_temperatura/run.py
python simulador_bateria/run.py
python ux_termostato/run.py
```

### Testing
```bash
# Run all tests for a product
cd simulador_temperatura && pytest tests/ -v

# Run single test file
pytest tests/test_generador_temperatura.py -v

# Run single test function
pytest tests/test_generador_temperatura.py::test_generar_valor -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Quality Analysis (per product)
```bash
cd <product>
python quality/scripts/calculate_metrics.py app
python quality/scripts/validate_gates.py quality/reports/quality_*.json
python quality/scripts/generate_report.py quality/reports/quality_*.json
```

## Quality Gates

Each product must meet these thresholds:
- **Cyclomatic Complexity:** average ≤ 10
- **Maintainability Index:** average > 20
- **Pylint Score:** ≥ 8.0

Grades: A (3/3 gates), B (2/3), C (1/3), F (0/3)

## Technology Stack

- **Python:** 3.12+
- **GUI:** PyQt6 6.7.0, pyqtgraph 0.13.3
- **Testing:** pytest 8.0.0, pytest-qt 4.2.0
- **Quality:** radon, pylint, pytest-cov

## Product Module Structure

**simulador_temperatura** (v1.0.0 - arquitectura MVC):
```
simulador_temperatura/
├── run.py                      # Entry point + AplicacionSimulador (lifecycle)
├── app/
│   ├── factory.py              # ComponenteFactory (creacion de componentes)
│   ├── coordinator.py          # SimuladorCoordinator (conexion de senales)
│   ├── configuracion/          # ConfigManager, ConfigSimuladorTemperatura
│   ├── dominio/                # GeneradorTemperatura, VariacionSenoidal, EstadoTemperatura
│   ├── comunicacion/           # ClienteTemperatura, ServicioEnvioTemperatura
│   └── presentacion/           # UI + paneles MVC
│       ├── ui_compositor.py    # UIPrincipalCompositor (layout)
│       └── paneles/            # MVC: estado/, control_temperatura/, grafico/, conexion/
├── tests/                      # 283 tests
├── quality/                    # Scripts e informes de calidad
└── docs/                       # arquitectura.md
```

**simulador_bateria, ux_termostato** (original architecture):
```
<product>/
├── run.py
├── app/
│   ├── configuracion/          # Config singleton
│   ├── servicios/              # Main UI window
│   ├── general/                # Business logic
│   └── datos/                  # Socket client/server
├── tests/
└── quality/scripts/
```

**compartido** (shared library):
```
compartido/
├── networking/                 # BaseSocketClient, BaseSocketServer, EphemeralSocketClient
├── widgets/                    # ConfigPanel, LedIndicator, LogViewer, StatusIndicator
└── estilos/                    # ThemeProvider, QSS generation, dark theme
```

## Configuration

- `config.json`: Network settings, simulation parameters (committed)
- `.env`: Environment overrides for IP/ports (not committed, copy from `.env.example`)

## Estado Actual

### simulador_temperatura - v1.0.0 (Completado)

**Branch:** `main`
**Fecha:** 2026-01-10

Refactorizacion arquitectonica completada con exito:
- **Fase 1** (ST-50, ST-51): Metodo publico `actualizar_variacion`, eliminado anti-patron
- **Fase 2** (ST-52, ST-53, ST-54): Estructura MVC base, Panel Estado migrado
- **Fase 3** (ST-55, ST-56, ST-57): Paneles Control, Grafico, Conexion migrados a MVC
- **Fase 4** (ST-58, ST-59, ST-60, ST-61): Factory, Coordinator, UIPrincipalCompositor

### Metricas de Calidad
| Metrica | Valor | Umbral |
|---------|-------|--------|
| Tests | 283 | - |
| Pylint | 9.52/10 | >= 8.0 |
| Complejidad Ciclomatica | 1.36 | <= 10 |
| Indice Mantenibilidad | 70.10 | > 20 |
| Grade | A | - |

### Patrones Implementados
- **MVC:** `app/presentacion/paneles/` (4 paneles)
- **Factory:** `app/factory.py` (ComponenteFactory)
- **Coordinator:** `app/coordinator.py` (SimuladorCoordinator)
- **Compositor:** `app/presentacion/ui_compositor.py`

### Documentacion
- `README.md`: Documentacion principal
- `CHANGELOG.md`: Historial de versiones
- `docs/arquitectura.md`: Diagramas y patrones
- `quality/reports/informe_calidad_diseno.md`: Analisis SOLID

### Proximos Pasos (otros productos)
- Aplicar misma arquitectura a `simulador_bateria`
- Aplicar misma arquitectura a `ux_termostato`

## Integration

- **Atlassian MCP:** Configured in `.mcp.json` for Jira/Confluence integration
- **GitHub Actions:** Workflow syncs README.md to Confluence on push to main
