# Plan: Implementar Tests Unitarios para Simulador Batería (ST-65/SB-13)

## Objetivo

Crear suite completa de tests unitarios para simulador_bateria con coverage ≥80%, siguiendo los patrones establecidos en simulador_temperatura.

## Estrategia: Implementación por Fases (4 Semanas)

### Fase 1: Fundamentos (Semana 1) - 6 archivos
**Prioridad:** CRÍTICA - 60% del coverage total

1. **conftest.py + __init__.py** - Setup base
   - Fixtures globales: config, mock_ephemeral_client, generador, mock_cliente, servicio
   - PYTHONPATH setup

2. **test_config.py** - Configuración
   - ConfigSimuladorBateria (dataclass)
   - ConfigManager (singleton)

3. **test_estado_bateria.py** - Dominio puro
   - Métodos: `to_string()` (formato "X.XX\n"), `validar_rango()`
   - Mock: datetime.now()

4. **test_generador_bateria.py** - Dominio Qt (CORE)
   - Métodos: `set_voltaje()`, `generar_valor()`, `iniciar()`, `detener()`
   - Signals: `valor_generado`, `voltaje_cambiado`
   - QTimer con qtbot.wait()

5. **test_cliente_bateria.py** - Comunicación TCP
   - Métodos sync/async
   - Mock EphemeralSocketClient completo
   - Formato: "{voltaje:.2f}" (sin newline)

6. **test_servicio_envio.py** - Integración generador-cliente
   - Métodos: `iniciar()`, `detener()`
   - 4 signals: envio_exitoso, envio_fallido, servicio_iniciado, servicio_detenido

### Fase 2: Modelos y Controladores Críticos (Semana 2) - 5 archivos
**Prioridad:** ALTA - 20% del coverage

7. **test_estado_bateria_panel_modelo.py**
   - Contadores, tasa_exito, cálculo porcentaje normalizado

8. **test_control_panel_modelo.py** (CRÍTICO)
   - Conversión bidireccional voltaje ↔ paso slider
   - Tests exhaustivos de precisión

9. **test_conexion_panel_modelo.py**
   - Validación puerto 1-65535
   - Strip() en IP

10. **test_panel_estado_controlador.py**
    - `actualizar_voltaje()`, `actualizar_conexion()`
    - `registrar_envio_exitoso/fallido()`
    - 3 signals

11. **test_factory.py** (CRÍTICO)
    - Creación de 4 componentes
    - Defaults vs overrides

### Fase 3: Controladores y Coordinator (Semana 3) - 3 archivos
**Prioridad:** ALTA

12. **test_control_panel_controlador.py**
    - Callback slider → voltaje
    - Signal voltaje_cambiado

13. **test_conexion_panel_controlador.py**
    - Callbacks botones
    - Signals conectar/desconectar_solicitado

14. **test_coordinator.py** (COMPLEJO)
    - 6 conexiones de signals con lambdas
    - Properties: ip_configurada, puerto_configurado
    - Integración completa

### Fase 4: Vistas y Base (Semana 4) - 4 archivos
**Prioridad:** MEDIA - 5% del coverage

15. **test_paneles_base.py**
    - ModeloBase, VistaBase, ControladorBase
    - Implementaciones concretas in-test

16. **test_estado_bateria_panel_vista.py**
    - UI: labels voltaje/porcentaje/conexión
    - `actualizar()`, `mostrar_sin_datos()`

17. **test_control_panel_vista.py**
    - QSlider + bloqueo signals
    - Signal slider_cambiado

18. **test_conexion_panel_vista.py**
    - Delegate a ConfigPanel (compartido.widgets)
    - Signals botones

## Estructura de Directorios

```
simulador_bateria/tests/
├── __init__.py
├── conftest.py                              # Fixtures globales
├── test_config.py                           # (Fase 1)
├── test_estado_bateria.py
├── test_generador_bateria.py
├── test_cliente_bateria.py
├── test_servicio_envio.py
├── test_estado_bateria_panel_modelo.py      # (Fase 2)
├── test_control_panel_modelo.py
├── test_conexion_panel_modelo.py
├── test_panel_estado_controlador.py
├── test_factory.py
├── test_control_panel_controlador.py        # (Fase 3)
├── test_conexion_panel_controlador.py
├── test_coordinator.py
├── test_paneles_base.py                     # (Fase 4)
├── test_estado_bateria_panel_vista.py
├── test_control_panel_vista.py
└── test_conexion_panel_vista.py
```

## Patrones de Testing a Aplicar

### 1. Fixtures Encadenadas (conftest.py)
```python
@pytest.fixture
def config():
    return ConfigSimuladorBateria(
        host="127.0.0.1",
        puerto=11000,
        intervalo_envio_ms=100,
        voltaje_minimo=10.0,
        voltaje_maximo=15.0,
        voltaje_inicial=12.0
    )

@pytest.fixture
def mock_ephemeral_client():
    with patch('app.comunicacion.cliente_bateria.EphemeralSocketClient') as mock:
        mock_instance = MagicMock()
        mock_instance.send.return_value = True
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def generador(config, qtbot):
    return GeneradorBateria(config)

@pytest.fixture
def mock_cliente(mock_ephemeral_client, qtbot):
    with patch('app.comunicacion.cliente_bateria.EphemeralSocketClient') as mock_class:
        mock_class.return_value = mock_ephemeral_client
        return ClienteBateria("127.0.0.1", 11000)

@pytest.fixture
def servicio(generador, mock_cliente, qtbot):
    return ServicioEnvioBateria(generador, mock_cliente)
```

### 2. Testing de Signals PyQt6
```python
def test_signal_emitido(componente, qtbot):
    with qtbot.waitSignal(componente.signal_name, timeout=1000) as blocker:
        componente.trigger_action()
    assert blocker.args[0] == valor_esperado
```

### 3. Testing de Timers
```python
def test_timer_genera_valores(generador, qtbot):
    signal_spy = []
    generador.valor_generado.connect(lambda x: signal_spy.append(x))

    generador.iniciar()
    qtbot.wait(250)
    generador.detener()

    assert len(signal_spy) >= 2
```

### 4. Agrupación por Clases
```python
class TestComponenteCreacion:
    """Tests de inicialización."""

class TestComponenteMetodos:
    """Tests de métodos públicos."""

class TestComponenteSignals:
    """Tests de señales Qt."""

class TestComponenteIntegracion:
    """Tests de integración."""
```

### 5. Mocking de EphemeralSocketClient
```python
def test_envio_exitoso(cliente, mock_ephemeral_client):
    resultado = cliente.enviar_voltaje(12.5)
    mock_ephemeral_client.send.assert_called_once_with("12.50")
    assert resultado is True
```

## Casos Especiales

### 1. Testing Coordinator con Lambdas
El coordinator conecta signals con lambdas que transforman datos:
```python
self._generador.valor_generado.connect(
    lambda estado: self._ctrl_estado.actualizar_voltaje(estado.voltaje)
)
```

**Test:**
```python
def test_generador_actualiza_estado(coordinator, generador, qtbot):
    signal_spy = []
    coordinator._ctrl_estado.voltaje_actualizado.connect(lambda v: signal_spy.append(v))

    generador.set_voltaje(13.5)
    generador.generar_valor()
    qtbot.wait(50)

    assert signal_spy[0] == 13.5
```

### 2. Testing Conversión Voltaje ↔ Paso Slider
Tests exhaustivos de conversión bidireccional:
```python
def test_conversion_bidireccional(modelo):
    voltaje_original = 13.7
    paso = modelo.voltaje_a_paso(voltaje_original)
    voltaje_recuperado = modelo.paso_a_voltaje(paso)
    assert voltaje_recuperado == pytest.approx(voltaje_original, abs=0.1)
```

### 3. Testing Bloqueo de Signals en Vistas
```python
def test_actualizar_no_emite_signals(qtbot):
    vista = ControlPanelVista()
    qtbot.addWidget(vista)

    signal_spy = []
    vista.slider_cambiado.connect(lambda v: signal_spy.append(v))

    vista.actualizar(modelo)
    assert len(signal_spy) == 0  # No debe emitir durante actualización
```

## Archivos Críticos a Crear Primero

1. `/simulador_bateria/tests/conftest.py` - Base de fixtures globales
2. `/simulador_bateria/tests/__init__.py` - Docstring módulo
3. `/simulador_bateria/tests/test_generador_bateria.py` - Core del simulador (60% lógica)
4. `/simulador_bateria/tests/test_cliente_bateria.py` - Comunicación TCP crítica
5. `/simulador_bateria/tests/test_coordinator.py` - Integración más compleja

## Verificación de Coverage

### Comandos
```bash
cd simulador_bateria
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
open htmlcov/index.html
```

### Metas por Capa
- Dominio: 90-95%
- Comunicación: 85-90%
- Configuración: 90-95%
- Factory/Coordinator: 85-90%
- Modelos MVC: 85-90%
- Controladores MVC: 80-85%
- Vistas MVC: 70-75%

**Target Global:** ≥80%

### Validación Quality Gates
```bash
python quality/scripts/calculate_metrics.py app
python quality/scripts/validate_gates.py quality/reports/quality_*.json
```

## Métricas de Éxito

- ✓ **18 archivos de test** creados
- ✓ **~80-100 test cases** totales
- ✓ **≥80% coverage** en app/
- ✓ **0 fallos** en pytest
- ✓ **Pylint ≥8.0** mantenido
- ✓ **Quality gates** aprobados
