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
`development/simulador-bateria-fase5`

### Fases Completadas

| Fase | Tickets | Estado |
|------|---------|--------|
| Fase 1: Dominio y Configuración | SB-1 a SB-4 | ✅ Completada |
| Fase 2: Comunicación | SB-5, SB-6 | ✅ Completada |
| Fase 3: Presentación MVC | SB-7, SB-8, SB-9 | ✅ Completada |
| Fase 4: Orquestación | SB-10, SB-11, SB-12 | ✅ Completada (con bugs corregidos) |
| Fase 5: Calidad - Tests Fase 1 | SB-13/ST-65 | ✅ Completada |
| Fase 5: Calidad - Tests Fase 2-4 | SB-13/ST-65 (cont.) | ⏳ Siguiente |
| Fase 5: Quality Gates | SB-14/ST-66 | ⏳ Pendiente |

### Última Sesión (2026-01-13)

**Completado:**
- ✅ Implementados 84 tests unitarios Fase 1 (100% passing)
- ✅ Coverage ~96% en componentes testeados (dominio, comunicación, configuración)
- ✅ Corregidos 3 bugs críticos en código producción:
  - Error handling en `ClienteBateria` (enviar_voltaje sync/async)
  - Error handling en `ServicioEnvioBateria` (_on_valor_generado)
  - Voltage clamping en `GeneradorBateria` (previene valores fuera de rango [0.0-5.0])
- ✅ Documentación completa en `simulador_bateria/docs/`:
  - `fase1_completada.md` - Resumen con métricas
  - `fase1_resultados_tests.md` - Análisis de fallas y fixes
  - `plan_tests_unitarios.md` - Plan 4 fases completo

**Tests creados (7 archivos, 84 tests):**
- `tests/conftest.py` - Fixtures globales (5 niveles)
- `tests/test_config.py` - ConfigSimuladorBateria y ConfigManager (8 tests)
- `tests/test_estado_bateria.py` - EstadoBateria dataclass (15 tests)
- `tests/test_generador_bateria.py` - GeneradorBateria core (20 tests)
- `tests/test_cliente_bateria.py` - ClienteBateria TCP (20 tests)
- `tests/test_servicio_envio.py` - ServicioEnvioBateria integración (21 tests)

### Próxima Sesión: Tests Unitarios Fase 2

**Objetivo:** Implementar tests para modelos MVC y factory (~50 tests adicionales)

**Archivos a crear:**
1. `tests/test_estado_bateria_panel_modelo.py` - Contadores, tasa_exito, porcentaje
2. `tests/test_control_panel_modelo.py` - Conversión voltaje ↔ paso slider (CRÍTICO)
3. `tests/test_conexion_panel_modelo.py` - Validación IP/puerto
4. `tests/test_panel_estado_controlador.py` - Actualización estado, signals
5. `tests/test_factory.py` - Creación de 4 componentes (CRÍTICO)

**Coverage objetivo:** +15-20% (de 34% a ~50%)

**Comandos útiles:**
```bash
cd simulador_bateria
pytest tests/ -v                                    # Ejecutar todos los tests
pytest tests/ --cov=app --cov-report=html          # Ver coverage
pytest tests/test_generador_bateria.py -v          # Test específico
```

**Patrón a seguir:**
- Usar fixtures de `conftest.py` como base
- Agrupar tests por clases (Creacion, Metodos, Signals, Integracion)
- Tests de conversión bidireccional en ControlPanelModelo son críticos
- Factory tests deben verificar creación de todos los componentes

### Referencia
- Plan detallado: `simulador_bateria/docs/plan_tests_unitarios.md`
- Tickets Jira: `jira_estructura_proyecto.md` y proyecto ST (Simuladores Termostato)
