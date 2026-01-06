# Plan de Implementación ST-38

## HU-2.7: Cliente TCP puerto 12000

**Epic:** ST-31 - Simulador de Temperatura
**Estado:** En curso
**Prioridad:** Medium

---

## Descripción

Como desarrollador, quiero tener un cliente TCP que envíe los valores de temperatura al puerto 12000 de la Raspberry Pi para comunicar los datos del simulador.

---

## Criterios de Aceptación

- [x] Clase `ClienteTemperatura` en `app/comunicacion/`
- [x] Hereda/usa `EphemeralSocketClient` de compartido
- [x] Conexión al puerto 12000 (configurable)
- [x] Método `enviar_temperatura(temp: float)` que envía formato `"<temperatura>"`
- [x] Señales Qt: `dato_enviado`, `error_conexion`
- [x] Integración con `GeneradorTemperatura` para envío automático (`ServicioEnvioTemperatura`)
- [x] Logs de comunicación para debugging
- [x] Tests unitarios con mock de socket (27 tests)

---

## Análisis Técnico

### Arquitectura

```
ClienteTemperatura (QObject)
    │
    ├── EphemeralSocketClient (compartido) ✓
    │       └── send(data) → conectar, enviar, cerrar
    │
    ├── EstadoTemperatura (ST-34) ✓
    │       └── Encapsula valor a enviar
    │
    └── ConfigSimuladorTemperatura
            └── ip_raspberry, puerto
```

### Protocolo de comunicación

Según `docs/ESPECIFICACION_COMUNICACIONES.md`:

| Aspecto | Valor |
|---------|-------|
| Puerto | 12000 |
| Dirección | Simulador → ISSE_Termostato |
| Formato | Texto plano UTF-8 |
| Estructura | `<valor_float>` (ej: `23.5`) |
| Patrón | Efímero: conectar → enviar → cerrar |

### Señales Qt

| Señal | Parámetro | Cuándo se emite |
|-------|-----------|-----------------|
| `dato_enviado` | `float` | Cuando el valor se envía exitosamente |
| `error_conexion` | `str` | Cuando ocurre un error de conexión |

### Clase base disponible

`EphemeralSocketClient` en `compartido/networking/` ya implementa:
- Patrón conectar → enviar → cerrar
- Señales: `data_sent`, `error_occurred`
- Métodos: `send()`, `send_async()`

---

## Pasos de Implementación

### Paso 1: Crear la clase ClienteTemperatura

**Archivo:** `simulador_temperatura/app/comunicacion/cliente_temperatura.py`

```python
from PyQt6.QtCore import QObject, pyqtSignal
from compartido.networking import EphemeralSocketClient
from ..dominio.estado_temperatura import EstadoTemperatura

class ClienteTemperatura(QObject):
    dato_enviado = pyqtSignal(float)
    error_conexion = pyqtSignal(str)

    def __init__(self, host: str, port: int, parent=None):
        ...

    def enviar_temperatura(self, temperatura: float) -> bool
    def enviar_temperatura_async(self, temperatura: float) -> None
    def enviar_estado(self, estado: EstadoTemperatura) -> bool
    def enviar_estado_async(self, estado: EstadoTemperatura) -> None

    @property
    def host(self) -> str
    @property
    def port(self) -> int
```

### Paso 2: Actualizar exports del módulo comunicacion

**Archivo:** `simulador_temperatura/app/comunicacion/__init__.py`

- Importar y exportar `ClienteTemperatura`

### Paso 3: Crear clase integradora (opcional)

**Archivo:** `simulador_temperatura/app/comunicacion/servicio_envio.py`

Clase que conecta `GeneradorTemperatura` con `ClienteTemperatura`:

```python
class ServicioEnvioTemperatura(QObject):
    """Integra generador con cliente para envío automático."""

    def __init__(self, generador, cliente, parent=None):
        ...
        generador.valor_generado.connect(self._on_valor_generado)

    def iniciar(self) -> None
    def detener(self) -> None
```

### Paso 4: Crear tests unitarios

**Archivo:** `simulador_temperatura/tests/test_cliente_temperatura.py`

Tests a implementar:

**Creación y configuración:**
1. `test_crear_cliente` - Creación con host y puerto
2. `test_propiedades_host_port` - Verifica getters

**Envío de datos:**
3. `test_enviar_temperatura_formato` - Formato correcto del mensaje
4. `test_enviar_temperatura_exitoso` - Retorna True y emite señal
5. `test_enviar_temperatura_error` - Retorna False y emite error
6. `test_enviar_estado` - Envía desde EstadoTemperatura

**Envío asíncrono:**
7. `test_enviar_temperatura_async` - No bloquea
8. `test_enviar_estado_async` - Desde EstadoTemperatura

**Señales:**
9. `test_signal_dato_enviado` - Emite con temperatura correcta
10. `test_signal_error_conexion` - Emite mensaje de error

**Integración (con mock):**
11. `test_usa_ephemeral_socket_client` - Verifica delegación
12. `test_logging_envio_exitoso` - Log en envío OK
13. `test_logging_error_conexion` - Log en error

### Paso 5: Ejecutar tests y validar calidad

```bash
cd simulador_temperatura
pytest tests/test_cliente_temperatura.py -v
pytest tests/ --cov=app --cov-report=html
python quality/scripts/calculate_metrics.py app
```

---

## Dependencias

| Componente | Archivo | Estado |
|------------|---------|--------|
| `EphemeralSocketClient` | `compartido/networking/` | ✓ Implementado |
| `EstadoTemperatura` | `dominio/estado_temperatura.py` | ✓ Implementado (ST-34) |
| `GeneradorTemperatura` | `dominio/generador_temperatura.py` | ✓ Implementado (ST-37) |
| `ConfigSimuladorTemperatura` | `configuracion/config.py` | ✓ Existente |
| `PyQt6.QtCore` | Externa | ✓ Instalada |

---

## Configuración utilizada

```python
# Desde ConfigSimuladorTemperatura
ip_raspberry: str     # Host del servidor (ej: "127.0.0.1")
puerto: int           # Puerto TCP (12000)
```

```json
// Desde config.json
{
  "raspberry_pi": { "ip": "192.168.1.100" },
  "puertos": { "temperatura": 12000 }
}
```

---

## Notas

- El puerto correcto es **12000** (no 14001 como indica el ticket original)
- Se usa `EphemeralSocketClient` porque el protocolo ISSE_Termostato espera conexiones efímeras
- El formato de envío es `"<float>"` sin newline (ej: `"23.50"`)
- El cliente NO mantiene conexión persistente
- Los logs usan el módulo `logging` estándar de Python
- La integración con `GeneradorTemperatura` puede hacerse:
  - Directamente conectando señales
  - Mediante una clase `ServicioEnvioTemperatura` (más desacoplado)

---

## Verificación Final

- [x] Tests pasan al 100% (72/72 passed)
- [x] Cobertura de código: OK
- [x] Quality gates cumplidos - Calificación: **A**
  - Pylint: 8.55/10 (threshold >= 8.0)
  - Cyclomatic Complexity: 1.45 (threshold <= 10)
  - Maintainability Index: 77.00 (threshold > 20)
