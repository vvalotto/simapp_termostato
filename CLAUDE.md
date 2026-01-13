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

# Testing (desde directorio del producto)
cd simulador_temperatura
pytest tests/ -v                                                   # Todos
pytest tests/test_generador_temperatura.py -v                      # Archivo
pytest tests/test_generador_temperatura.py::test_generar_valor -v  # Funcion
pytest tests/ --cov=app --cov-report=html                          # Coverage

# Quality (desde directorio del producto)
pylint app/
python quality/scripts/calculate_metrics.py app
python quality/scripts/validate_gates.py quality/reports/quality_*.json
```

## Quality Gates

Cada producto debe cumplir: CC promedio ≤ 10, MI promedio > 20, Pylint ≥ 8.0

## Architecture

### Simuladores (temperatura y bateria) - MVC + Factory/Coordinator

Ambos usan la misma arquitectura:

```
run.py                      # AplicacionSimulador (lifecycle)
app/
├── factory.py              # ComponenteFactory - crea todos los componentes
├── coordinator.py          # SimuladorCoordinator - conecta signals PyQt
├── configuracion/          # ConfigManager, ConfigSimulador*
├── dominio/                # Generador*, Estado* (logica de negocio)
├── comunicacion/           # Cliente*, ServicioEnvio* (TCP con EphemeralSocketClient)
└── presentacion/
    ├── ui_compositor.py    # Composicion del layout
    └── paneles/            # MVC: modelo.py, vista.py, controlador.py
```

**Flujo de signals:**
```
Generador ──signal──► Controladores ──signal──► ServicioEnvio ──TCP──► Raspberry
                           │
                           ▼
                      Vista (UI)
```

### ux_termostato

Arquitectura mas simple sin Factory/Coordinator.

### compartido/

- `networking/`: BaseSocketClient, BaseSocketServer, EphemeralSocketClient
- `widgets/`: ConfigPanel, LedIndicator, LogViewer, StatusIndicator
- `estilos/`: ThemeProvider, dark theme

## Communication Protocol

| Puerto | Direccion | Formato | Uso |
|--------|-----------|---------|-----|
| 12000 | Sim → RPi | `<float>\n` | Temperatura |
| 11000 | Sim → RPi | `<float>\n` | Bateria (voltaje) |
| 13000 | UX → RPi | `aumentar\|disminuir` | Seteo temperatura |
| 14000 | UX → RPi | `ambiente\|deseada` | Selector display |
| 14001 | RPi → UX | `<etiqueta>: <valor>` | Visualizador temp |
| 14002 | RPi → UX | `<float>` | Visualizador bateria |

## Configuration

- `config.json`: Parametros de red y simulacion (committed)
- `.env`: Override de IP/puertos (not committed)

## Estado de Desarrollo - Simulador Batería

### Branch Activo
`development/simulador-bateria-fase3`

### Fases Completadas

| Fase | Tickets | Estado |
|------|---------|--------|
| Fase 1: Dominio y Configuración | SB-1 a SB-4 | ✅ Completada |
| Fase 2: Comunicación | SB-5, SB-6 | ✅ Completada |
| Fase 3: Presentación MVC | SB-7, SB-8, SB-9 | ✅ Completada |
| Fase 4: Orquestación | SB-10, SB-11, SB-12 | ⏳ Pendiente |
| Fase 5: Calidad | SB-13, SB-14 | ⏳ Pendiente |

### Próximos Tickets (Fase 4)
- **SB-10/ST-65**: ComponenteFactory - crear todos los componentes
- **SB-11/ST-66**: SimuladorCoordinator - conectar signals
- **SB-12/ST-67**: UIPrincipalCompositor - componer paneles

### Revisión de Diseño Pendiente
Hallazgos de revisión de cohesión/acoplamiento/SOLID en capa presentación:

1. `PanelEstadoControlador` maneja contadores de envío (considerar extraer a capa comunicación)
2. `ConexionPanelVista` tiene acoplamiento concreto con `compartido.widgets`
3. `UIPrincipalCompositor` sin type hints para controladores
4. Vistas con métodos no definidos en `VistaBase` (ISP)

Calificación general: 8/10 - Mejoras para Fase 5.

### Referencia Jira
Tickets detallados en `jira_estructura_proyecto.md` y en Jira proyecto ST (Simuladores Termostato).
