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

**simulador_temperatura** (refactored architecture):
```
simulador_temperatura/
├── run.py                      # Entry point + AplicacionSimulador orchestrator
├── app/
│   ├── configuracion/          # ConfigManager, ConfigSimuladorTemperatura
│   ├── dominio/                # GeneradorTemperatura, VariacionSenoidal, EstadoTemperatura
│   ├── comunicacion/           # ClienteTemperatura, ServicioEnvioTemperatura
│   └── presentacion/           # UIPrincipal, ControlTemperatura, GraficoTemperatura
├── tests/
└── quality/scripts/
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

## Ongoing Refactoring

`simulador_temperatura` is undergoing architectural refactoring. See `simulador_temperatura/docs/plan_refactorizacion.md` for the 5-phase plan focusing on:
- Eliminating anti-patterns (private member access)
- MVC pattern for presentation panels
- Factory and Coordinator patterns for orchestration

## Integration

- **Atlassian MCP:** Configured in `.mcp.json` for Jira/Confluence integration
- **GitHub Actions:** Workflow syncs README.md to Confluence on push to main
