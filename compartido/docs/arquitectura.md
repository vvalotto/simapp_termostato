# Arquitectura del Módulo Compartido

## Visión General

El módulo **compartido** proporciona **infraestructura crítica reutilizable** para los 3 productos del proyecto simapp_termostato. Implementa abstracciones de red TCP, componentes UI personalizados y gestión de temas, siguiendo principios SOLID y patrones de diseño para maximizar cohesión, minimizar acoplamiento y facilitar la extensibilidad.

**Principio arquitectónico:** Código reutilizable, bajo acoplamiento, alta testabilidad.

```mermaid
graph TB
    subgraph compartido["Módulo Compartido"]
        networking["networking/<br/>Abstracciones TCP"]
        widgets["widgets/<br/>Componentes UI"]
        estilos["estilos/<br/>Temas visuales"]
        quality["quality/<br/>Scripts calidad"]
    end

    subgraph productos["Productos"]
        temp["simulador_temperatura"]
        bat["simulador_bateria"]
        ux["ux_termostato"]
    end

    networking --> temp
    networking --> bat
    networking --> ux

    widgets --> temp
    widgets --> bat
    widgets --> ux

    estilos --> temp
    estilos --> bat
    estilos --> ux

    quality --> temp
    quality --> bat
    quality --> ux

    style compartido fill:#2B5B84,stroke:#4A90E2,stroke-width:3px
    style productos fill:#4A5568,stroke:#718096,stroke-width:2px
```

---

## Estructura de Módulos

```
compartido/
├── networking/                        # Abstracciones TCP
│   ├── socket_client_base.py         # Clase base clientes
│   ├── ephemeral_socket_client.py    # Cliente efímero (fire-and-forget)
│   ├── persistent_socket_client.py   # Cliente persistente (long-lived)
│   ├── base_socket_server.py         # Servidor TCP con threading
│   └── client_session.py             # Gestión de sesión individual
│
├── widgets/                           # Componentes UI reutilizables
│   ├── config_panel.py                # Panel configuración IP/puerto
│   ├── led_indicator.py               # Indicador LED personalizado
│   ├── log_viewer.py                  # Visor de logs con colores
│   ├── status_indicator.py            # Indicador de estado (Protocol)
│   ├── validation_feedback.py         # Feedback visual de validación
│   ├── ip_validator.py                # Validación de IPs
│   ├── led_color_provider.py          # Provider colores LED
│   ├── log_color_provider.py          # Provider colores logs
│   └── log_formatter.py               # Formateador de logs
│
├── estilos/                           # Temas y estilos QSS
│   ├── theme_provider.py              # Protocol para providers
│   ├── file_theme_provider.py         # Carga tema desde archivo
│   ├── generated_theme_provider.py    # Genera tema dinámico
│   ├── qss_generator.py               # Generador QSS programático
│   ├── theme_colors.py                # Paleta de colores
│   └── theme_loader.py                # Cargador de temas
│
├── quality/                           # Scripts de calidad
│   └── scripts/
│       ├── calculate_metrics.py       # Calcula CC/MI con radon
│       ├── validate_gates.py          # Valida métricas vs umbrales
│       └── generate_report.py         # Genera reportes
│
├── tests/                             # Tests unitarios (89.5% coverage)
└── docs/                              # Documentación
    ├── arquitectura.md                # Este documento
    ├── guia_uso.md                    # Guía de uso
    └── informes/
        └── informe_diseno.md          # Análisis SOLID/patrones
```

---

## Responsabilidades por Módulo

```mermaid
graph LR
    subgraph networking["networking/"]
        direction TB
        A1["SocketClientBase<br/>Clase base común"]
        A2["EphemeralSocketClient<br/>Conexión efímera"]
        A3["PersistentSocketClient<br/>Conexión persistente"]
        A4["BaseSocketServer<br/>Servidor TCP"]
        A5["ClientSession<br/>Sesión individual"]
    end

    subgraph widgets["widgets/"]
        direction TB
        B1["ConfigPanel<br/>Config IP/puerto"]
        B2["LEDIndicator<br/>LED visual"]
        B3["LogViewer<br/>Logs con colores"]
        B4["Validators & Providers<br/>Strategies"]
    end

    subgraph estilos["estilos/"]
        direction TB
        C1["ThemeProvider<br/>Protocol"]
        C2["FileThemeProvider<br/>Desde archivo"]
        C3["GeneratedThemeProvider<br/>Dinámico"]
        C4["ThemeColors<br/>Paleta"]
    end

    subgraph quality["quality/"]
        direction TB
        D1["calculate_metrics<br/>CC/MI"]
        D2["validate_gates<br/>Umbrales"]
        D3["generate_report<br/>Reportes"]
    end

    style networking fill:#E8F4F8,stroke:#4A90E2
    style widgets fill:#F0F4F8,stroke:#6B7280
    style estilos fill:#FEF3E2,stroke:#F59E0B
    style quality fill:#E5E7EB,stroke:#9CA3AF
```

### networking/

**Responsabilidad:** Abstracciones para comunicación TCP cliente-servidor

- **SocketClientBase**: Clase base con configuración común (host, port, timeout, encoding)
- **EphemeralSocketClient**: Patrón "conectar→enviar→cerrar" para simuladores
- **PersistentSocketClient**: Conexión de larga duración para UX termostato
- **BaseSocketServer**: Servidor TCP con threading, acepta múltiples clientes
- **ClientSession**: Gestiona ciclo de vida de una sesión individual

**Usado por:**
- simulador_temperatura: EphemeralSocketClient (puerto 12000)
- simulador_bateria: EphemeralSocketClient (puerto 11000)
- ux_termostato: PersistentSocketClient (puertos 13000, 14000, 14001)

### widgets/

**Responsabilidad:** Componentes UI reutilizables con bajo acoplamiento

- **ConfigPanel**: Panel de configuración IP/puerto con validación en tiempo real
- **LEDIndicator**: Indicador LED personalizado con colores configurables
- **LogViewer**: Visor de logs con auto-scroll y límite de líneas
- **Providers**: Abstracciones (Strategy Pattern) para colores, validación, feedback

**Usado por:** Los 3 productos (ConfigPanel en todos, LEDIndicator en bateria/ux, LogViewer según necesidad)

### estilos/

**Responsabilidad:** Gestión de temas visuales QSS

- **ThemeProvider (Protocol)**: Interfaz para proveedores de tema
- **FileThemeProvider**: Carga tema desde archivo `.qss`
- **GeneratedThemeProvider**: Genera tema dinámicamente con `QSSGenerator`
- **ThemeColors**: Paleta de colores del tema oscuro (dataclass inmutable)

**Usado por:** Los 3 productos cargan `dark_theme.qss` mediante `FileThemeProvider`

### quality/

**Responsabilidad:** Scripts de métricas y validación de calidad

- **calculate_metrics.py**: Usa radon para calcular CC (Complejidad Ciclomática) y MI (Índice de Mantenibilidad)
- **validate_gates.py**: Valida métricas contra umbrales (CC ≤ 10, MI > 20, Pylint ≥ 8.0)
- **generate_report.py**: Genera reportes JSON de calidad

**Usado por:** Los 3 productos copian estos scripts a sus directorios `quality/scripts/`

---

## Dependencias

```mermaid
graph TD
    subgraph Capa_Externa["Dependencias Externas"]
        PyQt6["PyQt6<br/>Qt framework"]
        Python["Python stdlib<br/>socket, threading, dataclasses"]
        Radon["radon<br/>Métricas CC/MI"]
    end

    subgraph Compartido["Módulo Compartido"]
        estilos["estilos/<br/>Sin deps internas"]
        widgets["widgets/"]
        networking["networking/<br/>Sin deps internas"]
        quality["quality/"]
    end

    PyQt6 --> widgets
    PyQt6 --> networking
    Python --> widgets
    Python --> networking
    Python --> estilos

    estilos --> widgets

    Radon --> quality
    Python --> quality

    style Capa_Externa fill:#FEE2E2,stroke:#DC2626
    style Compartido fill:#E8F4F8,stroke:#4A90E2
```

### Dependencias entre Módulos Internos

```mermaid
graph BT
    estilos["estilos/"]
    widgets["widgets/"]
    networking["networking/"]
    quality["quality/"]

    widgets -->|usa ThemeProvider| estilos

    style estilos fill:#FEF3E2,stroke:#F59E0B
    style widgets fill:#F0F4F8,stroke:#6B7280
    style networking fill:#E8F4F8,stroke:#4A90E2
    style quality fill:#E5E7EB,stroke:#9CA3AF
```

**Nota:** No hay dependencias circulares. `networking/` y `quality/` son completamente independientes.

### Dependencias Externas

| Módulo | Dependencias | Propósito |
|--------|--------------|-----------|
| **networking/** | PyQt6.QtCore, socket, threading | Señales Qt, TCP, concurrencia |
| **widgets/** | PyQt6.QtWidgets, PyQt6.QtCore, PyQt6.QtGui | Componentes UI, señales, rendering |
| **estilos/** | Python stdlib (dataclasses, pathlib) | Sin dependencias externas pesadas |
| **quality/** | radon, json, pathlib | Cálculo de métricas, serialización |

---

## Patrones de Diseño

### 1. Strategy Pattern (Providers)

**Uso:** `LEDColorProvider`, `LogColorProvider`, `LogFormatter`, `IPValidator`

**Propósito:** Permitir cambiar comportamiento sin modificar widgets (OCP).

```mermaid
classDiagram
    class LEDIndicator {
        -color_provider: LEDColorProvider
        +paintEvent()
    }

    class LEDColorProvider {
        <<Protocol>>
        +get_color_on() str
        +get_color_off() str
    }

    class DefaultLEDColorProvider {
        +get_color_on() str
        +get_color_off() str
    }

    class CustomLEDColorProvider {
        +get_color_on() str
        +get_color_off() str
    }

    LEDIndicator --> LEDColorProvider
    LEDColorProvider <|.. DefaultLEDColorProvider
    LEDColorProvider <|.. CustomLEDColorProvider
```

**Beneficios:**
- OCP cumplido: agregar nuevos providers sin modificar `LEDIndicator`
- DIP cumplido: `LEDIndicator` depende del protocol, no de implementación concreta
- Testabilidad: fácil inyectar providers mock

**Ejemplo de uso:**
```python
# Default
led = LEDIndicator()  # Usa DefaultLEDColorProvider

# Custom
led = LEDIndicator(color_provider=CustomLEDColorProvider())
```

---

### 2. Template Method Pattern

**Uso:** `SocketClientBase`, `BaseSocketServer`

**Propósito:** Definir esqueleto de algoritmo, permitir sobrescritura de pasos.

```mermaid
classDiagram
    class SocketClientBase {
        <<abstract>>
        -_host: str
        -_port: int
        +_create_socket() socket
        +_handle_connection_error(error)
    }

    class EphemeralSocketClient {
        +send(data) bool
        +send_async(data)
    }

    class PersistentSocketClient {
        +connect()
        +disconnect()
        +send(data)
        +receive_loop()
    }

    SocketClientBase <|-- EphemeralSocketClient
    SocketClientBase <|-- PersistentSocketClient
```

**Método template:**
```python
class SocketClientBase:
    def _create_socket(self) -> socket.socket:
        # Template method - puede ser sobrescrito
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.DEFAULT_TIMEOUT)
        return sock
```

**Beneficios:**
- Reutilización de código común (timeout, encoding, error handling)
- Personalización controlada en subclases

---

### 3. Observer Pattern (Señales PyQt)

**Uso:** Todos los componentes de networking y widgets

**Propósito:** Notificación de eventos sin acoplamiento.

```mermaid
sequenceDiagram
    participant Client as EphemeralSocketClient
    participant Observer1 as ServicioEnvio
    participant Observer2 as ControladorEstado

    Client->>Client: send("4.20")
    Client->>Observer1: emit data_sent()
    Client->>Observer2: emit data_sent()

    Note over Observer1,Observer2: Múltiples observadores<br/>sin acoplamiento
```

**Señales específicas por componente:**

| Componente | Señales | Propósito |
|------------|---------|-----------|
| `EphemeralSocketClient` | `data_sent()`, `error_occurred(str)` | Envío efímero |
| `PersistentSocketClient` | `connected()`, `disconnected()`, `data_received(str)`, `error_occurred(str)` | Conexión persistente |
| `ConfigPanel` | `connect_requested()`, `disconnect_requested()`, `config_changed()` | Eventos UI |
| `LEDIndicator` | `state_changed(bool)` | Cambio de estado |

**Beneficios:**
- Desacoplamiento: observadores no conocen al emisor
- Múltiples observadores por señal
- Comunicación asíncrona

---

### 4. Composition Pattern

**Uso:** Todos los widgets

**Propósito:** "Composition over inheritance" - evitar jerarquías complejas.

```mermaid
classDiagram
    class ConfigPanel {
        -_status_indicator: StatusIndicator
        -_ip_validator: IPValidator
        -_validation_feedback: ValidationFeedbackProvider
        -_ip_input: QLineEdit
        -_port_input: QSpinBox
    }

    class StatusIndicator {
        <<Protocol>>
    }

    class IPValidator {
        <<Protocol>>
    }

    class ValidationFeedbackProvider {
        <<Protocol>>
    }

    ConfigPanel *-- StatusIndicator
    ConfigPanel *-- IPValidator
    ConfigPanel *-- ValidationFeedbackProvider
```

**Ejemplo:**
```python
class ConfigPanel(QWidget):
    def __init__(self,
                 status_indicator: StatusIndicator | None = None,
                 ip_validator: IPValidator | None = None):
        # Composición: inyectar dependencias
        self._status_indicator = status_indicator or LEDStatusIndicator()
        self._ip_validator = ip_validator or DefaultIPValidator()
```

**Beneficios:**
- Flexibilidad: cambiar componentes en runtime
- Sin herencia múltiple
- Fácil testing (inyectar mocks)

---

### 5. Singleton Pattern (ThemeProvider)

**Uso:** Gestión de tema global

**Propósito:** Un solo proveedor de tema para toda la aplicación.

```mermaid
classDiagram
    class ThemeProvider {
        <<Protocol>>
        +get_stylesheet() str
    }

    class FileThemeProvider {
        -_stylesheet_path: Path
        -_cached_stylesheet: str
        +get_stylesheet() str
    }

    class GeneratedThemeProvider {
        -_generator: QSSGenerator
        +get_stylesheet() str
    }

    ThemeProvider <|.. FileThemeProvider
    ThemeProvider <|.. GeneratedThemeProvider

    note for FileThemeProvider "Usado en producción<br/>Carga dark_theme.qss"
    note for GeneratedThemeProvider "Para temas dinámicos<br/>Genera QSS con QSSGenerator"
```

**Uso típico:**
```python
# Una instancia global por aplicación
theme_provider = FileThemeProvider("compartido/estilos/dark_theme.qss")
app.setStyleSheet(theme_provider.get_stylesheet())
```

**Beneficios:**
- Tema consistente en toda la app
- Fácil cambiar entre FileThemeProvider y GeneratedThemeProvider
- DIP cumplido (depender del protocol)

---

### 6. Provider Pattern (DIP)

**Uso:** `LEDColorProvider`, `LogColorProvider`, `ThemeProvider`, `IPValidator`

**Propósito:** Inversión de dependencias mediante protocols.

```mermaid
graph TB
    subgraph "Alto Nivel"
        ConfigPanel["ConfigPanel<br/>(widget de alto nivel)"]
    end

    subgraph "Abstracción"
        IPValidator["IPValidator<br/>(Protocol)"]
    end

    subgraph "Bajo Nivel"
        DefaultIPValidator["DefaultIPValidator<br/>(implementación)"]
        CustomIPValidator["CustomIPValidator<br/>(implementación)"]
    end

    ConfigPanel -->|depende de| IPValidator
    DefaultIPValidator -.->|implementa| IPValidator
    CustomIPValidator -.->|implementa| IPValidator

    style ConfigPanel fill:#E8F4F8
    style IPValidator fill:#FEF3E2
    style DefaultIPValidator fill:#F0F4F8
    style CustomIPValidator fill:#F0F4F8
```

**Ejemplo DIP:**
```python
# Protocol (abstracción)
class IPValidator(Protocol):
    def validate(self, ip: str) -> bool: ...
    def get_error_message(self) -> str: ...

# Alto nivel depende de abstracción
class ConfigPanel:
    def __init__(self, ip_validator: IPValidator | None = None):
        self._ip_validator = ip_validator or DefaultIPValidator()
```

**Beneficios:**
- DIP cumplido: alto nivel no depende de bajo nivel
- Duck typing: no requiere herencia explícita
- Fácil agregar nuevos validators sin modificar `ConfigPanel`

---

## Decisiones de Diseño

### Decisión 1: ¿Por qué separar EphemeralSocketClient de PersistentSocketClient?

#### Alternativas Consideradas

```mermaid
graph LR
    A["Opción 1:<br/>Cliente único<br/>configurable"] -->|rechazada| X1[❌]
    B["Opción 2:<br/>Dos clientes<br/>especializados"] -->|adoptada| V1[✅]

    style A fill:#FEE2E2
    style B fill:#D1FAE5
```

**Opción 1: Cliente único configurable**
```python
class SocketClient:
    def __init__(self, host, port, persistent=False):
        self._persistent = persistent

    def send(self, data):
        if self._persistent:
            # lógica conexión persistente
        else:
            # lógica conexión efímera
```

**Problemas:**
- Viola SRP: una clase hace dos cosas diferentes
- Cohesión baja: comportamientos no relacionados mezclados
- Más complejo de testear (múltiples caminos)

**Opción 2: Dos clientes especializados**
```python
class EphemeralSocketClient(SocketClientBase):
    def send(self, data): ...  # conectar→enviar→cerrar

class PersistentSocketClient(SocketClientBase):
    def connect(self): ...
    def send(self, data): ...  # requiere conexión previa
    def disconnect(self): ...
```

#### Decisión: Dos Clientes Especializados

**Justificación:**

1. **Patrones de uso diferentes:**
   - Efímero: simuladores (envío periódico, sin estado de conexión)
   - Persistente: UX termostato (recepción continua, mantiene conexión)

2. **SRP cumplido:**
   - `EphemeralSocketClient`: una razón para cambiar (patrón efímero)
   - `PersistentSocketClient`: una razón para cambiar (patrón persistente)

3. **Señales PyQt específicas:**
   ```python
   # EphemeralSocketClient
   data_sent = pyqtSignal()
   error_occurred = pyqtSignal(str)

   # PersistentSocketClient
   connected = pyqtSignal()
   disconnected = pyqtSignal()
   data_received = pyqtSignal(str)
   error_occurred = pyqtSignal(str)
   ```

4. **API clara y semántica:**
   ```python
   # Efímero: send() hace todo (conecta, envía, cierra)
   ephemeral.send("4.20")

   # Persistente: flujo explícito
   persistent.connect()
   persistent.send("aumentar")
   persistent.disconnect()
   ```

#### Trade-offs

| Aspecto | Pro ✅ | Con ⚠️ |
|---------|-------|-------|
| **Cohesión** | Alta (cada clase hace una cosa) | - |
| **SRP** | Cumplido perfectamente | - |
| **Código duplicado** | - | Mitigado por `SocketClientBase` |
| **Curva de aprendizaje** | API clara y simple | Dos clases en lugar de una |
| **Testabilidad** | Fácil (paths independientes) | - |

#### Diagrama Comparativo

```mermaid
graph TB
    subgraph Efímero["Patrón Efímero"]
        E1[Crear socket] --> E2[Conectar]
        E2 --> E3[Enviar]
        E3 --> E4[Cerrar]
        E4 --> E5[emit data_sent]
    end

    subgraph Persistente["Patrón Persistente"]
        P1[connect: Crear socket] --> P2[connect: Conectar]
        P2 --> P3[Iniciar thread recepción]
        P3 --> P4[send: Enviar datos]
        P4 --> P5[receive_loop: Recibir datos]
        P5 --> P6[disconnect: Cerrar]
    end

    style Efímero fill:#E8F4F8
    style Persistente fill:#FEF3E2
```

**Calificación:** 10/10 - Decisión correcta, cumple SOLID.

---

### Decisión 2: ¿Por qué usar Protocols para DIP en lugar de herencia?

#### Alternativas Consideradas

```mermaid
graph LR
    A["Opción 1:<br/>Herencia<br/>de clase base"] -->|rechazada| X1[❌]
    B["Opción 2:<br/>Protocols<br/>(duck typing)"] -->|adoptada| V1[✅]

    style A fill:#FEE2E2
    style B fill:#D1FAE5
```

**Opción 1: Herencia de clase base abstracta**
```python
from abc import ABC, abstractmethod

class IPValidatorBase(ABC):
    @abstractmethod
    def validate(self, ip: str) -> bool: ...

class DefaultIPValidator(IPValidatorBase):
    def validate(self, ip: str) -> bool:
        # implementación
```

**Problemas:**
- Requiere modificar jerarquía de herencia
- Menos flexible (fuerza herencia)
- No permite duck typing

**Opción 2: Protocols (duck typing)**
```python
from typing import Protocol

class IPValidator(Protocol):
    def validate(self, ip: str) -> bool: ...

# Cualquier clase con validate() es IPValidator
class CustomValidator:  # No necesita heredar
    def validate(self, ip: str) -> bool:
        # implementación
```

#### Decisión: Protocols

**Justificación:**

1. **Flexibilidad:** No requiere herencia explícita
   ```python
   # Esto funciona aunque CustomValidator no herede de IPValidator
   class CustomValidator:
       def validate(self, ip: str) -> bool:
           return True

   validator: IPValidator = CustomValidator()  # ✅ OK
   ```

2. **DIP perfecto:** Consumidores dependen de abstracción, no de implementación
   ```python
   class ConfigPanel:
       def __init__(self, ip_validator: IPValidator | None = None):
           # Depende del Protocol, no de DefaultIPValidator
   ```

3. **Duck typing pythónico:**
   - Si camina como pato y hace cuac, es un pato
   - Si tiene `validate()`, es un `IPValidator`

4. **No fuerza modificar jerarquías:**
   ```python
   # Clase existente puede ser IPValidator sin modificarla
   class ExistingValidator:
       def validate(self, ip: str) -> bool: ...

   # No necesita heredar de IPValidator, ya lo implementa
   ```

#### Trade-offs

| Aspecto | Pro ✅ | Con ⚠️ |
|---------|-------|-------|
| **Flexibilidad** | Máxima (no requiere herencia) | - |
| **DIP** | Cumplido perfectamente | - |
| **Type safety** | - | Sin validación en runtime (pero mypy valida) |
| **Pythonico** | Duck typing natural | - |
| **Extensibilidad** | Fácil agregar nuevos providers | - |

#### Ejemplo de Extensibilidad

```mermaid
classDiagram
    class LEDColorProvider {
        <<Protocol>>
        +get_color_on() str
        +get_color_off() str
    }

    class DefaultLEDColorProvider {
        +get_color_on() str
        +get_color_off() str
    }

    class AnimatedLEDColorProvider {
        +get_color_on() str
        +get_color_off() str
        +animate()
    }

    class ThemeLEDColorProvider {
        +get_color_on() str
        +get_color_off() str
        +sync_with_theme()
    }

    LEDColorProvider <|.. DefaultLEDColorProvider
    LEDColorProvider <|.. AnimatedLEDColorProvider
    LEDColorProvider <|.. ThemeLEDColorProvider

    note for AnimatedLEDColorProvider "Sin modificar Protocol<br/>ni LEDIndicator"
```

**Calificación:** 10/10 - Uso correcto de protocols, DIP cumplido.

---

### Decisión 3: ¿Por qué widgets con composición en lugar de herencia?

#### Alternativas Consideradas

```mermaid
graph LR
    A["Opción 1:<br/>Herencia<br/>de QWidget"] -->|rechazada| X1[❌]
    B["Opción 2:<br/>Composición<br/>de QWidgets"] -->|adoptada| V1[✅]

    style A fill:#FEE2E2
    style B fill:#D1FAE5
```

**Opción 1: Herencia compleja**
```python
class BaseLEDWidget(QWidget):
    # lógica común de LEDs

class LEDIndicator(BaseLEDWidget):
    # hereda BaseLEDWidget → QWidget
```

**Problemas:**
- Jerarquía de herencia compleja
- Acoplamiento alto entre clases
- Difícil modificar comportamiento en runtime

**Opción 2: Composición**
```python
class LEDIndicator(QWidget):
    def __init__(self, color_provider: LEDColorProvider | None = None):
        # Componer en lugar de heredar
        self._color_provider = color_provider or DefaultLEDColorProvider()
```

#### Decisión: Composición

**Justificación:**

1. **"Composition over inheritance" (GoF):**
   - Favorece flexibilidad sobre jerarquías rígidas
   - Permite cambiar comportamiento en runtime

2. **Inyección de dependencias:**
   ```python
   # Cambiar colores sin heredar
   led = LEDIndicator(color_provider=CustomLEDColorProvider())
   ```

3. **Testabilidad:**
   ```python
   # Test con mock provider
   mock_provider = MockLEDColorProvider()
   led = LEDIndicator(color_provider=mock_provider)
   ```

4. **Sin jerarquías complejas:**
   ```
   QWidget
     ↑
   LEDIndicator (solo)

   (en lugar de)

   QWidget
     ↑
   BaseLEDWidget
     ↑
   LEDIndicator
     ↑
   AnimatedLEDIndicator
   ```

#### Trade-offs

| Aspecto | Pro ✅ | Con ⚠️ |
|---------|-------|-------|
| **Flexibilidad** | Cambiar providers en runtime | - |
| **Acoplamiento** | Bajo (depende de protocols) | - |
| **Delegación** | - | Más código de delegación (mitigado) |
| **Testabilidad** | Fácil inyectar mocks | - |
| **Reutilización** | Compartir providers entre widgets | - |

#### Ejemplo de Composición

```mermaid
classDiagram
    class LEDIndicator {
        -_color_provider: LEDColorProvider
        -_state: bool
        +set_state(active)
        +paintEvent(event)
    }

    class LEDColorProvider {
        <<Protocol>>
        +get_color_on() str
        +get_color_off() str
    }

    class DefaultLEDColorProvider {
        +get_color_on() "green"
        +get_color_off() "gray"
    }

    LEDIndicator *-- LEDColorProvider : compone
    LEDColorProvider <|.. DefaultLEDColorProvider

    note for LEDIndicator "Delega colores al provider<br/>Cambiable en runtime"
```

**Calificación:** 10/10 - Composición favorece flexibilidad y testabilidad.

---

### Decisión 4: ¿Por qué ThemeProvider como Protocol?

#### Alternativas Consideradas

```mermaid
graph LR
    A["Opción 1:<br/>Singleton<br/>global"] -->|rechazada| X1[❌]
    B["Opción 2:<br/>Módulo<br/>global"] -->|rechazada| X2[❌]
    C["Opción 3:<br/>Protocol<br/>inyectable"] -->|adoptada| V1[✅]

    style A fill:#FEE2E2
    style B fill:#FEE2E2
    style C fill:#D1FAE5
```

**Opción 1: Singleton tradicional**
```python
class ThemeManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Problemas:**
- Estado global mutable
- Difícil de testear (un solo estado)
- Viola DIP

**Opción 2: Módulo global**
```python
# theme_config.py
CURRENT_THEME = load_dark_theme()
```

**Problemas:**
- Estado global
- Sin abstracción
- No intercambiable

**Opción 3: Protocol con inyección**
```python
class ThemeProvider(Protocol):
    def get_stylesheet(self) -> str: ...

# Uso
provider: ThemeProvider = FileThemeProvider("dark_theme.qss")
app.setStyleSheet(provider.get_stylesheet())
```

#### Decisión: Protocol Inyectable

**Justificación:**

1. **DIP cumplido:** Aplicación depende del protocol, no de implementación
   ```python
   def setup_theme(app: QApplication, provider: ThemeProvider):
       app.setStyleSheet(provider.get_stylesheet())
   ```

2. **Intercambiabilidad:**
   ```python
   # Producción
   provider = FileThemeProvider("dark_theme.qss")

   # Desarrollo (tema dinámico)
   provider = GeneratedThemeProvider()

   # Ambos implementan ThemeProvider
   ```

3. **Testabilidad:**
   ```python
   # Test con tema mock
   mock_provider = MockThemeProvider()
   assert "QWidget" in mock_provider.get_stylesheet()
   ```

4. **Sin estado global mutable:**
   - Cada aplicación puede tener su proveedor
   - No interfiere con tests paralelos

#### Trade-offs

| Aspecto | Pro ✅ | Con ⚠️ |
|---------|-------|-------|
| **DIP** | Cumplido perfectamente | - |
| **Testabilidad** | Fácil inyectar mocks | - |
| **Estado global** | - | Evitado (bien) |
| **Flexibilidad** | Intercambiar providers | - |
| **Simplicidad** | - | Requiere pasar provider (aceptable) |

#### Implementaciones de ThemeProvider

```mermaid
classDiagram
    class ThemeProvider {
        <<Protocol>>
        +get_stylesheet() str
    }

    class FileThemeProvider {
        -_stylesheet_path: Path
        -_cached_stylesheet: str | None
        +get_stylesheet() str
        -_load_from_file() str
    }

    class GeneratedThemeProvider {
        -_generator: QSSGenerator
        -_colors: DarkThemeColors
        +get_stylesheet() str
    }

    ThemeProvider <|.. FileThemeProvider
    ThemeProvider <|.. GeneratedThemeProvider

    note for FileThemeProvider "Producción:<br/>Carga dark_theme.qss<br/>Con caché"
    note for GeneratedThemeProvider "Desarrollo:<br/>Genera QSS dinámico<br/>desde DarkThemeColors"
```

**Calificación:** 10/10 - Protocol permite flexibilidad sin estado global.

---

## Flujo de Uso Típico

### Ejemplo: simulador_bateria usando compartido

```mermaid
sequenceDiagram
    participant SB as simulador_bateria
    participant Factory as ComponenteFactory
    participant Client as EphemeralSocketClient
    participant Server as ISSE_Termostato
    participant Panel as ConfigPanel
    participant Theme as FileThemeProvider

    Note over SB: Inicialización
    SB->>Factory: crear_cliente(host, port)
    Factory->>Client: __init__(host, port)
    Client-->>Factory: cliente_bateria
    Factory-->>SB: cliente_bateria

    SB->>Theme: FileThemeProvider("dark_theme.qss")
    Theme-->>SB: provider
    SB->>SB: app.setStyleSheet(provider.get_stylesheet())

    SB->>Panel: ConfigPanel(default_ip, default_port)
    Panel-->>SB: panel_conexion

    Note over SB: Usuario conecta
    Panel->>SB: emit connect_requested()
    SB->>Client: send("4.20")
    Client->>Client: _create_socket()
    Client->>Server: connect + sendall("4.20")
    Server-->>Client: ACK
    Client->>SB: emit data_sent()

    Note over SB: Envío periódico
    loop cada 2 segundos
        SB->>Client: send_async(voltaje)
        Client->>Server: connect + sendall + close
        Client->>SB: emit data_sent()
    end
```

### Flujo de Inyección de Dependencias

```mermaid
graph TB
    subgraph "Producto (simulador_bateria)"
        Main["run.py"]
        Factory["ComponenteFactory"]
    end

    subgraph "compartido/networking"
        ClientBase["SocketClientBase"]
        Ephemeral["EphemeralSocketClient"]
    end

    subgraph "compartido/widgets"
        Config["ConfigPanel"]
        LED["LEDIndicator"]
    end

    subgraph "compartido/estilos"
        ThemeP["ThemeProvider (Protocol)"]
        FileTheme["FileThemeProvider"]
    end

    Main -->|crea| Factory
    Factory -->|instancia| Ephemeral
    Ephemeral -.->|hereda| ClientBase

    Factory -->|instancia| Config
    Config *--o LED

    Main -->|instancia| FileTheme
    FileTheme -.->|implementa| ThemeP

    style Main fill:#E8F4F8
    style compartido fill:#D1FAE5
```

---

## Métricas de Reutilización

### Tabla de Uso por Producto

| Componente | simulador_temperatura | simulador_bateria | ux_termostato | Reutilización |
|------------|----------------------|-------------------|---------------|---------------|
| **networking/** |
| EphemeralSocketClient | ✅ | ✅ | ❌ | 66% (2/3) |
| PersistentSocketClient | ❌ | ❌ | ✅ | 33% (1/3) |
| BaseSocketServer | ❌ | ❌ | ✅ | 33% (1/3) |
| **widgets/** |
| ConfigPanel | ✅ | ✅ | ✅ | 100% (3/3) |
| LEDIndicator | ❌ | ✅ | ✅ | 66% (2/3) |
| LogViewer | ✅ | ✅ | ✅ | 100% (3/3) |
| StatusIndicator | ✅ | ✅ | ✅ | 100% (3/3) |
| ValidationFeedback | ✅ | ✅ | ✅ | 100% (3/3) |
| **estilos/** |
| FileThemeProvider | ✅ | ✅ | ✅ | 100% (3/3) |
| ThemeColors | ✅ | ✅ | ✅ | 100% (3/3) |
| **quality/** |
| calculate_metrics.py | ✅ | ✅ | ✅ | 100% (3/3) |
| validate_gates.py | ✅ | ✅ | ✅ | 100% (3/3) |

### Métricas Agregadas

```mermaid
pie title Reutilización de Componentes
    "Usados en 3 productos" : 8
    "Usados en 2 productos" : 2
    "Usados en 1 producto" : 2
```

**Estadísticas:**
- **Componentes totales:** 12
- **Reutilización 100% (3/3 productos):** 8 componentes (66%)
- **Reutilización 66% (2/3 productos):** 2 componentes (17%)
- **Reutilización 33% (1/3 productos):** 2 componentes (17%)
- **Tasa de reutilización promedio:** 83%

**Conclusión:** ✅ Diseño altamente reutilizable. 66% de componentes usados por los 3 productos.

---

## Métricas de Calidad

### Complejidad Ciclomática y Mantenibilidad

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| **Complejidad Ciclomática (CC)** | 1.56 | ≤ 10 | ✅ Excelente |
| **Índice de Mantenibilidad (MI)** | 83.05 | > 20 | ✅ Excelente |
| **Pylint Score** | 9.34/10 | ≥ 8.0 | ✅ Muy bueno |
| **Coverage** | 89.5% | - | ✅ Muy bueno |
| **Tests** | 150+ | - | ✅ Robusto |

### Evaluación SOLID

| Principio | Calificación | Evidencia |
|-----------|--------------|-----------|
| **Single Responsibility** | 10/10 | Cada clase tiene una responsabilidad clara |
| **Open/Closed** | 10/10 | Extensible mediante protocols (ThemeProvider, IPValidator) |
| **Liskov Substitution** | 10/10 | Subtipos sustituibles (SocketClientBase → Ephemeral/Persistent) |
| **Interface Segregation** | 10/10 | Interfaces mínimas (ThemeProvider: 1 método) |
| **Dependency Inversion** | 9/10 | Protocols en lugar de clases concretas |
| **TOTAL SOLID** | **9.8/10** | ✅ Sobresaliente |

### Distribución de Complejidad

```mermaid
graph LR
    subgraph networking["networking/ - CC: 1.45"]
        N1["EphemeralSocketClient: 1.2"]
        N2["PersistentSocketClient: 1.8"]
        N3["BaseSocketServer: 1.5"]
    end

    subgraph widgets["widgets/ - CC: 1.62"]
        W1["ConfigPanel: 2.1"]
        W2["LEDIndicator: 1.1"]
        W3["LogViewer: 1.8"]
    end

    subgraph estilos["estilos/ - CC: 1.35"]
        E1["QSSGenerator: 1.9"]
        E2["FileThemeProvider: 1.0"]
    end

    style networking fill:#E8F4F8
    style widgets fill:#F0F4F8
    style estilos fill:#FEF3E2
```

**Nota:** Todos los módulos están muy por debajo del umbral de CC ≤ 10. QSSGenerator tiene CC 1.9 (aceptable para generador de QSS complejo).

---

## Comparación con Buenas Prácticas

| Práctica | Estado | Evidencia |
|----------|--------|-----------|
| **Separation of Concerns** | ✅ | 3 módulos independientes (networking, widgets, estilos) |
| **DRY (Don't Repeat Yourself)** | ✅ | SocketClientBase, providers reutilizables |
| **YAGNI (You Aren't Gonna Need It)** | ✅ | Sin over-engineering, solo lo necesario |
| **KISS (Keep It Simple)** | ✅ | Soluciones directas, CC promedio 1.56 |
| **Composition over Inheritance** | ✅ | Todos los widgets usan composición |
| **Dependency Injection** | ✅ | Usado en todos los componentes configurables |
| **Protocol-Oriented Design** | ✅ | DIP con protocols (ThemeProvider, IPValidator, etc.) |
| **Type Safety** | ✅ | Type hints completos en todas las clases |
| **Fail Fast** | ✅ | Validaciones tempranas en constructores |
| **Reutilización** | ✅ | 83% reutilización promedio entre productos |

---

## Referencias

- [Reporte de Calidad de Diseño](informes/informe_diseno.md) - Análisis SOLID y patrones
- [Guía de Uso](guia_uso.md) - Ejemplos de integración en productos
- [ESPECIFICACION_COMUNICACIONES.md](../../docs/ESPECIFICACION_COMUNICACIONES.md) - Protocolo TCP
- [ADR-001: Separación Socket Clients](../../docs/ADR-001-separacion-socket-clients.md) - Decisión efímero vs persistente

---

**Versión:** 1.0
**Fecha:** 2026-01-31
**Estado:** Producción (usado en 3 productos activos)
