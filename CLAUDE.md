# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ISSE_Simuladores is a Hardware-in-the-Loop (HIL) testing system comprising three PyQt6 desktop applications that communicate with the ISSE_Termostato embedded system running on Raspberry Pi.

## Architecture

```
Desktop Simulators (Mac/PC) ←→ TCP/IP ←→ Raspberry Pi (ISSE_Termostato)

Products:
├── simulador_temperatura/ → Client TCP (sends float values to :12000)
├── simulador_bateria/     → Client TCP (sends float values to :11000)
└── ux_termostato/         → Server + Client (receives state, sends commands)

Shared code:
└── compartido/            → Base socket classes, PyQt6 widgets, dark theme
```

**Communication Protocol:**
- Simulators → Raspberry: Plain text `<float>\n` (e.g., `23.5\n`)
- Raspberry → UX: JSON state object (temp_actual, temp_deseada, estado_climatizador, nivel_bateria)
- UX → Raspberry: JSON commands (set_temp_deseada, power on/off, set_modo_display)

**Ports:**
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
# Run all tests for a product (must cd into product directory)
cd simulador_temperatura && pytest tests/ -v

# Run single test file
pytest tests/test_generador_temperatura.py -v

# Run single test function
pytest tests/test_generador_temperatura.py::test_generar_valor -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Linting
```bash
cd <product>
pylint app/
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

## Product Architectures

### simulador_temperatura (v1.0.0 - MVC architecture)

Uses Factory, Coordinator, and Compositor patterns with MVC panels:

```
run.py                          # Entry point + AplicacionSimulador (lifecycle)
app/
├── factory.py                  # ComponenteFactory (creates all components)
├── coordinator.py              # SimuladorCoordinator (connects PyQt signals)
├── configuracion/              # ConfigManager, ConfigSimuladorTemperatura
├── dominio/                    # GeneradorTemperatura, VariacionSenoidal, EstadoTemperatura
├── comunicacion/               # ClienteTemperatura, ServicioEnvioTemperatura
└── presentacion/
    ├── ui_compositor.py        # UIPrincipalCompositor (layout composition)
    └── paneles/                # MVC pattern: modelo.py, vista.py, controlador.py
        ├── base.py             # ModeloBase, VistaBase, ControladorBase
        ├── estado/             # Temperature display panel
        ├── control_temperatura/# Sliders and mode controls
        ├── grafico/            # Real-time temperature graph
        └── conexion/           # Connection settings panel
```

Key classes:
- `ComponenteFactory`: Creates GeneradorTemperatura, ClienteTemperatura, ServicioEnvio, and all MVC controllers
- `SimuladorCoordinator`: Connects signals between Generador ↔ Controllers ↔ Servicio
- `UIPrincipalCompositor`: Composes controller views into main window layout

### simulador_bateria, ux_termostato (original architecture)

```
run.py
app/
├── configuracion/          # Config singleton
├── servicios/              # Main UI window
├── general/                # Business logic
└── datos/                  # Socket client/server
```

### compartido (shared library)

```
compartido/
├── networking/             # BaseSocketClient, BaseSocketServer, EphemeralSocketClient
├── widgets/                # ConfigPanel, LedIndicator, LogViewer, StatusIndicator
└── estilos/                # ThemeProvider, QSS generation, dark theme
```

## Configuration

- `config.json`: Network settings, simulation parameters (committed)
- `.env`: Environment overrides for IP/ports (not committed, copy from `.env.example`)

## Key Patterns (simulador_temperatura)

1. **MVC per panel**: Each panel has modelo.py (dataclass), vista.py (QWidget), controlador.py (QObject with signals)
2. **Factory**: `ComponenteFactory` creates all components with consistent configuration
3. **Coordinator**: `SimuladorCoordinator` manages all PyQt signal connections, decoupling lifecycle from wiring
4. **Compositor**: `UIPrincipalCompositor` only handles layout, receives pre-configured controllers

## Integration

- **Atlassian MCP:** Configured in `.mcp.json` for Jira/Confluence integration
- **GitHub Actions:** Workflow syncs README.md to Confluence on push to main
