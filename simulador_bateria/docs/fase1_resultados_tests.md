# Resultados Tests Fase 1 - Simulador Batería

## Resumen Ejecutivo

**Tests ejecutados:** 84
**Tests pasados:** 73 (86.9%)
**Tests fallidos:** 11 (13.1%)

### Coverage Fase 1 (Componentes Testeados)

| Componente | Coverage | Estado |
|------------|----------|--------|
| config.py | 100% | ✅ |
| constantes.py | 100% | ✅ |
| estado_bateria.py | 100% | ✅ |
| generador_bateria.py | 100% | ✅ |
| cliente_bateria.py | 89% | ⚠️ Missing: error callbacks |
| servicio_envio.py | 96% | ✅ Missing: error callbacks |
| **Promedio Fase 1** | **97.5%** | ✅ |

**Coverage Global:** 33% (240/725 statements)
- La baja cobertura global es esperada: solo Fase 1 (6 archivos) está testeada
- Fase 2-4 (12 archivos restantes) pendientes: factory, coordinator, presentación MVC
- Coverage objetivo ≥80% se alcanzará al completar las 4 fases

## Análisis de Fallas

### 1. Error Handling en ClienteBateria (2 fallas)

**Archivos afectados:**
- `app/comunicacion/cliente_bateria.py:90` (enviar_voltaje)
- `app/comunicacion/cliente_bateria.py:105` (enviar_voltaje_async)

**Problema:** Los métodos no capturan excepciones lanzadas por EphemeralSocketClient.

**Tests fallidos:**
- `test_cliente_bateria.py::TestClienteBateriaErrorHandling::test_envio_con_excepcion_retorna_false`
- `test_cliente_bateria.py::TestClienteBateriaErrorHandling::test_envio_async_con_excepcion_no_falla`

**Fix requerido:**
```python
def enviar_voltaje(self, voltaje: float) -> bool:
    try:
        self._ultimo_valor = voltaje
        mensaje = f"{voltaje:.2f}"
        logger.debug("Enviando voltaje: %s", mensaje)
        return self._cliente.send(mensaje)
    except Exception as e:
        logger.error("Error al enviar voltaje: %s", str(e))
        self.error_conexion.emit(str(e))
        return False

def enviar_voltaje_async(self, voltaje: float) -> None:
    try:
        self._ultimo_valor = voltaje
        mensaje = f"{voltaje:.2f}"
        logger.debug("Enviando voltaje (async): %s", mensaje)
        self._cliente.send_async(mensaje)
    except Exception as e:
        logger.error("Error al enviar voltaje async: %s", str(e))
        self.error_conexion.emit(str(e))
```

### 2. Error Handling en ServicioEnvioBateria (1 falla)

**Archivo afectado:**
- `app/comunicacion/servicio_envio.py:111` (_on_valor_generado)

**Problema:** Excepciones en el slot _on_valor_generado propagan por el Qt event loop.

**Test fallido:**
- `test_servicio_envio.py::TestServicioEnvioBateriaErrorHandling::test_error_en_envio_no_detiene_servicio`

**Fix requerido:**
```python
def _on_valor_generado(self, estado: EstadoBateria) -> None:
    """Callback cuando el generador produce un nuevo valor."""
    try:
        self._cliente.enviar_estado_async(estado)
    except Exception as e:
        logger.error("Error al procesar valor generado: %s", str(e))
        self.envio_fallido.emit(str(e))
```

### 3. Clamping de Voltaje en GeneradorBateria (3 fallas)

**Archivo afectado:**
- `app/dominio/generador_bateria.py:47` (set_voltaje)

**Problema:** El método set_voltaje() no limita valores a rango min/max.

**Tests fallidos:**
- `test_generador_bateria.py::TestGeneradorBateriaSetVoltaje::test_set_voltaje_clampea_a_minimo`
- `test_generador_bateria.py::TestGeneradorBateriaSetVoltaje::test_set_voltaje_clampea_a_maximo`
- `test_generador_bateria.py::TestGeneradorBateriaGenerarValor::test_generar_valor_fuera_de_rango`

**Comportamiento actual:** Acepta cualquier valor sin restricción.
**Comportamiento esperado:** Limitar voltaje entre config.voltaje_minimo y config.voltaje_maximo.

**Fix requerido:**
```python
def set_voltaje(self, voltaje: float) -> None:
    """Establece el voltaje actual.

    El voltaje se clampea al rango [voltaje_minimo, voltaje_maximo].

    Args:
        voltaje: Voltaje a establecer (V).
    """
    voltaje_clamped = max(
        self._config.voltaje_minimo,
        min(voltaje, self._config.voltaje_maximo)
    )
    self._voltaje_actual = voltaje_clamped
    self.voltaje_cambiado.emit(voltaje_clamped)
```

### 4. Mocking de Config en Tests (3 fallas)

**Archivo afectado:**
- `tests/test_config.py`

**Problema:** Tests encuentran config.json real en lugar de usar valores mockeados.

**Tests fallidos:**
- `test_config.py::TestConfigSimuladorBateriaCreacion::test_desde_defaults`
- `test_config.py::TestConfigManagerCargar::test_cargar_usa_defaults_si_no_existe_archivo`
- `test_config.py::TestConfigManagerCargar::test_cargar_lee_archivo_json`

**Valores esperados vs obtenidos:**
- Esperado: `host = "localhost"`
- Obtenido: `host = "192.168.1.100"` (de config.json real)

**Fix requerido en tests:**
Mejorar el mocking para evitar que ConfigManager._buscar_config_json() encuentre el archivo real:

```python
def test_cargar_usa_defaults_si_no_existe_archivo(self):
    manager = ConfigManager.obtener_instancia()

    with patch.object(manager, '_buscar_config_json', return_value=None):
        config = manager.cargar()

    assert config.host == "localhost"
    assert config.puerto == 11000
```

### 5. Mocking de datetime.now() (1 falla)

**Archivo afectado:**
- `tests/test_estado_bateria.py:40`

**Problema:** El mock de datetime.now() no intercepta correctamente la llamada.

**Test fallido:**
- `test_estado_bateria.py::TestEstadoBateriaCreacion::test_timestamp_usa_datetime_now`

**Fix requerido:**
Ajustar el path del mock para que coincida con la ubicación real:

```python
def test_timestamp_usa_datetime_now(self):
    fecha_fija = datetime(2026, 1, 13, 15, 45, 30)

    # Mock en el módulo donde se importa datetime, no donde se define
    with patch('app.dominio.estado_bateria.datetime') as mock_dt:
        mock_dt.now.return_value = fecha_fija
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        estado = EstadoBateria(voltaje=12.0)

    assert estado.timestamp == fecha_fija
```

### 6. Signal Emission en Test (1 falla)

**Archivo afectado:**
- `tests/test_servicio_envio.py:119`

**Problema:** Test espera que señal envio_exitoso se emita pero signal_spy está vacío.

**Test fallido:**
- `test_servicio_envio.py::TestServicioEnvioBateriaSignalEnvioExitoso::test_generador_dispara_envio_exitoso`

**Análisis:** El flujo es:
1. GeneradorBateria → valor_generado(EstadoBateria)
2. ServicioEnvioBateria._on_valor_generado() → ClienteBateria.enviar_estado_async()
3. ClienteBateria._on_data_sent() → dato_enviado(voltaje)
4. ServicioEnvioBateria._on_dato_enviado() → envio_exitoso(voltaje)

El test configuró `mock_ephemeral_client.send_async.return_value = None` pero no configuró que emita el signal `data_sent`.

**Fix requerido en test:**
```python
def test_generador_dispara_envio_exitoso(self, servicio, mock_ephemeral_client, qtbot):
    """Valor generado dispara envio_exitoso."""
    # Configurar mock para emitir data_sent cuando se llama send_async
    def emit_data_sent(data):
        servicio.cliente._cliente.data_sent.emit()

    mock_ephemeral_client.send_async.side_effect = emit_data_sent

    signal_spy = []
    servicio.envio_exitoso.connect(lambda v: signal_spy.append(v))

    servicio.iniciar()
    qtbot.wait(250)
    servicio.detener()

    assert len(signal_spy) >= 1
```

## Priorización de Fixes

### Alta Prioridad (Código Producción)
1. ✅ Error handling en ClienteBateria
2. ✅ Error handling en ServicioEnvioBateria
3. ⚠️ Voltage clamping en GeneradorBateria (decisión de diseño)

### Media Prioridad (Tests)
4. Config mocking
5. datetime mocking
6. Signal emission test

## Decisión sobre Voltage Clamping

El clamping de voltaje NO estaba en los requerimientos originales. Opciones:

**Opción A:** Implementar clamping (más robusto)
- Pro: Previene valores inválidos en UI
- Pro: Consistente con validación de rango
- Con: Cambia comportamiento esperado

**Opción B:** Ajustar tests para no esperar clamping
- Pro: Mantiene diseño actual
- Pro: UI (slider) ya limita el rango
- Con: Permite valores inválidos si se setea programáticamente

**Recomendación:** Opción A - El clamping agrega robustez y es consistente con el concepto de "rango válido" que ya existe en el dominio.

## Próximos Pasos

1. Decidir sobre voltage clamping (A vs B)
2. Implementar fixes de alta prioridad en código producción
3. Corregir mocking en tests
4. Re-ejecutar suite completa
5. Verificar coverage ≥80%
6. Proceder con Fase 2 si todo pasa
