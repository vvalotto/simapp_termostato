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

## Important Notes

- **Siempre leer CLAUDE.md cuando cambies de producto** - simulador_temperatura, simulador_bateria y ux_termostato tienen sutiles diferencias
- **Tests requieren PyQt6** - configurado en pytest.ini con `qt_api = pyqt6`
- **Venv en .venv** (no venv) - ya está en .gitignore
- **Documentación detallada** en `{producto}/docs/arquitectura.md` para cada simulador
- **Coverage objetivo**: ~95%+ según estándares del proyecto
- **Pylint puede quejarse de PyQt6** - usar `# pylint: disable=...` solo si es falso positivo de PyQt
