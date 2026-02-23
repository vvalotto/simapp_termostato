# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema HIL (Hardware-in-the-Loop) con tres aplicaciones PyQt6 que simulan sensores y UI para testing del sistema ISSE_Termostato en Raspberry Pi. Requiere Python 3.12+.

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
# Setup (Python 3.12+)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configurar RASPBERRY_IP

# Ejecutar simuladores
python simulador_temperatura/run.py
python simulador_bateria/run.py
python ux_termostato/run.py

# Tests (ejecutar desde directorio del producto, e.g. cd ux_termostato)
pytest                                               # Todos los tests
pytest tests/test_display_modelo.py                  # Archivo específico
pytest tests/test_display_modelo.py::TestCreacion    # Clase específica
pytest tests/test_display_modelo.py::TestCreacion::test_valores_iniciales  # Test específico
pytest --cov=app --cov-report=html                   # Con coverage (reporte en htmlcov/)
pytest --cov=app --cov-report=term-missing           # Coverage en terminal
pytest tests/features/                               # Solo tests BDD
pytest -k "display"                                  # Tests que contienen "display"

# Quality (ejecutar desde directorio del producto)
pylint app/                                          # Linting
python quality/scripts/calculate_metrics.py app      # Generar métricas CC/MI
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
        ├── selector_vista/ # Toggle ambiente/deseada
        ├── conexion/       # Config IP/puerto
        └── estado_conexion/# Indicador LED conectado/desconectado
```

**Diferencia con simuladores:**
- **Comunicación bidireccional**: Recibe estado (puerto 14001) y envía comandos (14000)
- **Sin generador**: No simula datos, solo renderiza estado recibido del RPi
- **Sin persistencia**: Estado es efímero, pertenece al RPi

### compartido/

Código reutilizable entre productos:
- `networking/`:
  - `EphemeralSocketClient` - patrón "conectar→enviar→cerrar" para clientes TCP
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

1. **config.json** (root): Valores por defecto, versionado en git
   - IP Raspberry (default: 127.0.0.1), puertos, parámetros de simulación

2. **.env** (root): Overrides locales, NO versionado
   - `RASPBERRY_IP` - IP del RPi real
   - `PUERTO_TEMPERATURA`, `PUERTO_BATERIA`, etc.
   - `DEBUG` - modo debug

Los simuladores leen config.json y sobrescriben con variables de .env si existen.

## Testing Patterns

Tests en `tests/` con pytest y pytest-qt:

**Estructura de fixtures** (`conftest.py`):
```python
@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def config():
    return ConfigSimuladorBateria(...)

@pytest.fixture
def modelo(config):
    return PanelEstadoModelo(...)
```

**Organización de tests por panel:**
```python
class TestCreacion:    # inicialización e invariantes
class TestMetodos:     # métodos públicos
class TestSignals:     # señales PyQt (usa qtbot.waitSignal())
class TestIntegracion: # flujo completo modelo → controlador → vista
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

3. **Coordinator**: Conecta señales entre componentes sin acoplamiento directo

4. **Compositor**: Ensambla vistas en layout, sin lógica de negocio

5. **Observer**: PyQt signals/slots para desacoplamiento

## Development Status

Los tres productos están completos:

- **simulador_temperatura** ✅ - Coverage ~95%+, quality gates OK
- **simulador_bateria** ✅ - Coverage 96%, quality gates OK
- **ux_termostato** ✅ - Coverage ~96%, Pylint 9.91/10

Documentación detallada de cada producto: `{producto}/docs/`.

## Important Notes

- **pytest.ini en cada producto** - ejecutar pytest desde el directorio del producto, no desde el root
- **Venv en `.venv`** (no `venv`) - ya está en .gitignore
- **Tests requieren PyQt6** - configurado con `qt_api = pyqt6`
- **pylint puede quejarse de PyQt6** - usar `# pylint: disable=...` solo para falsos positivos de PyQt
- **Coverage objetivo**: ~95%+ según estándares del proyecto
- **Documentación técnica** completa en la [Wiki del proyecto](../../wiki) (sincronización automática vía GitHub Actions)
