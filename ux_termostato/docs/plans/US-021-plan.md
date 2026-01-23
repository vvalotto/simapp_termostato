# Plan de Implementación - US-021: Capa de Comunicación

**Historia:** Como desarrollador del sistema quiero implementar comunicación TCP bidireccional con el RPi
**Puntos:** 5
**Prioridad:** CRÍTICA
**Estado:** ✅ COMPLETADO (todos los quality gates cumplidos)

---

## Descripción

Implementar la capa de comunicación TCP bidireccional con el Raspberry Pi:
- **ServidorEstado**: Recibe JSON con estado del termostato (puerto 14001)
- **ClienteComandos**: Envía comandos JSON al termostato (puerto 14000)

**Principio:** Esta capa orquesta la comunicación de red - usa clases de `compartido/networking` y el dominio de US-020.

**Dependencias:**
- ✅ US-020 (EstadoTermostato, Comandos)
- ✅ `compartido/networking` (BaseSocketServer, EphemeralSocketClient)

---

## Componentes a Implementar

### 1. ServidorEstado (`comunicacion/servidor_estado.py`)

**Responsabilidades:**
- Hereda de `BaseSocketServer` para manejar conexiones TCP
- Escucha en puerto 14001 (recibe estado del RPi)
- Parsea JSON recibido → `EstadoTermostato`
- Emite señales PyQt para notificar a la UI
- Manejo robusto de errores (JSON malformado, conexión perdida)

**Señales PyQt:**
```python
estado_recibido = pyqtSignal(EstadoTermostato)  # Estado actualizado
conexion_establecida = pyqtSignal(str)          # Cliente conectado (ip:puerto)
conexion_perdida = pyqtSignal(str)              # Cliente desconectado
error_parsing = pyqtSignal(str)                 # Error al parsear JSON
```

**Métodos públicos:**
```python
def __init__(self, host: str = "0.0.0.0", port: int = 14001, parent=None)
def iniciar() -> bool                  # Inicia servidor en thread
def detener() -> None                  # Detiene servidor
def esta_activo() -> bool              # Verifica si está corriendo
```

**Métodos privados:**
```python
def _procesar_mensaje(self, data: str) -> None
    # 1. Parsear JSON
    # 2. Validar estructura
    # 3. Crear EstadoTermostato.from_json()
    # 4. Emitir estado_recibido(estado)
    # 5. Manejo de errores: log + emitir error_parsing
```

**Logging:**
- INFO: Servidor iniciado, cliente conectado/desconectado
- DEBUG: Mensaje JSON recibido
- ERROR: Error de parsing, conexión perdida inesperadamente

---

### 2. ClienteComandos (`comunicacion/cliente_comandos.py`)

**Responsabilidades:**
- Encapsula `EphemeralSocketClient` para envíos efímeros
- Envía comandos JSON al RPi (puerto 14000)
- Fire-and-forget (no espera respuesta)
- Manejo robusto de errores de conexión

**Métodos públicos:**
```python
def __init__(self, host: str, port: int = 14000, parent=None)
def enviar_comando(self, cmd: ComandoTermostato) -> bool
    # 1. Serializar: cmd.to_json()
    # 2. Convertir a JSON string + newline
    # 3. Enviar via EphemeralSocketClient
    # 4. Retornar True si éxito, False si error
    # 5. Nunca lanza excepciones
```

**Propiedades:**
```python
@property
def host(self) -> str

@property
def port(self) -> int
```

**Logging:**
- INFO: Comando enviado exitosamente (tipo de comando)
- ERROR: Error de conexión, timeout

**Patrón de uso:**
```python
cliente = ClienteComandos("192.168.1.50", 14000)
cmd = ComandoPower(estado=True)
exito = cliente.enviar_comando(cmd)
if exito:
    print("Comando enviado")
else:
    print("Error al enviar")
```

---

### 3. Exports (`comunicacion/__init__.py`)

```python
from .servidor_estado import ServidorEstado
from .cliente_comandos import ClienteComandos

__all__ = [
    "ServidorEstado",
    "ClienteComandos",
]
```

---

## Tasks

### Implementación

- [ ] **ServidorEstado** (~2h)
  - Heredar de BaseSocketServer
  - Conectar señal `data_received` de BaseSocketServer
  - Implementar `_procesar_mensaje(data: str)`
  - Parsear JSON → dict
  - Crear EstadoTermostato.from_json()
  - Emitir señales apropiadas
  - Manejo de errores (JSON malformado, campos faltantes)
  - Override de `_handle_new_client` para señal `conexion_establecida`
  - Logging completo (INFO, DEBUG, ERROR)

- [ ] **ClienteComandos** (~1h)
  - Encapsular EphemeralSocketClient
  - Método `enviar_comando(cmd)`
  - Serializar comando: `json.dumps(cmd.to_json()) + "\n"`
  - Enviar via `self._cliente.send()`
  - Manejo de errores (no lanzar excepciones)
  - Logging de envíos exitosos y errores
  - Propiedades `host` y `port`

- [ ] **__init__.py** (~5min)
  - Exports públicos

### Tests Unitarios

- [ ] **test_servidor_estado.py** (~2h) **~15 tests**
  - `TestCreacion`: inicialización correcta (2 tests)
  - `TestRecepcionJSON`: parseo de JSON válido (3 tests)
  - `TestErroresJSON`: JSON malformado, campos faltantes (4 tests)
  - `TestSignals`: emisión correcta de señales PyQt (3 tests)
  - `TestConexion`: conexión establecida/perdida (3 tests)
  - Mock de sockets para simular conexión del RPi
  - Verificar que emite `estado_recibido` con objeto correcto
  - Verificar que no crashea con JSON inválido

- [ ] **test_cliente_comandos.py** (~1.5h) **~12 tests**
  - `TestCreacion`: inicialización, propiedades (2 tests)
  - `TestEnvioComandos`: envío de cada tipo de comando (3 tests)
  - `TestSerializacion`: JSON generado es correcto (3 tests)
  - `TestErrores`: timeout, conexión rechazada (2 tests)
  - `TestNoExcepciones`: captura todas las excepciones (2 tests)
  - Mock de `EphemeralSocketClient`
  - Verificar formato JSON enviado

### Tests de Integración (Opcional)

- [ ] **test_comunicacion_integracion.py** (~1h) **~3 tests**
  - Servidor recibe → Cliente envía (loopback)
  - Flujo completo: enviar comando → recibir estado actualizado
  - Test con mock de RPi (envía JSON periódicamente)

---

## Quality Gates

- **Coverage:** ≥ 95%
- **Pylint:** ≥ 8.0
- **Complejidad:** CC ≤ 10
- **Type hints:** 100%

---

## Estimación

**Total:** ~8 horas
- Implementación: 3h
- Tests: 5h

---

## Notas de Implementación

### Protocolo JSON del RPi (Entrada - Puerto 14001)

**Estado del termostato (recibido cada ~1 segundo):**
```json
{
  "temperatura_actual": 22.5,
  "temperatura_deseada": 24.0,
  "modo_climatizador": "calentando",
  "falla_sensor": false,
  "bateria_baja": false,
  "encendido": true,
  "modo_display": "ambiente",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

**Formato esperado:** JSON terminado en `\n`

---

### Protocolo JSON al RPi (Salida - Puerto 14000)

**ComandoPower:**
```json
{
  "comando": "power",
  "estado": "on",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

**ComandoSetTemp:**
```json
{
  "comando": "set_temp_deseada",
  "valor": 24.5,
  "timestamp": "2026-01-23T10:30:00Z"
}
```

**ComandoSetModoDisplay:**
```json
{
  "comando": "set_modo_display",
  "modo": "deseada",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

**Formato:** JSON terminado en `\n`

---

### Implementación de ServidorEstado

**Estructura básica:**
```python
import json
import logging
from typing import Optional
from PyQt6.QtCore import pyqtSignal

from compartido.networking import BaseSocketServer
from ..dominio import EstadoTermostato

logger = logging.getLogger(__name__)


class ServidorEstado(BaseSocketServer):
    """Servidor TCP que recibe estado del termostato desde el RPi."""

    estado_recibido = pyqtSignal(EstadoTermostato)
    conexion_establecida = pyqtSignal(str)
    conexion_perdida = pyqtSignal(str)
    error_parsing = pyqtSignal(str)

    def __init__(self, host: str = "0.0.0.0", port: int = 14001, parent=None):
        super().__init__(host, port, parent)

        # Conectar señales de BaseSocketServer
        self.data_received.connect(self._procesar_mensaje)
        self.client_connected.connect(self._on_cliente_conectado)
        self.client_disconnected.connect(self._on_cliente_desconectado)

    def iniciar(self) -> bool:
        """Inicia el servidor."""
        return self.start()

    def detener(self) -> None:
        """Detiene el servidor."""
        self.stop()

    def esta_activo(self) -> bool:
        """Verifica si el servidor está activo."""
        return self.is_running()

    def _procesar_mensaje(self, data: str) -> None:
        """Procesa mensaje JSON recibido del RPi."""
        try:
            # 1. Parsear JSON
            datos = json.loads(data.strip())

            # 2. Crear EstadoTermostato
            estado = EstadoTermostato.from_json(datos)

            # 3. Emitir señal
            logger.debug("Estado recibido: %s", estado.to_dict())
            self.estado_recibido.emit(estado)

        except json.JSONDecodeError as e:
            msg = f"JSON malformado: {e}"
            logger.error(msg)
            self.error_parsing.emit(msg)

        except (KeyError, ValueError) as e:
            msg = f"Error al crear EstadoTermostato: {e}"
            logger.error(msg)
            self.error_parsing.emit(msg)

    def _on_cliente_conectado(self, direccion: str) -> None:
        """Maneja conexión de cliente."""
        logger.info("Cliente RPi conectado: %s", direccion)
        self.conexion_establecida.emit(direccion)

    def _on_cliente_desconectado(self, direccion: str) -> None:
        """Maneja desconexión de cliente."""
        logger.info("Cliente RPi desconectado: %s", direccion)
        self.conexion_perdida.emit(direccion)
```

---

### Implementación de ClienteComandos

**Estructura básica:**
```python
import json
import logging
from typing import Optional

from PyQt6.QtCore import QObject

from compartido.networking import EphemeralSocketClient
from ..dominio import ComandoTermostato

logger = logging.getLogger(__name__)


class ClienteComandos(QObject):
    """Cliente TCP para enviar comandos al termostato en el RPi."""

    def __init__(
        self,
        host: str,
        port: int = 14000,
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self._host = host
        self._port = port
        self._cliente = EphemeralSocketClient(host, port, self)

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    def enviar_comando(self, cmd: ComandoTermostato) -> bool:
        """Envía comando al RPi. Retorna True si éxito, False si error."""
        try:
            # 1. Serializar comando
            datos_json = cmd.to_json()
            mensaje = json.dumps(datos_json) + "\n"

            # 2. Enviar via cliente efímero
            exito = self._cliente.send(mensaje)

            if exito:
                logger.info(
                    "Comando enviado: %s -> %s:%d",
                    datos_json.get("comando"),
                    self._host,
                    self._port
                )
            else:
                logger.error("Error al enviar comando a %s:%d", self._host, self._port)

            return exito

        except Exception as e:
            logger.error("Excepción al enviar comando: %s", e)
            return False
```

---

## Checklist de Progreso

### Implementación
- [x] servidor_estado.py ✅ (207 líneas)
- [x] cliente_comandos.py ✅ (135 líneas)
- [x] __init__.py ✅

### Tests
- [x] test_servidor_estado.py ✅ (18 tests, 269 líneas)
- [x] test_cliente_comandos.py ✅ (17 tests, 259 líneas)
- [ ] test_comunicacion_integracion.py (opcional - no implementado)

### Quality
- [x] Coverage = 95% ✅ (97/102 statements)
- [x] Pylint = 10.00/10 ✅
- [x] CC Promedio = 1.85 ✅ (objetivo: ≤10)
- [x] MI Promedio = 96.00 ✅ (objetivo: >20)
- [x] Tests pasan (34/34 ✅)

---

## Arquitectura de Referencia

**Simuladores (temperatura/bateria):**
- `ClienteTemperatura` / `ClienteBateria`: envían datos al RPi
- Usan `EphemeralSocketClient` (patrón efímero)
- Logging apropiado (INFO, ERROR)
- No lanzan excepciones al usuario

**UX Termostato (esta US):**
- `ServidorEstado`: recibe datos del RPi (puerto 14001)
- `ClienteComandos`: envía comandos al RPi (puerto 14000)
- Comunicación bidireccional (servidor + cliente)

---

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│                    Desktop (ux_termostato)              │
│                                                          │
│  ┌────────────────┐                  ┌────────────────┐ │
│  │ ServidorEstado │◄────14001────────┤  Raspberry Pi  │ │
│  │  (escucha)     │                  │   (envía       │ │
│  │                │                  │    estado)     │ │
│  └───────┬────────┘                  └────────▲───────┘ │
│          │                                    │         │
│          │ estado_recibido(EstadoTermostato) │         │
│          ▼                                    │         │
│  ┌────────────────┐                  ┌────────┴───────┐ │
│  │   Paneles UI   │                  │ ClienteComandos│ │
│  │  (display,     │                  │   (envía)      │ │
│  │   control,     │                  │                │ │
│  │   power...)    │──────14000───────►                │ │
│  └────────────────┘   enviar_comando()└────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Resultados Finales

### ✅ Implementación Completada

**Archivos creados:**
- `app/comunicacion/servidor_estado.py` (207 líneas)
- `app/comunicacion/cliente_comandos.py` (135 líneas)
- `app/comunicacion/__init__.py` (14 líneas)
- `tests/test_servidor_estado.py` (269 líneas, 18 tests)
- `tests/test_cliente_comandos.py` (259 líneas, 17 tests)

**Métricas de Calidad:**
- **Tests:** 34/34 ✅ (18 + 17)
- **Coverage:** 95% (97/102 statements) ✅
- **Pylint:** 10.00/10 ✅
- **CC Promedio:** 1.85 ✅ (objetivo: ≤10)
- **MI Promedio:** 96.00 ✅ (objetivo: >20)

**Detalle por Archivo:**

| Archivo | Coverage | Pylint | CC Max | MI | Calificación |
|---------|----------|--------|--------|----|--------------|
| servidor_estado.py | 92% | 10/10 | 5 (A) | 100.00 (A) | ✅ A |
| cliente_comandos.py | 100% | 10/10 | 3 (A) | 88.01 (A) | ✅ A |
| __init__.py | 100% | 10/10 | - | 100.00 (A) | ✅ A |

**Estadísticas de Código:**
- **Código:** 356 líneas
- **Tests:** 528 líneas
- **Ratio tests/código:** 1.48:1

**Quality Gates:**
- ✅ Coverage ≥ 95% (obtuvo 95%)
- ✅ Pylint ≥ 8.0 (obtuvo 10.00/10)
- ✅ CC ≤ 10 (obtuvo 1.85 promedio)
- ✅ MI > 20 (obtuvo 96.00 promedio)
- ✅ Tests pasan (34/34)

**🎉 TODOS LOS QUALITY GATES CUMPLIDOS**

**Componentes Implementados:**

1. **ServidorEstado:**
   - Hereda de BaseSocketServer
   - Recibe JSON del RPi (puerto 14001)
   - Parsea JSON → EstadoTermostato
   - Emite señales PyQt (estado_recibido, conexion_establecida, etc.)
   - Manejo robusto de errores (JSON malformado, campos faltantes)
   - Logging completo (DEBUG, INFO, ERROR)

2. **ClienteComandos:**
   - Encapsula EphemeralSocketClient
   - Envía comandos JSON al RPi (puerto 14000)
   - Fire-and-forget (no espera respuesta)
   - Serialización automática (comando.to_json() → JSON + newline)
   - Manejo de errores (no lanza excepciones)
   - Logging apropiado

---

## Próximos Pasos

Una vez completado US-021:
- ✅ Tendremos comunicación bidireccional con RPi
- ➡️ US-022: Factory + Coordinator (usa ServidorEstado y ClienteComandos)
- ➡️ Paneles podrán recibir estado real del RPi
- ➡️ Paneles podrán enviar comandos al RPi
