# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ISSE_Simuladores is a Hardware-in-the-Loop (HIL) testing system comprising three PyQt6 desktop applications that communicate with the ISSE_Termostato embedded system running on Raspberry Pi. Currently in design/planning phase.

## Architecture

```
Desktop Simulators (Mac/PC) ←→ TCP/IP ←→ Raspberry Pi (ISSE_Termostato)

Three Products:
├── simulador_temperatura/ → Client TCP port 14001 (sends float values)
├── simulador_bateria/     → Client TCP port 14002 (sends float values)
└── ux_termostato/         → Server 14003 (receives JSON state), Client 14004 (sends JSON commands)

Shared code:
└── compartido/            → Base socket classes, PyQt6 widgets, dark theme styles
```

**Communication Protocol:**
- Simulators → Raspberry: Plain text `<float>\n` (e.g., `23.5\n`)
- Raspberry → UX: JSON state object (temp_actual, temp_deseada, estado_climatizador, nivel_bateria)
- UX → Raspberry: JSON commands (set_temp_deseada, power on/off, set_modo_display)

## Commands

### Installation
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Applications
```bash
python simulador_temperatura/run.py
python simulador_bateria/run.py
python ux_termostato/run.py
```

### Testing (per product)
```bash
cd simulador_temperatura
pytest tests/ -v
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

Each product follows this pattern:
```
<product>/
├── run.py                    # Entry point
├── app/
│   ├── configuracion/        # Config singleton, settings
│   ├── servicios/            # Main UI window (ui_principal.py)
│   ├── general/              # Business logic
│   └── datos/                # Socket client/server
├── tests/
└── quality/scripts/          # Metrics calculation and validation
```

## Integration

- **Atlassian MCP:** Configured in `.mcp.json` for Jira/Confluence integration
- **GitHub Actions:** Workflow syncs README.md to Confluence on push to main
