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

```bash
# Instalar
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configurar IP de Raspberry

# Ejecutar
python simulador_temperatura/run.py
python simulador_bateria/run.py
python ux_termostato/run.py

# Testing (ejecutar desde directorio del producto)
cd simulador_bateria  # o simulador_temperatura
pytest tests/ -v                                                   # Todos los tests
pytest tests/test_generador_bateria.py -v                          # Un archivo
pytest tests/test_generador_bateria.py::TestGeneradorBateria -v    # Una clase
pytest tests/test_generador_bateria.py::test_generar_valor -v      # Una funcion
pytest tests/ --cov=app --cov-report=html                          # Coverage HTML

# Quality (ejecutar desde directorio del producto)
pylint app/
python quality/scripts/calculate_metrics.py app
python quality/scripts/validate_gates.py quality/reports/quality_*.json
```

## Quality Gates

Cada producto debe cumplir: CC promedio ≤ 10, MI promedio > 20, Pylint ≥ 8.0

## Architecture

### Simuladores (temperatura y bateria) - MVC + Factory/Coordinator

Ambos simuladores usan arquitectura identica:

```
run.py                      # AplicacionSimulador (lifecycle)
app/
├── factory.py              # ComponenteFactory - crea todos los componentes
├── coordinator.py          # SimuladorCoordinator - conecta signals PyQt
├── configuracion/          # ConfigManager, ConfigSimulador*, constantes
├── dominio/                # Generador*, Estado* (logica de negocio pura)
├── comunicacion/           # Cliente*, ServicioEnvio* (TCP via EphemeralSocketClient)
└── presentacion/
    ├── ui_compositor.py    # Composicion del layout principal
    └── paneles/            # Cada panel tiene: modelo.py, vista.py, controlador.py
        ├── conexion/       # Config IP/puerto
        ├── control/        # Slider voltaje/temperatura
        └── estado/         # Contadores envios exitosos/fallidos
```

**Flujo de signals PyQt:**
```
Generador ──valor_generado──► Controladores ──signal──► ServicioEnvio ──TCP──► RPi
                                    │
                                    ▼
                               Vista (UI)
```

**Patron Factory/Coordinator:** `factory.py` crea componentes independientes, `coordinator.py` los conecta via signals evitando dependencias circulares.

### ux_termostato

Arquitectura mas simple: widgets directos sin Factory/Coordinator.

### compartido/

Codigo reutilizable entre productos:
- `networking/`: EphemeralSocketClient (conexion-por-mensaje), BaseSocketServer
- `widgets/`: ConfigPanel, LedIndicator, LogViewer, StatusIndicator
- `estilos/`: ThemeProvider con dark theme
- `quality/scripts/`: calculate_metrics.py, validate_gates.py (copiados a cada producto)

## Communication Protocol

| Puerto | Direccion | Formato | Uso |
|--------|-----------|---------|-----|
| 12000 | Desktop → RPi | `<float>\n` | Temperatura simulada |
| 11000 | Desktop → RPi | `<float>\n` | Voltaje bateria [0.0-5.0] |
| 13000 | Desktop → RPi | `aumentar\|disminuir` | Seteo temperatura |
| 14000 | Desktop → RPi | `ambiente\|deseada` | Selector display |
| 14001 | RPi → Desktop | `<etiqueta>: <valor>` | Visualizador temperatura |
| 14002 | RPi → Desktop | `<float>` | Visualizador bateria |

## Configuration

- `config.json`: Parametros de red y simulacion (committed, valores por defecto)
- `.env`: Override de IP/puertos para entorno local (not committed)

## Testing Patterns

Los tests usan pytest con fixtures en `conftest.py`:
- Agrupar tests por clase: `TestCreacion`, `TestMetodos`, `TestSignals`, `TestIntegracion`
- Fixtures por nivel: config → modelo → componente
- Mock de conexiones TCP con `unittest.mock`
