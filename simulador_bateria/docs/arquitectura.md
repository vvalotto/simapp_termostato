# Arquitectura del Simulador de Batería

## Visión General

El Simulador de Batería es un cliente TCP que genera valores de voltaje simulados (modo manual por slider) y los envía al servidor ISSE_Termostato en el puerto 11000. Implementa una arquitectura en capas con patrones MVC, Factory y Coordinator.

```mermaid
flowchart TB
    subgraph SimBat["Simulador de Batería (PyQt6)"]
        RunPy["run.py<br/>AplicacionSimulador<br/>(Lifecycle)"]

        RunPy --> Factory["Factory"]
        RunPy --> Coordinator["Coordinator"]
        RunPy --> Compositor["UIPrincipal<br/>Compositor"]

        Factory --> Controllers
        Coordinator --> Controllers
        Compositor --> Controllers

        subgraph Controllers["Controladores MVC"]
            CtrlEstado["CtrlEstado"]
            CtrlControl["CtrlControl"]
            CtrlConexion["CtrlConexion"]
        end

        Controllers --> Dominio["Dominio<br/>Generador<br/>Batería"]
        Controllers --> Comunicacion["Comunicación<br/>Cliente<br/>Servicio"]
        Controllers --> Presentacion["Presentación<br/>Vistas<br/>(PyQt6)"]
    end

    Comunicacion -->|TCP :11000| RPi["ISSE_Termostato<br/>(Raspberry Pi)"]

    style SimBat fill:#f5f5f5,stroke:#333,stroke-width:2px
    style Controllers fill:#e1f5e1,stroke:#333
    style Dominio fill:#e1e8f5,stroke:#333
    style Comunicacion fill:#fff4e1,stroke:#333
    style Presentacion fill:#ffe1e1,stroke:#333
    style RPi fill:#e8e8e8,stroke:#333,stroke-width:2px
```

---

## Estructura de Módulos

```
simulador_bateria/
├── run.py                          # Entry point + AplicacionSimulador
├── app/
│   ├── factory.py                  # ComponenteFactory
│   ├── coordinator.py              # SimuladorCoordinator
│   │
│   ├── configuracion/              # Capa de configuración
│   │   ├── config.py               # ConfigManager, ConfigSimuladorBateria
│   │   └── constantes.py           # Valores por defecto
│   │
│   ├── dominio/                    # Capa de lógica de negocio
│   │   ├── estado_bateria.py       # Modelo de datos (dataclass)
│   │   └── generador_bateria.py    # Generador de valores (modo manual)
│   │
│   ├── comunicacion/               # Capa de comunicación TCP
│   │   ├── cliente_bateria.py      # Cliente TCP
│   │   └── servicio_envio.py       # Integración gen+cliente
│   │
│   └── presentacion/               # Capa de presentación (UI)
│       ├── ui_compositor.py        # UIPrincipalCompositor
│       │
│       └── paneles/                # Arquitectura MVC
│           ├── base.py             # ModeloBase, VistaBase, ControladorBase
│           ├── estado/             # Panel Estado
│           │   ├── modelo.py       # PanelEstadoModelo
│           │   ├── vista.py        # PanelEstadoVista
│           │   └── controlador.py  # PanelEstadoControlador
│           ├── control/            # Panel Control Voltaje
│           │   ├── modelo.py       # ControlPanelModelo
│           │   ├── vista.py        # ControlPanelVista
│           │   └── controlador.py  # ControlPanelControlador
│           └── conexion/           # Panel Conexión
│               ├── modelo.py       # ConexionPanelModelo
│               ├── vista.py        # ConexionPanelVista
│               └── controlador.py  # ConexionPanelControlador
│
├── tests/                          # Tests unitarios (275 tests, 96% coverage)
├── quality/                        # Scripts de calidad
└── docs/                           # Documentación
```

---

## Patrones de Diseño

### 1. Factory Pattern

```mermaid
classDiagram
    class ComponenteFactory {
        -_config: ConfigSimuladorBateria
        +crear_generador() GeneradorBateria
        +crear_cliente(host, port) ClienteBateria
        +crear_servicio(gen, cli) ServicioEnvioBateria
        +crear_controladores() dict~str, Controlador~
    }

    ComponenteFactory --> GeneradorBateria : crea
    ComponenteFactory --> ClienteBateria : crea
    ComponenteFactory --> ServicioEnvioBateria : crea
    ComponenteFactory --> Controladores : crea

    class Controladores {
        estado: PanelEstadoControlador
        control: ControlPanelControlador
        conexion: ConexionPanelControlador
    }

    note for ComponenteFactory "Centraliza creación de componentes\ncon configuración consistente"
```

**Responsabilidad:** Centraliza la creación de todos los componentes, permitiendo configuración consistente y facilitando testing con mocks.

### 2. Coordinator Pattern

```mermaid
classDiagram
    class SimuladorCoordinator {
        -_generador: GeneradorBateria
        -_servicio: ServicioEnvioBateria
        -_ctrl_estado: PanelEstadoControlador
        -_ctrl_control: ControlPanelControlador
        -_ctrl_conexion: ConexionPanelControlador
        +set_servicio(servicio) None
        +ip_configurada: str
        +puerto_configurado: int
        <<signal>> conexion_solicitada()
        <<signal>> desconexion_solicitada()
    }

    SimuladorCoordinator ..> GeneradorBateria : conecta señales
    SimuladorCoordinator ..> ServicioEnvioBateria : conecta señales
    SimuladorCoordinator ..> CtrlEstado : conecta señales
    SimuladorCoordinator ..> CtrlControl : conecta señales
    SimuladorCoordinator ..> CtrlConexion : conecta señales

    note for SimuladorCoordinator "Conecta señales entre:\n• Generador ↔ CtrlEstado\n• CtrlControl → Generador (slider)\n• CtrlConexion → conexion/desconexion\n• Servicio ↔ CtrlEstado"
```

**Responsabilidad:** Gestiona todas las conexiones de señales PyQt6 entre componentes, desacoplando la lógica de conexión del ciclo de vida.

**Diferencia con simulador_temperatura:** No hay panel gráfico, el control es solo manual (slider).

### 3. Compositor Pattern

```mermaid
flowchart TB
    subgraph Compositor["UIPrincipalCompositor"]
        direction TB
        Info["Recibe controladores configurados<br/>Solo compone layout visual<br/>Sin lógica de negocio"]

        subgraph Params["Constructor Parameters"]
            P1["ctrl_estado: PanelEstadoControlador"]
            P2["ctrl_control: ControlPanelControlador"]
            P3["ctrl_conexion: ConexionPanelControlador"]
        end
    end

    Compositor ==> Layout

    subgraph Layout["Layout Compuesto"]
        direction TB
        PanelEstado["Panel Estado<br/>Voltaje actual, conexión<br/>Envíos exitosos/fallidos"]
        PanelControl["Panel Control<br/>Slider de voltaje (0.0V - 5.0V)"]
        PanelConexion["Panel Conexión<br/>IP, Puerto, Botón Conectar/Desconectar"]

        PanelEstado --> PanelControl
        PanelControl --> PanelConexion
    end

    style Compositor fill:#fff4e1,stroke:#333
    style Layout fill:#f5f5f5,stroke:#333,stroke-width:2px
    style PanelEstado fill:#e1f5e1,stroke:#333
    style PanelControl fill:#e1f5e1,stroke:#333
    style PanelConexion fill:#e1f5e1,stroke:#333
```

### 4. MVC Pattern (Model-View-Controller)

```mermaid
classDiagram
    class Modelo {
        <<dataclass>>
        Datos puros
        Sin lógica
        Inmutable
    }

    class Vista {
        <<QWidget>>
        Solo UI
        Sin lógica
        Emite eventos
    }

    class Controlador {
        <<QObject>>
        Lógica
        Coordina M+V
        Señales Qt
    }

    Controlador --> Modelo : actualiza
    Controlador --> Vista : actualiza
    Vista ..> Controlador : eventos

    class PanelEstadoModelo {
        <<dataclass>>
        +voltaje: float
        +conectado: bool
        +envios_exitosos: int
        +envios_fallidos: int
    }

    class PanelEstadoVista {
        <<QWidget>>
        +label_voltaje: QLabel
        +led_conexion: LedIndicator
        +label_envios: QLabel
        +label_errores: QLabel
    }

    class PanelEstadoControlador {
        <<QObject>>
        -_modelo: PanelEstadoModelo
        -_vista: PanelEstadoVista
        +actualizar_voltaje(float)
        +registrar_envio(bool)
    }

    PanelEstadoModelo --|> Modelo : ejemplo
    PanelEstadoVista --|> Vista : ejemplo
    PanelEstadoControlador --|> Controlador : ejemplo

    PanelEstadoControlador --> PanelEstadoModelo
    PanelEstadoControlador --> PanelEstadoVista
```

---

## Diagrama de Clases: Capa de Dominio

```mermaid
classDiagram
    class EstadoBateria {
        <<dataclass>>
        +voltaje: float
        +timestamp: datetime
        +en_rango: bool
        +to_string() str
        +validar_rango(min, max) bool
    }

    class GeneradorBateria {
        <<QObject>>
        -_config: ConfigSimuladorBateria
        -_voltaje_actual: float
        -_timer: QTimer
        +generar_valor() EstadoBateria
        +set_voltaje(voltaje) None
        +voltaje_actual: float
        +iniciar() None
        +detener() None
        <<signal>> valor_generado(EstadoBateria)
        <<signal>> voltaje_cambiado(float)
    }

    GeneradorBateria --> EstadoBateria : genera

    note for GeneradorBateria "Solo modo manual (slider)\nSin variación senoidal\nRango: 0.0V - 5.0V"
    note for EstadoBateria "Representa el estado\nde voltaje de batería"
```

**Diferencias con simulador_temperatura:**
- No hay `VariacionSenoidal` (no hay modo automático)
- Solo control manual por slider
- Rango: 0.0V - 5.0V (voltaje de batería)

---

## Diagrama de Clases: Capa de Comunicación

```mermaid
classDiagram
    class EphemeralSocketClient {
        <<QObject>>
        +send(data) bool
        +send_async(data) None
        <<signal>> data_sent()
        <<signal>> error_occurred(str)
    }

    class ClienteBateria {
        <<QObject>>
        -_host: str
        -_port: int
        -_cliente: EphemeralSocketClient
        -_ultimo_valor: float
        +enviar_voltaje(v) bool
        +enviar_voltaje_async(v) None
        +enviar_estado(estado) bool
        +enviar_estado_async(estado) None
        +host: str
        +port: int
        <<signal>> dato_enviado(float)
        <<signal>> error_conexion(str)
    }

    class ServicioEnvioBateria {
        <<QObject>>
        -_generador: GeneradorBateria
        -_cliente: ClienteBateria
        -_activo: bool
        +iniciar() None
        +detener() None
        +activo: bool
        +generador: GeneradorBateria
        +cliente: ClienteBateria
        <<signal>> envio_exitoso(float)
        <<signal>> envio_fallido(str)
        <<signal>> servicio_iniciado()
        <<signal>> servicio_detenido()
    }

    ClienteBateria --> EphemeralSocketClient : usa
    ServicioEnvioBateria --> ClienteBateria : usa
    ServicioEnvioBateria --> GeneradorBateria : escucha

    note for EphemeralSocketClient "De compartido/networking\nPatrón: connect→send→close"
    note for ServicioEnvioBateria "Integra generador + cliente\nEscucha valor_generado y envía"
```

**Protocolo:** Puerto 11000, formato `"<voltaje>"` (ej: `"4.20"`), patrón efímero.

---

## Diagrama de Clases: Capa de Presentación (MVC)

```mermaid
classDiagram
    class ModeloBase {
        <<ABC>>
    }

    class VistaBase {
        <<QWidget>>
        +actualizar(modelo) None
    }

    class ControladorBase {
        <<QObject>>
        -_modelo: ModeloBase
        -_vista: VistaBase
        +vista: VistaBase
        +modelo: ModeloBase
    }

    %% Panel Estado
    class PanelEstadoModelo {
        <<dataclass>>
        +voltaje: float
        +conectado: bool
        +envios_exitosos: int
        +envios_fallidos: int
    }

    class PanelEstadoVista {
        <<QWidget>>
        +lbl_voltaje: QLabel
        +led_conexion: LedIndicator
        +lbl_envios_ok: QLabel
        +lbl_envios_error: QLabel
    }

    class PanelEstadoControlador {
        <<QObject>>
        +actualizar_voltaje(float) None
        +registrar_envio(bool) None
    }

    %% Panel Control
    class ControlPanelModelo {
        <<dataclass>>
        +voltaje: float
        +voltaje_minimo: float
        +voltaje_maximo: float
        +precision: int
    }

    class ControlPanelVista {
        <<QWidget>>
        +slider_voltaje: QSlider
        +spinbox_voltaje: QDoubleSpinBox
        +lbl_voltaje: QLabel
    }

    class ControlPanelControlador {
        <<QObject>>
        +on_slider_cambiado(int) None
        +set_voltaje(float) None
    }

    %% Panel Conexión
    class ConexionPanelModelo {
        <<dataclass>>
        +ip: str
        +puerto: int
    }

    class ConexionPanelVista {
        <<QWidget>>
        +input_ip: QLineEdit
        +input_puerto: QSpinBox
        +btn_conectar: QPushButton
    }

    class ConexionPanelControlador {
        <<QObject>>
        +on_conectar() None
        +on_desconectar() None
        +validar_ip(str) bool
    }

    %% Herencia
    PanelEstadoModelo --|> ModeloBase
    PanelEstadoVista --|> VistaBase
    PanelEstadoControlador --|> ControladorBase

    ControlPanelModelo --|> ModeloBase
    ControlPanelVista --|> VistaBase
    ControlPanelControlador --|> ControladorBase

    ConexionPanelModelo --|> ModeloBase
    ConexionPanelVista --|> VistaBase
    ConexionPanelControlador --|> ControladorBase

    note for ModeloBase "Clases base en\napp/presentacion/paneles/base.py"
    note for ControlPanelControlador "Solo modo manual\nSin panel gráfico"
```

**Nota:** No hay panel gráfico (a diferencia del simulador_temperatura).

---

## Diagrama de Secuencia: Inicio de Aplicación

```mermaid
sequenceDiagram
    participant Main as main
    participant Factory
    participant Coordinator
    participant Compositor
    participant Controllers
    participant Dominio

    Main->>Factory: crear()
    Factory->>Dominio: crear_generador()
    Factory->>Dominio: crear_cliente()
    Factory->>Controllers: crear_controladores()
    Controllers-->>Factory: dict{estado, control, conexion}
    Factory-->>Main: componentes creados

    Main->>Compositor: crear Compositor(controllers)
    Compositor->>Controllers: obtener vistas
    Compositor->>Compositor: componer layout
    Compositor-->>Main: layout compuesto

    Main->>Coordinator: crear Coordinator(gen, controllers)
    Coordinator->>Controllers: conectar señales
    Coordinator->>Dominio: conectar a generador
    Coordinator-->>Main: señales conectadas

    Main->>Compositor: mostrar()
    Note over Main,Dominio: Aplicación lista y visible
```

---

## Diagrama de Secuencia: Flujo de Conexión

```mermaid
sequenceDiagram
    actor Usuario
    participant PanelConexion as PanelConex
    participant Coordinator
    participant App as AplicacionSim
    participant Factory
    participant Servicio

    Usuario->>PanelConexion: click Conectar
    PanelConexion->>Coordinator: conectar_solicitado()
    Coordinator->>App: emit conexion_solicitada()

    App->>Coordinator: obtener ip/puerto
    App->>Factory: crear_cliente(ip, port)
    App->>Factory: crear_servicio()
    Factory-->>App: servicio creado

    App->>Coordinator: set_servicio()
    App->>Servicio: iniciar()
    Servicio->>Servicio: generador.iniciar()<br/>(QTimer periódico)

    Note over Usuario,Servicio: Generador activo, enviando datos
```

---

## Diagrama de Secuencia: Envío Automático

```mermaid
sequenceDiagram
    participant Servicio as ServicioEnvio
    participant Gen as Generador
    participant Cliente as ClienteBateria
    participant Ephemeral as EphemeralSocket
    participant RPi as ISSE_Term:11000

    Servicio->>Gen: iniciar()
    Gen->>Gen: QTimer.start()

    loop cada intervalo_envio_ms
        Gen->>Gen: _on_timer()
        Gen->>Gen: generar_valor()<br/>(voltaje actual del slider)
        Gen->>Servicio: valor_generado(estado)

        Servicio->>Cliente: enviar_estado_async(estado)
        Cliente->>Ephemeral: send_async()

        Ephemeral->>Ephemeral: connect()
        Ephemeral->>Ephemeral: send()
        Ephemeral->>Ephemeral: close()
        Ephemeral->>RPi: "4.20"

        Ephemeral-->>Cliente: data_sent()
        Cliente-->>Gen: dato_enviado(4.20)
        Gen-->>Servicio: envio_exitoso(4.20)
    end

    Note over Servicio,RPi: Patrón efímero: connect→send→close
```

---

## Diagrama de Secuencia: Control Manual de Voltaje

```mermaid
sequenceDiagram
    actor Usuario
    participant CtrlControl
    participant Coordinator
    participant Generador
    participant CtrlEstado

    Usuario->>CtrlControl: mover slider
    CtrlControl->>CtrlControl: slider_cambiado(paso)<br/>paso→voltaje
    CtrlControl->>Coordinator: voltaje_cambiado(4.2)

    Coordinator->>Generador: set_voltaje(4.2)
    Generador->>CtrlEstado: voltaje_cambiado(4.2)
    CtrlEstado->>CtrlEstado: actualizar_voltaje()
    Note over CtrlEstado: UI: "4.20 V"

    Generador->>Generador: generar_valor()<br/>(usa voltaje actual)

    Note over Usuario,CtrlEstado: El voltaje solo cambia cuando el usuario mueve el slider
```

---

## Protocolo de Comunicación

### Formato del Mensaje

```mermaid
flowchart LR
    A["Simulador<br/>Batería"] -->|TCP :11000| B["ISSE_Termostato<br/>(Raspberry Pi)"]

    subgraph Protocolo
        direction TB
        C["Formato: &lt;voltaje&gt;<br/>Ejemplo: '4.20' (llena), '3.50' (media), '2.80' (baja)<br/>Encoding: UTF-8<br/>Rango: 0.0V - 5.0V (sensor ADC)<br/>Patrón: Efímero"]
    end

    A -.->|especificación| Protocolo

    style A fill:#fff4e1,stroke:#333
    style B fill:#e8e8e8,stroke:#333,stroke-width:2px
    style Protocolo fill:#e1f5e1,stroke:#333
```

---

## Señales Qt (Observer Pattern)

| Componente | Señal | Parámetro | Descripción |
|------------|-------|-----------|-------------|
| `GeneradorBateria` | `valor_generado` | `EstadoBateria` | Nuevo valor generado |
| `GeneradorBateria` | `voltaje_cambiado` | `float` | Voltaje cambió |
| `ClienteBateria` | `dato_enviado` | `float` | Envío exitoso |
| `ClienteBateria` | `error_conexion` | `str` | Error de conexión |
| `ServicioEnvioBateria` | `envio_exitoso` | `float` | Dato enviado OK |
| `ServicioEnvioBateria` | `envio_fallido` | `str` | Error en envío |
| `ServicioEnvioBateria` | `servicio_iniciado` | - | Servicio iniciado |
| `ServicioEnvioBateria` | `servicio_detenido` | - | Servicio detenido |
| `SimuladorCoordinator` | `conexion_solicitada` | - | Usuario solicita conectar |
| `SimuladorCoordinator` | `desconexion_solicitada` | - | Usuario solicita desconectar |
| `ControlPanelControlador` | `voltaje_cambiado` | `float` | Slider modificado |
| `ConexionPanelControlador` | `conectar_solicitado` | - | Botón conectar pulsado |
| `ConexionPanelControlador` | `desconectar_solicitado` | - | Botón desconectar pulsado |

---

## Dependencias entre Módulos

```mermaid
graph TB
    RunPy[run.py] --> Factory
    RunPy --> Coordinator
    RunPy --> Compositor[UIPrincipalCompositor]

    Factory --> Controllers
    Coordinator --> Controllers
    Compositor --> Controllers

    subgraph Controllers["Controladores MVC (paneles/)"]
        CtrlEstado
        CtrlControl
        CtrlConexion
    end

    Controllers --> ModelosVistas["Modelos + Vistas MVC"]

    ModelosVistas --> Config[Configuracion<br/>ConfigManager]
    ModelosVistas --> Dominio[Dominio<br/>Generador<br/>Bateria]
    ModelosVistas --> Comunicacion[Comunicacion<br/>ServicioEnvio<br/>ClienteBateria]

    Config --> Dominio
    Dominio --> Comunicacion
    Comunicacion --> Compartido[compartido/networking<br/>EphemeralSocketClient]

    style RunPy fill:#e1f5e1,stroke:#333,stroke-width:2px
    style Factory fill:#fff4e1,stroke:#333
    style Coordinator fill:#fff4e1,stroke:#333
    style Compositor fill:#fff4e1,stroke:#333
    style Controllers fill:#e1e8f5,stroke:#333
    style ModelosVistas fill:#ffe1e1,stroke:#333
    style Config fill:#f5f5f5,stroke:#333
    style Dominio fill:#e1f5e1,stroke:#333
    style Comunicacion fill:#fff4e1,stroke:#333
    style Compartido fill:#e8e8e8,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
```

---

## Métricas de Calidad

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| **Complejidad Ciclomática** | 1.40 | ≤ 10 | ✅ OK |
| **Índice Mantenibilidad** | 80.98 | > 20 | ✅ OK |
| **Pylint Score** | 9.94/10 | ≥ 8.0 | ✅ OK |
| **Coverage** | 96% | - | ✅ Excelente |
| **Tests** | 275 | - | ✅ Pasando |
| **Archivos Python** | 19 | - | - |
| **Funciones** | 69 | - | - |
| **SLOC** | 453 | - | - |

### Evaluación SOLID

| Principio | Calificación | Estado |
|-----------|--------------|--------|
| **Single Responsibility** | 10/10 | ✅ Excelente |
| **Open/Closed** | 9/10 | ✅ Muy bueno |
| **Liskov Substitution** | 10/10 | ✅ Excelente |
| **Interface Segregation** | 10/10 | ✅ Excelente |
| **Dependency Inversion** | 9/10 | ✅ Muy bueno |
| **TOTAL SOLID** | **9.6/10** | ✅ Sobresaliente |

---

## Comparación con Simulador de Temperatura

| Aspecto | Simulador Temperatura | Simulador Batería |
|---------|----------------------|-------------------|
| **Puerto TCP** | 12000 | 11000 |
| **Modos** | Manual + Automático (senoidal) | Solo Manual |
| **Rango** | -40°C a 85°C | 0.0V - 5.0V |
| **Componente dominio** | VariacionSenoidal | (No aplica) |
| **Panel Gráfico** | ✅ Sí (pyqtgraph) | ❌ No |
| **Paneles MVC** | 4 (Estado, Control, Gráfico, Conexión) | 3 (Estado, Control, Conexión) |
| **Control UI** | Sliders + Radio (Manual/Auto) | Solo Slider |
| **Arquitectura** | MVC + Factory/Coordinator | MVC + Factory/Coordinator |
| **Tests** | 283 | 275 |
| **Coverage** | ~95% | 96% |
| **Pylint** | 9.52 | 9.94 |
| **CC** | 1.36 | 1.40 |
| **MI** | 70.10 | 80.98 |

**Conclusión:** Ambos simuladores comparten la misma arquitectura base (MVC + Factory/Coordinator), con el simulador de batería siendo más simple al no tener modo automático ni gráfico. El simulador de batería tiene mejores métricas de calidad (Pylint 9.94, MI 80.98).

---

## Decisiones de Diseño

### ¿Por qué solo modo manual sin variación automática?

**Alternativas consideradas:**

1. **Modo automático con variación senoidal** - Similar al simulador_temperatura
2. **Modo manual con slider** - Solo control directo del usuario (seleccionada)
3. **Modo híbrido** - Manual + patrones de descarga predefinidos

**Decisión:** Opción 2 - Solo modo manual con slider

**Justificación:**

- **Naturaleza del sensor**: El voltaje de batería cambia lentamente en el sistema real (horas/días, no segundos)
- **Uso en testing**: Los casos de prueba requieren voltajes específicos controlados (batería llena 5.0V, media 3.5V, baja 2.8V)
- **Simplicidad**: No se requiere simular patrones de descarga complejos para validar el termostato
- **Consistencia con objetivo**: El simulador solo necesita probar umbrales de alerta, no dinámicas de batería

**Trade-offs:**

- ✅ **Ventajas**: Más simple (menos código), control preciso de voltaje, sin clase VariacionSenoidal
- ⚠️ **Desventajas**: No simula descarga realista de batería (no es necesario para este sistema)

```mermaid
graph LR
    A[Usuario] -->|mueve slider| B[ControlPanelControlador]
    B -->|voltaje_cambiado| C[GeneradorBateria]
    C -->|set_voltaje| D[_voltaje_actual]
    C -->|valor_generado| E[ServicioEnvio]
    E -->|TCP :11000| F[ISSE_Termostato]

    style A fill:#e1f5e1
    style B fill:#fff4e1
    style C fill:#e1f5e1
    style D fill:#e8e8e8
    style E fill:#fff4e1
    style F fill:#e1e8f5
```

---

### ¿Por qué no incluir panel gráfico?

**Alternativas consideradas:**

1. **Con panel gráfico pyqtgraph** - Similar al simulador_temperatura
2. **Sin panel gráfico** - Solo valores numéricos (seleccionada)
3. **Gráfico simple de barra** - Indicador visual sin historial

**Decisión:** Opción 2 - Sin panel gráfico

**Justificación:**

- **Voltaje estático**: En modo manual, el voltaje no cambia hasta que el usuario mueve el slider
- **Sin valor histórico**: No hay variación temporal que justifique una gráfica de tendencia
- **Feedback suficiente**: El label numérico ("4.20 V") es más preciso y útil que una visualización gráfica
- **Economía de recursos**: Menos dependencias (no requiere pyqtgraph), UI más ligera

**Trade-offs:**

- ✅ **Ventajas**: UI más simple, sin dependencia pyqtgraph, menor consumo de recursos
- ⚠️ **Desventajas**: Sin validación visual de valores (no es necesario para voltaje estático)

```mermaid
flowchart TB
    subgraph "Simulador Temperatura"
        T1[Panel Control<br/>Slider + Radio]
        T2[Panel Gráfico<br/>pyqtgraph]
        T3[Modo Automático<br/>Variación Senoidal]
        T1 --> T2
        T3 --> T2
    end

    subgraph "Simulador Batería"
        B1[Panel Control<br/>Solo Slider]
        B2[Sin Panel Gráfico]
        B3[Solo Modo Manual]
        B1 --> B2
        B3 --> B2
    end

    style T2 fill:#e1f5e1
    style B2 fill:#ffe1e1
    style T3 fill:#e1f5e1
    style B3 fill:#fff4e1
```

---

### ¿Por qué separar GeneradorBateria de ServicioEnvio?

**Alternativas consideradas:**

1. **Clase única SimuladorBateria** - Genera y envía en un solo componente
2. **Separación en capas** - Generador en dominio, ServicioEnvio en comunicación (seleccionada)

**Decisión:** Opción 2 - Separación en capas (siguiendo patrón de temperatura)

**Justificación:**

- **Consistencia arquitectónica**: Mismo patrón que simulador_temperatura facilita mantenimiento
- **Testing aislado**: Generador se prueba sin red (96% coverage)
- **Adherencia a SRP**: Generador solo gestiona voltaje, ServicioEnvio solo envía
- **Reutilización**: ServicioEnvio podría usarse con otros generadores futuros

**Trade-offs:**

- ✅ **Ventajas**: Alta testabilidad, bajo acoplamiento, consistencia con temperatura
- ⚠️ **Desventajas**: Mayor complejidad estructural que una clase única (justificado por testing)

```mermaid
graph TB
    subgraph Dominio["Dominio (Lógica Pura)"]
        Gen[GeneradorBateria<br/>_voltaje_actual: float<br/>set_voltaje<br/>generar_valor]
    end

    subgraph Comunicacion["Comunicación (Networking)"]
        Srv[ServicioEnvioBateria<br/>_generador<br/>_cliente<br/>iniciar/detener]
        Cli[ClienteBateria<br/>_host, _port<br/>enviar_voltaje]
    end

    Gen -->|valor_generado| Srv
    Srv --> Cli
    Cli -->|TCP :11000| RPi[ISSE_Termostato]

    style Dominio fill:#e1f5e1,stroke:#333
    style Comunicacion fill:#fff4e1,stroke:#333
    style Gen fill:#e8e8e8
    style Srv fill:#e8e8e8
    style Cli fill:#e8e8e8
    style RPi fill:#e1e8f5,stroke:#333,stroke-width:2px
```

---

### ¿Por qué patrón Factory + Coordinator idéntico a temperatura?

**Alternativas consideradas:**

1. **Creación directa en run.py** - Instanciar componentes sin abstracción
2. **Solo Factory** - Factory sin Coordinator, señales en constructor
3. **Factory + Coordinator** - Separar creación de orquestación (seleccionada)

**Decisión:** Opción 3 - Factory + Coordinator (arquitectura de referencia)

**Justificación:**

- **Arquitectura de referencia**: Documentado en ADR-005 como patrón estándar del proyecto
- **Reutilización de concepto**: Mismo patrón mental para todos los simuladores
- **Testabilidad**: Factory facilita mocking, Coordinator centraliza señales
- **Mantenibilidad**: Cambios en orquestación solo afectan a Coordinator

**Trade-offs:**

- ✅ **Ventajas**: Consistencia entre productos, alta testabilidad, bajo acoplamiento
- ⚠️ **Desventajas**: Dos clases adicionales (overhead aceptable para 3 paneles MVC)

```mermaid
classDiagram
    class ComponenteFactory {
        -_config: ConfigSimuladorBateria
        +crear_generador() GeneradorBateria
        +crear_cliente(host, port) ClienteBateria
        +crear_servicio(gen, cli) ServicioEnvio
        +crear_controladores() dict
    }

    class SimuladorCoordinator {
        -_generador: GeneradorBateria
        -_servicio: ServicioEnvio
        -_ctrl_estado
        -_ctrl_control
        -_ctrl_conexion
        +set_servicio(servicio)
        <<signal>> conexion_solicitada()
        <<signal>> desconexion_solicitada()
    }

    ComponenteFactory --> GeneradorBateria : crea
    ComponenteFactory --> ClienteBateria : crea
    ComponenteFactory --> ServicioEnvio : crea
    ComponenteFactory --> Controladores : crea

    SimuladorCoordinator ..> GeneradorBateria : conecta señales
    SimuladorCoordinator ..> ServicioEnvio : conecta señales
    SimuladorCoordinator ..> Controladores : conecta señales

    note for ComponenteFactory "Centraliza creación\ncon config consistente"
    note for SimuladorCoordinator "Centraliza orquestación\nde señales PyQt"
```

---

## Referencias

- [ESPECIFICACION_COMUNICACIONES.md](../../docs/ESPECIFICACION_COMUNICACIONES.md)
- [ADR-001: Separación Socket Clients](../../docs/ADR-001-separacion-socket-clients.md)
- [Reporte de Calidad de Diseño](reporte_calidad_diseno.md)
- [Plan de Tests Unitarios](plan_tests_unitarios.md)

---

**Versión:** 1.0
**Fecha:** 2026-01-16
**Estado:** Pre-release (Ready for v1.0)
