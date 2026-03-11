# Arquitectura del Simulador de Temperatura

## Visión General

El Simulador de Temperatura es un cliente TCP que genera valores de temperatura simulados y los envía al servidor ISSE_Termostato en el puerto 12000. Implementa una arquitectura en capas con patrones MVC, Factory y Coordinator.

```mermaid
flowchart TB
    subgraph SimTemp["Simulador de Temperatura (PyQt6)"]
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
            CtrlGrafico["CtrlGrafico"]
            CtrlConexion["CtrlConexion"]
        end

        Controllers --> Dominio["Dominio<br/>Generador<br/>Variacion"]
        Controllers --> Comunicacion["Comunicación<br/>Cliente<br/>Servicio"]
        Controllers --> Presentacion["Presentación<br/>Vistas<br/>(PyQt6)"]
    end

    Comunicacion -->|TCP :12000| RPi["ISSE_Termostato<br/>(Raspberry Pi)"]

    style SimTemp fill:#f5f5f5,stroke:#333,stroke-width:2px
    style Controllers fill:#e1f5e1,stroke:#333
    style Dominio fill:#e1e8f5,stroke:#333
    style Comunicacion fill:#fff4e1,stroke:#333
    style Presentacion fill:#ffe1e1,stroke:#333
    style RPi fill:#e8e8e8,stroke:#333,stroke-width:2px
```

---

## Estructura de Módulos

```
simulador_temperatura/
├── run.py                          # Entry point + AplicacionSimulador
├── app/
│   ├── factory.py                  # ComponenteFactory
│   ├── coordinator.py              # SimuladorCoordinator
│   │
│   ├── configuracion/              # Capa de configuración
│   │   ├── config.py               # ConfigManager
│   │   └── constantes.py           # Valores por defecto
│   │
│   ├── dominio/                    # Capa de lógica de negocio
│   │   ├── estado_temperatura.py   # Modelo de datos
│   │   ├── variacion_senoidal.py   # Algoritmo de variación
│   │   └── generador_temperatura.py # Generador de valores
│   │
│   ├── comunicacion/               # Capa de comunicación TCP
│   │   ├── interfaces.py           # IClienteTemperatura (typing.Protocol)
│   │   ├── cliente_temperatura.py  # Cliente TCP
│   │   └── servicio_envio.py       # Integración gen+cliente
│   │
│   └── presentacion/               # Capa de presentación (UI)
│       ├── ui_compositor.py        # UIPrincipalCompositor
│       ├── control_temperatura.py  # Widget control (legacy)
│       ├── grafico_temperatura.py  # Widget gráfico (legacy)
│       ├── ui_principal.py         # Ventana principal (legacy)
│       │
│       └── paneles/                # Arquitectura MVC
│           ├── base.py             # ModeloBase, VistaBase, ControladorBase
│           ├── estado/             # Panel Estado
│           │   ├── modelo.py       # EstadoSimulacion
│           │   ├── vista.py        # PanelEstadoVista
│           │   └── controlador.py  # PanelEstadoControlador
│           ├── control_temperatura/ # Panel Control
│           │   ├── modelo.py       # ParametrosControl
│           │   ├── vista.py        # ControlTemperaturaVista
│           │   └── controlador.py  # ControlTemperaturaControlador
│           ├── grafico/            # Panel Gráfico
│           │   ├── modelo.py       # DatosGrafico
│           │   ├── vista.py        # GraficoTemperaturaVista
│           │   └── controlador.py  # GraficoControlador
│           └── conexion/           # Panel Conexión
│               ├── modelo.py       # ConfiguracionConexion
│               ├── vista.py        # PanelConexionVista
│               └── controlador.py  # PanelConexionControlador
│
├── tests/                          # Tests unitarios (283 tests)
├── quality/                        # Scripts de calidad
└── docs/                           # Documentación
```

---

## Patrones de Diseño

### 1. Factory Pattern

```mermaid
classDiagram
    class ComponenteFactory {
        -_config: ConfigSimuladorTemperatura
        +crear_generador() GeneradorTemperatura
        +crear_cliente(host, port) ClienteTemperatura
        +crear_servicio(gen, cli) ServicioEnvioTemperatura
        +crear_controladores() dict~str, Controlador~
    }

    ComponenteFactory --> GeneradorTemperatura : crea
    ComponenteFactory --> ClienteTemperatura : crea
    ComponenteFactory --> ServicioEnvioTemperatura : crea
    ComponenteFactory --> Controladores : crea

    class Controladores {
        estado: PanelEstadoControlador
        control: ControlTemperaturaControlador
        grafico: GraficoControlador
        conexion: PanelConexionControlador
    }

    note for ComponenteFactory "Centraliza creación de componentes\ncon configuración consistente"
```

**Responsabilidad:** Centraliza la creación de todos los componentes, permitiendo configuración consistente y facilitando testing con mocks.

### 2. Coordinator Pattern

```mermaid
classDiagram
    class SimuladorCoordinator {
        -_generador: GeneradorTemperatura
        -_servicio: ServicioEnvioTemperatura
        -_ctrl_estado: PanelEstadoControlador
        -_ctrl_control: ControlTemperaturaControlador
        -_ctrl_grafico: GraficoControlador
        -_ctrl_conexion: PanelConexionControlador
        +set_servicio(servicio) None
        +ip_configurada: str
        +puerto_configurado: int
        <<signal>> conexion_solicitada()
        <<signal>> desconexion_solicitada()
    }

    SimuladorCoordinator ..> GeneradorTemperatura : conecta señales
    SimuladorCoordinator ..> ServicioEnvioTemperatura : conecta señales
    SimuladorCoordinator ..> CtrlEstado : conecta señales
    SimuladorCoordinator ..> CtrlControl : conecta señales
    SimuladorCoordinator ..> CtrlGrafico : conecta señales
    SimuladorCoordinator ..> CtrlConexion : conecta señales

    note for SimuladorCoordinator "Conecta señales entre:\n• Generador ↔ CtrlEstado\n• Generador ↔ CtrlGrafico\n• CtrlControl → Generador\n• CtrlConexion → conexion/desconexion\n• Servicio ↔ CtrlEstado"
```

**Responsabilidad:** Gestiona todas las conexiones de señales PyQt6 entre componentes, desacoplando la lógica de conexión del ciclo de vida.

### 3. Compositor Pattern

```mermaid
flowchart TB
    subgraph Compositor["UIPrincipalCompositor"]
        direction TB
        Info["Recibe controladores configurados<br/>Solo compone layout visual<br/>Sin lógica de negocio"]

        subgraph Params["Constructor Parameters"]
            P1["ctrl_estado: PanelEstadoControlador"]
            P2["ctrl_control: ControlTemperaturaControlador"]
            P3["ctrl_grafico: GraficoControlador"]
            P4["ctrl_conexion: PanelConexionControlador"]
        end
    end

    Compositor ==> Layout

    subgraph Layout["Layout Compuesto"]
        direction TB
        PanelEstado["Panel Estado<br/>(vista del controlador)"]

        subgraph Row2["Fila 2"]
            direction LR
            PanelControl["Panel Control<br/>Temperatura"]
            PanelGrafico["Panel Gráfico"]
        end

        PanelConexion["Panel Conexión"]

        PanelEstado --> Row2
        Row2 --> PanelConexion
    end

    style Compositor fill:#fff4e1,stroke:#333
    style Layout fill:#f5f5f5,stroke:#333,stroke-width:2px
    style PanelEstado fill:#e1f5e1,stroke:#333
    style PanelControl fill:#e1f5e1,stroke:#333
    style PanelGrafico fill:#e1f5e1,stroke:#333
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

    class EstadoSimulacion {
        <<dataclass>>
        +temperatura: float
        +modo: str
        +conectado: bool
    }

    class PanelEstadoVista {
        <<QWidget>>
        +label_temp: QLabel
        +label_modo: QLabel
        +led_conexion: LedIndicator
    }

    class PanelEstadoControlador {
        <<QObject>>
        -_modelo: EstadoSimulacion
        -_vista: PanelEstadoVista
        +actualizar_temperatura(float)
        +set_conectado(bool)
    }

    EstadoSimulacion --|> Modelo : ejemplo
    PanelEstadoVista --|> Vista : ejemplo
    PanelEstadoControlador --|> Controlador : ejemplo

    PanelEstadoControlador --> EstadoSimulacion
    PanelEstadoControlador --> PanelEstadoVista
```

---

## Diagrama de Clases: Capa de Dominio

```mermaid
classDiagram
    class EstadoTemperatura {
        <<dataclass>>
        +temperatura: float
        +timestamp: datetime
        +en_rango: bool
        +to_string() str
        +validar_rango() None
    }

    class VariacionSenoidal {
        -_temperatura_base: float
        -_amplitud: float
        -_periodo_segundos: float
        +calcular_temperatura(t) float
        +actualizar_amplitud(a) None
        +actualizar_periodo(p) None
        +actualizar_base(t) None
    }

    class GeneradorTemperatura {
        <<QObject>>
        -_config: ConfigSimuladorTemperatura
        -_variacion: VariacionSenoidal
        -_modo_manual: bool
        -_temperatura_manual: float
        -_timer: QTimer
        +generar_valor() EstadoTemperatura
        +set_temperatura_manual(temp) None
        +set_modo_automatico() None
        +actualizar_variacion(**kwargs) None
        +iniciar() None
        +detener() None
        <<signal>> valor_generado(EstadoTemperatura)
        <<signal>> temperatura_cambiada(float)
    }

    GeneradorTemperatura --> EstadoTemperatura : genera
    GeneradorTemperatura --> VariacionSenoidal : usa

    note for GeneradorTemperatura "Genera valores de temperatura\nen modo automático (senoidal)\no modo manual (usuario)"
    note for VariacionSenoidal "Implementa variación senoidal\ncon amplitud y periodo configurables"
```

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

    class ClienteTemperatura {
        <<QObject>>
        -_host: str
        -_port: int
        -_cliente: EphemeralSocketClient
        -_ultimo_valor: float
        +enviar_temperatura(t) bool
        +enviar_temperatura_async(t) None
        +enviar_estado(estado) bool
        +enviar_estado_async(estado) None
        +host: str
        +port: int
        <<signal>> dato_enviado(float)
        <<signal>> error_conexion(str)
    }

    class ServicioEnvioTemperatura {
        <<QObject>>
        -_generador: GeneradorTemperatura
        -_cliente: ClienteTemperatura
        -_activo: bool
        +iniciar() None
        +detener() None
        +activo: bool
        <<signal>> envio_exitoso(float)
        <<signal>> envio_fallido(str)
        <<signal>> servicio_iniciado()
        <<signal>> servicio_detenido()
    }

    ClienteTemperatura --> EphemeralSocketClient : usa
    ServicioEnvioTemperatura --> ClienteTemperatura : usa
    ServicioEnvioTemperatura --> GeneradorTemperatura : escucha

    note for EphemeralSocketClient "De compartido/networking\nPatrón: connect→send→close"
    note for ServicioEnvioTemperatura "Integra generador + cliente\nEscucha valor_generado y envía"
```

### Interfaz de comunicación (`interfaces.py`)

Define `IClienteTemperatura` como `typing.Protocol` con `@runtime_checkable`:

- `enviar_temperatura(temperatura: float) -> bool`
- `enviar_estado(estado: EstadoTemperatura) -> bool`

`ComponenteFactory.crear_cliente()` retorna `IClienteTemperatura`, permitiendo
sustitución transparente en tests sin herencia explícita (`ClienteTemperatura`
cumple el protocolo por duck typing).

---

## Diagrama de Clases: Capa de Presentación (MVC)

```mermaid
classDiagram
    class ModeloBase {
        <<ABC>>
        +to_dict() dict
        +from_dict(dict) ModeloBase
    }

    class VistaBase {
        <<QWidget>>
        +actualizar() None
    }

    class ControladorBase {
        <<QObject>>
        -_modelo: ModeloBase
        -_vista: VistaBase
        +vista: VistaBase
    }

    %% Panel Estado
    class EstadoSimulacion {
        <<dataclass>>
        +temperatura: float
        +modo: str
        +conectado: bool
    }

    class PanelEstadoVista {
        <<QWidget>>
        +lbl_temperatura: QLabel
        +lbl_modo: QLabel
        +led_conexion: LedIndicator
    }

    class PanelEstadoControlador {
        <<QObject>>
        +actualizar_temp(float) None
        +set_conectado(bool) None
    }

    %% Panel Control
    class ParametrosControl {
        <<dataclass>>
        +amplitud: float
        +periodo: float
        +temp_base: float
        +modo_manual: bool
    }

    class ControlTemperaturaVista {
        <<QWidget>>
        +sliders: QSlider[]
        +spinboxes: QSpinBox[]
        +radio_buttons: QRadioButton[]
    }

    class ControlTemperaturaControlador {
        <<QObject>>
        +on_amplitud(float) None
        +on_periodo(float) None
        +on_modo(bool) None
    }

    %% Panel Gráfico
    class DatosGrafico {
        <<dataclass>>
        +temperaturas: list~float~
        +tiempos: list~float~
        +max_puntos: int
    }

    class GraficoTemperaturaVista {
        <<QWidget>>
        +plot_widget: PlotWidget
        +curva: PlotCurveItem
    }

    class GraficoControlador {
        <<QObject>>
        +agregar_punto(float, float) None
        +limpiar() None
    }

    %% Herencia
    EstadoSimulacion --|> ModeloBase
    PanelEstadoVista --|> VistaBase
    PanelEstadoControlador --|> ControladorBase

    ParametrosControl --|> ModeloBase
    ControlTemperaturaVista --|> VistaBase
    ControlTemperaturaControlador --|> ControladorBase

    DatosGrafico --|> ModeloBase
    GraficoTemperaturaVista --|> VistaBase
    GraficoControlador --|> ControladorBase

    note for ModeloBase "Clases base en\napp/presentacion/paneles/base.py"
```

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
    Controllers-->>Factory: dict{estado, control, grafico, conexion}
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
    Servicio->>Servicio: generador.iniciar()

    Note over Usuario,Servicio: Generador activo, enviando datos
```

---

## Diagrama de Secuencia: Envío Automático

```mermaid
sequenceDiagram
    participant Servicio as ServicioEnvio
    participant Gen as Generador
    participant Cliente as ClienteTemp
    participant Ephemeral as EphemeralSocket
    participant RPi as ISSE_Term:12000

    Servicio->>Gen: iniciar()
    Gen->>Gen: QTimer.start()

    loop cada intervalo_envio_ms
        Gen->>Gen: _on_timer()
        Gen->>Gen: generar_valor()
        Gen->>Servicio: valor_generado(estado)

        Servicio->>Cliente: enviar_estado_async(estado)
        Cliente->>Ephemeral: send_async()

        Ephemeral->>Ephemeral: connect()
        Ephemeral->>Ephemeral: send()
        Ephemeral->>Ephemeral: close()
        Ephemeral->>RPi: "23.50"

        Ephemeral-->>Cliente: data_sent()
        Cliente-->>Gen: dato_enviado(23.5)
        Gen-->>Servicio: envio_exitoso(23.5)
    end

    Note over Servicio,RPi: Patrón efímero: connect→send→close
```

---

## Protocolo de Comunicación

### Formato del Mensaje

```mermaid
flowchart LR
    A["Simulador<br/>Temperatura"] -->|TCP :12000| B["ISSE_Termostato<br/>(Raspberry Pi)"]

    subgraph Protocolo
        direction TB
        C["Formato: &lt;temperatura&gt;<br/>Ejemplo: '23.50'<br/>Encoding: UTF-8<br/>Patrón: Efímero"]
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
| `GeneradorTemperatura` | `valor_generado` | `EstadoTemperatura` | Nuevo valor generado |
| `GeneradorTemperatura` | `temperatura_cambiada` | `float` | Temperatura cambió |
| `ClienteTemperatura` | `dato_enviado` | `float` | Envío exitoso |
| `ClienteTemperatura` | `error_conexion` | `str` | Error de conexión |
| `ServicioEnvioTemperatura` | `envio_exitoso` | `float` | Dato enviado OK |
| `ServicioEnvioTemperatura` | `envio_fallido` | `str` | Error en envío |
| `SimuladorCoordinator` | `conexion_solicitada` | - | Usuario solicita conectar |
| `SimuladorCoordinator` | `desconexion_solicitada` | - | Usuario solicita desconectar |
| `ControlTemperaturaControlador` | `amplitud_cambiada` | `float` | Amplitud modificada |
| `ControlTemperaturaControlador` | `periodo_cambiado` | `float` | Período modificado |
| `PanelConexionControlador` | `conectar_solicitado` | - | Botón conectar pulsado |
| `PanelConexionControlador` | `desconectar_solicitado` | - | Botón desconectar pulsado |

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
        CtrlGrafico
        CtrlConexion
    end

    Controllers --> ModelosVistas["Modelos + Vistas MVC"]

    ModelosVistas --> Config[Configuracion<br/>ConfigManager]
    ModelosVistas --> Dominio[Dominio<br/>Generador<br/>Variacion]
    ModelosVistas --> Comunicacion[Comunicacion<br/>ServicioEnvio<br/>ClienteTemperatura]

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

## Configuración de calidad (`pyproject.toml`)

```toml
[tool.designreviewer]
max_cbo = 10
max_method_lines = 50
max_lcom = 3
```

Justificación idéntica a `ux_termostato`: vistas PyQt, métodos `_setup_ui` procedurales,
y LCOM inflado por herencia PyQt. Ver `simulador_bateria` para detalles adicionales.

---

## Métricas de Calidad

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Complejidad Ciclomática | 1.36 | ≤ 10 | OK |
| Índice Mantenibilidad | 70.10 | > 20 | OK |
| Pylint Score | 9.52/10 | ≥ 8.0 | OK |
| Tests | 283 | - | Pasando |
| Archivos Python | 36 | - | - |
| Funciones | 319 | - | - |

---

## Tickets de Refactorización

### Fase 1: Eliminar Anti-patrones
| Ticket | Descripción | Estado |
|--------|-------------|--------|
| ST-50 | Crear método público `actualizar_variacion()` | Completado |
| ST-51 | Eliminar acceso a `generador._variacion` | Completado |

### Fase 2: Estructura MVC Base
| Ticket | Descripción | Estado |
|--------|-------------|--------|
| ST-52 | Crear clases base MVC | Completado |
| ST-53 | Migrar Panel Estado a MVC | Completado |
| ST-54 | Tests unitarios MVC | Completado |

### Fase 3: Migrar Paneles
| Ticket | Descripción | Estado |
|--------|-------------|--------|
| ST-55 | Panel Control Temperatura MVC | Completado |
| ST-56 | Panel Gráfico MVC | Completado |
| ST-57 | Panel Conexión MVC | Completado |

### Fase 4: Orquestación
| Ticket | Descripción | Estado |
|--------|-------------|--------|
| ST-58 | UIPrincipal como Compositor | Completado |
| ST-59 | Factory para crear componentes | Completado |
| ST-60 | Coordinator para señales | Completado |
| ST-61 | Simplificar AplicacionSimulador | Completado |

---

## Decisiones de Diseño

### ¿Por qué separar GeneradorTemperatura de ServicioEnvio?

**Alternativas consideradas:**

1. **Clase única SimuladorTemperatura** - Un componente monolítico que genera valores y los envía directamente
2. **Separación en capas** - Generador en dominio, ServicioEnvio en comunicación (seleccionada)

**Decisión:** Opción 2 - Separación en capas con responsabilidades únicas

**Justificación:**

- **Testing aislado**: El generador se puede probar sin dependencias de red
- **Reutilización**: ServicioEnvio puede usarse con otros generadores futuros
- **Adherencia a SRP**: Cada componente tiene una única razón para cambiar
- **Facilita modos de operación**: El modo automático/manual solo afecta al generador, no al envío

**Trade-offs:**

- ✅ **Ventajas**: Mayor testabilidad, bajo acoplamiento, alta cohesión
- ⚠️ **Desventajas**: Mayor complejidad estructural (más clases), coordinación vía signals (overhead mínimo de PyQt)

```mermaid
graph LR
    A[GeneradorTemperatura<br/>Dominio] -->|valor_generado| B[ServicioEnvio<br/>Comunicación]
    B -->|dato_enviado| C[ClienteTemperatura<br/>Comunicación]
    C -->|TCP :12000| D[ISSE_Termostato]

    style A fill:#e1f5e1
    style B fill:#fff4e1
    style C fill:#fff4e1
    style D fill:#e1e8f5
```

---

### ¿Por qué modo automático con variación senoidal?

**Alternativas consideradas:**

1. **Solo modo manual** - Usuario controla temperatura con slider (como simulador_bateria)
2. **Modo automático lineal** - Temperatura incrementa/decrementa linealmente
3. **Modo automático senoidal** - Variación sinusoidal parametrizable (seleccionada)

**Decisión:** Opción 3 - Variación senoidal con parámetros configurables

**Justificación:**

- **Simulación realista**: Las temperaturas ambientales varían de forma continua y cíclica
- **Testing exhaustivo**: Permite probar el comportamiento del termostato en condiciones dinámicas
- **Flexibilidad**: Amplitud y período son configurables en tiempo de ejecución
- **Compatibilidad**: Se mantiene modo manual para casos de prueba específicos

**Trade-offs:**

- ✅ **Ventajas**: Simulación más realista, testing automatizado, cubre más casos de uso
- ⚠️ **Desventajas**: Mayor complejidad que solo modo manual, requiere clase `VariacionSenoidal`

```mermaid
graph TB
    subgraph "Modo Automático"
        A[QTimer] -->|cada intervalo| B[GeneradorTemperatura]
        B -->|usa| C[VariacionSenoidal]
        C -->|calcular_temperatura| D[math.sin]
    end

    subgraph "Modo Manual"
        E[Usuario] -->|set_temperatura_manual| B
    end

    B -->|valor_generado| F[ServicioEnvio]

    style A fill:#e1f5e1
    style C fill:#e1f5e1
    style F fill:#fff4e1
```

---

### ¿Por qué incluir panel gráfico con pyqtgraph?

**Alternativas consideradas:**

1. **Sin visualización gráfica** - Solo valores numéricos (como simulador_bateria)
2. **Gráfico matplotlib embebido** - Integración con matplotlib
3. **Gráfico pyqtgraph** - Biblioteca especializada para PyQt (seleccionada)

**Decisión:** Opción 3 - Panel gráfico con pyqtgraph

**Justificación:**

- **Debugging visual**: Facilita la detección de anomalías en la generación de valores
- **Validación de variación senoidal**: Permite verificar visualmente que la curva es correcta
- **Experiencia de usuario**: Mejora la UX del simulador durante desarrollo y testing
- **Rendimiento**: pyqtgraph es más eficiente que matplotlib para gráficos en tiempo real

**Trade-offs:**

- ✅ **Ventajas**: Mejor debugging, validación visual, integración nativa con PyQt
- ⚠️ **Desventajas**: Dependencia adicional (pyqtgraph), mayor complejidad UI

```mermaid
graph LR
    A[GeneradorTemperatura] -->|valor_generado| B[GraficoControlador]
    B -->|agregar_punto| C[DatosGrafico<br/>Modelo]
    C -->|actualizar| D[GraficoTemperaturaVista<br/>pyqtgraph]

    D -->|renderiza| E[PlotWidget<br/>Curva en tiempo real]

    style A fill:#e1f5e1
    style B fill:#fff4e1
    style C fill:#e8e8e8
    style D fill:#e1e8f5
    style E fill:#e1e8f5
```

---

### ¿Por qué patrón Factory + Coordinator?

**Alternativas consideradas:**

1. **Creación directa en run.py** - Instanciar todos los componentes en el entry point
2. **Dependency Injection manual** - Pasar dependencias en constructores
3. **Factory + Coordinator** - Separar creación de configuración (seleccionada)

**Decisión:** Opción 3 - Factory para creación, Coordinator para orquestación

**Justificación:**

- **Consistencia**: Factory asegura que todos los componentes usen la misma configuración
- **Testabilidad**: Facilita mocking al centralizar la creación
- **Desacoplamiento**: Coordinator conecta señales sin que los componentes se conozcan entre sí
- **Mantenibilidad**: Cambios en configuración se hacen en un solo lugar

**Trade-offs:**

- ✅ **Ventajas**: Configuración consistente, testing simplificado, bajo acoplamiento
- ⚠️ **Desventajas**: Dos clases adicionales (Factory, Coordinator), indirección en creación

```mermaid
graph TB
    subgraph "Factory Pattern"
        F[ComponenteFactory] -->|crear_generador| G[GeneradorTemperatura]
        F -->|crear_cliente| H[ClienteTemperatura]
        F -->|crear_servicio| I[ServicioEnvio]
        F -->|crear_controladores| J[Controladores MVC]
    end

    subgraph "Coordinator Pattern"
        C[SimuladorCoordinator] -.->|conecta señales| G
        C -.->|conecta señales| I
        C -.->|conecta señales| J
    end

    F -.->|provee componentes| C

    style F fill:#fff4e1
    style C fill:#e1f5e1
    style G fill:#e8e8e8
    style H fill:#e8e8e8
    style I fill:#e8e8e8
    style J fill:#e8e8e8
```

---

## Referencias

- [ESPECIFICACION_COMUNICACIONES.md](../../docs/ESPECIFICACION_COMUNICACIONES.md)
- [ADR-001: Separación Socket Clients](../../docs/ADR-001-separacion-socket-clients.md)
- [Informe de Calidad de Diseño](informe_calidad_diseno.md)
