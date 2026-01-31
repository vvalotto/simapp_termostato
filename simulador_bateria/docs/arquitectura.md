# Arquitectura del Simulador de Batería

## Visión General

El Simulador de Batería es un cliente TCP que genera valores de voltaje simulados (modo manual por slider) y los envía al servidor ISSE_Termostato en el puerto 11000. Implementa una arquitectura en capas con patrones MVC, Factory y Coordinator.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Simulador de Batería (PyQt6)                                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        run.py (Entry Point)                              ││
│  │                    AplicacionSimulador (Lifecycle)                       ││
│  └──────────────────────────────┬──────────────────────────────────────────┘│
│                                 │                                            │
│     ┌───────────────────────────┼───────────────────────────┐               │
│     │                           │                           │               │
│     ▼                           ▼                           ▼               │
│  ┌──────────┐            ┌─────────────┐            ┌──────────────────┐   │
│  │ Factory  │            │ Coordinator │            │ UIPrincipal      │   │
│  │          │            │             │            │ Compositor       │   │
│  └────┬─────┘            └──────┬──────┘            └────────┬─────────┘   │
│       │                         │                            │              │
│       │    ┌────────────────────┼────────────────────────────┤              │
│       │    │                    │                            │              │
│       ▼    ▼                    ▼                            ▼              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Controladores MVC                               │   │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐               │   │
│  │  │CtrlEstado│  │CtrlControl   │  │CtrlConexion      │               │   │
│  │  └──────────┘  └──────────────┘  └──────────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                    │                    │                           │
│       ▼                    ▼                    ▼                           │
│  ┌───────────┐      ┌───────────┐      ┌────────────────┐                  │
│  │  Dominio  │      │Comunicación│     │  Presentación  │                  │
│  │ Generador │      │ Cliente   │      │  Vistas        │                  │
│  │ Batería   │      │ Servicio  │      │  (PyQt6)       │                  │
│  └───────────┘      └─────┬─────┘      └────────────────┘                  │
│                           │                                                 │
└───────────────────────────┼─────────────────────────────────────────────────┘
                            │ TCP :11000
                            ▼
                  ┌─────────────────────┐
                  │  ISSE_Termostato    │
                  │  (Raspberry Pi)     │
                  └─────────────────────┘
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

```
┌─────────────────────────────────────────────────────────────────┐
│                     ComponenteFactory                            │
│                      (app/factory.py)                            │
├─────────────────────────────────────────────────────────────────┤
│ - _config: ConfigSimuladorBateria                               │
├─────────────────────────────────────────────────────────────────┤
│ + crear_generador() → GeneradorBateria                          │
│ + crear_cliente(host?, port?) → ClienteBateria                  │
│ + crear_servicio(gen, cli) → ServicioEnvioBateria              │
│ + crear_controladores() → dict[str, Controlador]                │
│   └── {'estado', 'control', 'conexion'}                        │
└─────────────────────────────────────────────────────────────────┘
```

**Responsabilidad:** Centraliza la creación de todos los componentes, permitiendo configuración consistente y facilitando testing con mocks.

### 2. Coordinator Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   SimuladorCoordinator                           │
│                    (app/coordinator.py)                          │
├─────────────────────────────────────────────────────────────────┤
│ - _generador: GeneradorBateria                                  │
│ - _servicio: ServicioEnvioBateria                               │
│ - _ctrl_estado: PanelEstadoControlador                          │
│ - _ctrl_control: ControlPanelControlador                        │
│ - _ctrl_conexion: ConexionPanelControlador                      │
├─────────────────────────────────────────────────────────────────┤
│ + set_servicio(servicio): None                                  │
│ + ip_configurada: str                                           │
│ + puerto_configurado: int                                       │
├─────────────────────────────────────────────────────────────────┤
│ <<signal>> conexion_solicitada()                                │
│ <<signal>> desconexion_solicitada()                             │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Conecta señales entre:
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ Generador ←──→ CtrlEstado (actualización voltaje)               │
│ CtrlControl ──→ Generador (cambio voltaje desde slider)         │
│ CtrlConexion ──→ conexion_solicitada/desconexion_solicitada     │
│ Servicio ←──→ CtrlEstado (estado conexión, envíos exitosos)     │
└──────────────────────────────────────────────────────────────────┘
```

**Responsabilidad:** Gestiona todas las conexiones de señales PyQt6 entre componentes, desacoplando la lógica de conexión del ciclo de vida.

**Diferencia con simulador_temperatura:** No hay panel gráfico, el control es solo manual (slider).

### 3. Compositor Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   UIPrincipalCompositor                          │
│               (app/presentacion/ui_compositor.py)                │
├─────────────────────────────────────────────────────────────────┤
│ Recibe controladores ya configurados                            │
│ Solo compone el layout visual                                   │
│ Sin lógica de negocio                                           │
├─────────────────────────────────────────────────────────────────┤
│ Constructor:                                                    │
│   ctrl_estado: PanelEstadoControlador                           │
│   ctrl_control: ControlPanelControlador                         │
│   ctrl_conexion: ConexionPanelControlador                       │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Compone vistas de controladores en layout:
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Panel Estado                             │ │
│  │  Voltaje actual, conexión, envíos exitosos/fallidos        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Panel Control                            │ │
│  │  Slider de voltaje (0.0V - 5.0V)                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Panel Conexión                           │ │
│  │  IP, Puerto, Botón Conectar/Desconectar                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 4. MVC Pattern (Model-View-Controller)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PANEL MVC GENÉRICO                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │     MODELO      │     │      VISTA      │     │   CONTROLADOR   │   │
│  │   (dataclass)   │     │   (QWidget)     │     │   (QObject)     │   │
│  ├─────────────────┤     ├─────────────────┤     ├─────────────────┤   │
│  │ Datos puros     │     │ Solo UI         │     │ Lógica          │   │
│  │ Sin lógica      │◀────│ Sin lógica      │◀────│ Coordina M+V    │   │
│  │ Inmutable       │     │ Emite eventos   │     │ Señales Qt      │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                         │
│  Ejemplo: Panel Estado                                                  │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │PanelEstadoModelo│     │PanelEstadoVista │     │PanelEstado      │   │
│  │                 │     │                 │     │Controlador      │   │
│  │ voltaje         │     │ label_voltaje   │     │                 │   │
│  │ conectado       │     │ led_conexion    │     │ actualizar_     │   │
│  │ envios_exitosos │     │ label_envios    │     │   voltaje()     │   │
│  │ envios_fallidos │     │ label_errores   │     │ registrar_envio │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Diagrama de Clases: Capa de Dominio

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                DOMINIO                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────┐                                            │
│  │   EstadoBateria         │                                            │
│  │     <<dataclass>>       │                                            │
│  ├─────────────────────────┤                                            │
│  │ + voltaje: float        │                                            │
│  │ + timestamp: datetime   │                                            │
│  │ + en_rango: bool        │                                            │
│  ├─────────────────────────┤                                            │
│  │ + to_string(): str      │                                            │
│  │ + validar_rango(min, max): bool                                      │
│  └─────────────────────────┘                                            │
│            ▲                                                            │
│            │                                                            │
│            │           ┌────────────────────────────────────────────┐   │
│            │           │       GeneradorBateria                     │   │
│            │           │           <<QObject>>                      │   │
│            │           ├────────────────────────────────────────────┤   │
│            │           │ - _config: ConfigSimuladorBateria          │   │
│            │           │ - _voltaje_actual: float                   │   │
│            │           │ - _timer: QTimer                           │   │
│            │           ├────────────────────────────────────────────┤   │
│            └───────────│ + generar_valor(): EstadoBateria           │   │
│                        │ + set_voltaje(voltaje): None               │   │
│                        │ + voltaje_actual: float (property)         │   │
│                        │ + iniciar(): None                          │   │
│                        │ + detener(): None                          │   │
│                        ├────────────────────────────────────────────┤   │
│                        │ <<signal>> valor_generado(EstadoBateria)   │   │
│                        │ <<signal>> voltaje_cambiado(float)         │   │
│                        └────────────────────────────────────────────┘   │
│                                                                         │
│  Nota: Solo modo manual (slider), sin variación senoidal               │
└─────────────────────────────────────────────────────────────────────────┘
```

**Diferencias con simulador_temperatura:**
- No hay `VariacionSenoidal` (no hay modo automático)
- Solo control manual por slider
- Rango: 0.0V - 5.0V (voltaje de batería)

---

## Diagrama de Clases: Capa de Comunicación

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             COMUNICACION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────┐                                      │
│  │ EphemeralSocketClient         │  (de compartido/networking)          │
│  │     <<QObject>>               │                                      │
│  ├───────────────────────────────┤                                      │
│  │ + send(data): bool            │                                      │
│  │ + send_async(data): None      │                                      │
│  ├───────────────────────────────┤                                      │
│  │ <<signal>> data_sent()        │                                      │
│  │ <<signal>> error_occurred(str)│                                      │
│  └───────────────────────────────┘                                      │
│               ▲                                                         │
│               │ usa                                                     │
│  ┌────────────┴──────────────────┐    ┌─────────────────────────────┐  │
│  │    ClienteBateria             │    │  ServicioEnvioBateria       │  │
│  │       <<QObject>>             │◀───│        <<QObject>>          │  │
│  ├───────────────────────────────┤    ├─────────────────────────────┤  │
│  │ - _host: str                  │    │ - _generador: Generador...  │  │
│  │ - _port: int                  │    │ - _cliente: ClienteBat...   │  │
│  │ - _cliente: EphemeralSocket..│    │ - _activo: bool             │  │
│  │ - _ultimo_valor: float        │    ├─────────────────────────────┤  │
│  ├───────────────────────────────┤    │ + iniciar(): None           │  │
│  │ + enviar_voltaje(v): bool     │    │ + detener(): None           │  │
│  │ + enviar_voltaje_async(v)     │    │ + activo: bool              │  │
│  │ + enviar_estado(estado): bool │    │ + generador: GeneradorBat..│  │
│  │ + enviar_estado_async(estado) │    │ + cliente: ClienteBateria   │  │
│  │ + host: str                   │    ├─────────────────────────────┤  │
│  │ + port: int                   │    │ <<signal>> envio_exitoso    │  │
│  ├───────────────────────────────┤    │ <<signal>> envio_fallido    │  │
│  │ <<signal>> dato_enviado(float)│    │ <<signal>> servicio_iniciado│  │
│  │ <<signal>> error_conexion(str)│    │ <<signal>> servicio_detenido│  │
│  └───────────────────────────────┘    └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Protocolo:** Puerto 11000, formato `"<voltaje>"` (ej: `"4.20"`), patrón efímero.

---

## Diagrama de Clases: Capa de Presentación (MVC)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTACION - MVC                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Clases Base (app/presentacion/paneles/base.py)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │   ModeloBase    │  │   VistaBase     │  │   ControladorBase       │ │
│  │   <<ABC>>       │  │   <<QWidget>>   │  │   <<QObject>>           │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────────────┤ │
│  │                 │  │ + actualizar()  │  │ - _modelo: ModeloBase   │ │
│  │                 │  │   (modelo): None│  │ - _vista: VistaBase     │ │
│  └─────────────────┘  └─────────────────┘  │ + vista: VistaBase      │ │
│          ▲                    ▲            │ + modelo: ModeloBase    │ │
│          │                    │            └─────────────────────────┘ │
│          │                    │                        ▲                │
│          │                    │                        │                │
│  ┌───────┴────────────────────┴────────────────────────┴───────────┐   │
│  │                    Implementaciones Concretas                    │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  Panel Estado:                                                   │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │PanelEstadoModelo │ │PanelEstadoVista  │ │PanelEstado       │ │   │
│  │  │ voltaje          │ │ lbl_voltaje      │ │Controlador       │ │   │
│  │  │ conectado        │ │ led_conexion     │ │ actualizar_      │ │   │
│  │  │ envios_exitosos  │ │ lbl_envios_ok    │ │   voltaje()      │ │   │
│  │  │ envios_fallidos  │ │ lbl_envios_error │ │ registrar_envio()│ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  │  Panel Control:                                                  │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │ControlPanelModelo│ │ControlPanel      │ │ControlPanel      │ │   │
│  │  │ voltaje          │ │Vista             │ │Controlador       │ │   │
│  │  │ voltaje_minimo   │ │ slider_voltaje   │ │ on_slider_       │ │   │
│  │  │ voltaje_maximo   │ │ spinbox_voltaje  │ │   cambiado()     │ │   │
│  │  │ precision        │ │ lbl_voltaje      │ │ set_voltaje()    │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  │  Panel Conexión:                                                 │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │ConexionPanel     │ │ConexionPanel     │ │ConexionPanel     │ │   │
│  │  │Modelo            │ │Vista             │ │Controlador       │ │   │
│  │  │ ip               │ │ input_ip         │ │ on_conectar()    │ │   │
│  │  │ puerto           │ │ input_puerto     │ │ on_desconectar() │ │   │
│  │  │                  │ │ btn_conectar     │ │ validar_ip()     │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Nota:** No hay panel gráfico (a diferencia del simulador_temperatura).

---

## Diagrama de Secuencia: Inicio de Aplicación

```
┌────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│  main  │  │ Factory │  │Coordinator│ │Compositor │  │Controllers│ │  Dominio │
└───┬────┘  └────┬────┘  └────┬─────┘  └─────┬─────┘  └─────┬─────┘ └─────┬────┘
    │            │            │              │              │             │
    │ crear()    │            │              │              │             │
    │───────────▶│            │              │              │             │
    │            │            │              │              │             │
    │            │ crear_generador()         │              │             │
    │            │──────────────────────────────────────────────────────▶│
    │            │                           │              │             │
    │            │ crear_cliente()           │              │             │
    │            │──────────────────────────────────────────────────────▶│
    │            │                           │              │             │
    │            │ crear_controladores()     │              │             │
    │            │───────────────────────────────────────▶│             │
    │            │                           │              │             │
    │            │◀────────────── dict{ctrl_estado, ctrl_control, ...}   │
    │            │            │              │              │             │
    │◀───────────│            │              │              │             │
    │            │            │              │              │             │
    │ crear Compositor(controllers)          │              │             │
    │────────────────────────────────────────▶              │             │
    │            │            │              │              │             │
    │            │            │              │ obtener vistas│             │
    │            │            │              │◀─────────────│             │
    │            │            │              │              │             │
    │            │            │              │ componer layout             │
    │            │            │              │──┐           │             │
    │            │            │              │◀─┘           │             │
    │            │            │              │              │             │
    │ crear Coordinator(gen, controllers)    │              │             │
    │────────────────────────▶│              │              │             │
    │            │            │              │              │             │
    │            │            │ conectar señales            │             │
    │            │            │─────────────────────────────▶             │
    │            │            │              │              │             │
    │            │            │ conectar a generador        │             │
    │            │            │──────────────────────────────────────────▶│
    │            │            │              │              │             │
    │◀───────────────────────│              │              │             │
    │            │            │              │              │             │
    │ mostrar()  │            │              │              │             │
    │────────────────────────────────────────▶              │             │
    │            │            │              │              │             │
```

---

## Diagrama de Secuencia: Flujo de Conexión

```
┌────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────┐  ┌─────────┐  ┌──────────┐
│Usuario │  │PanelConex │  │Coordinator│  │AplicacionSim│  │ Factory │  │ Servicio │
└───┬────┘  └─────┬─────┘  └─────┬─────┘  └──────┬──────┘  └────┬────┘  └─────┬────┘
    │             │              │               │              │             │
    │ click       │              │               │              │             │
    │ Conectar    │              │               │              │             │
    │────────────▶│              │               │              │             │
    │             │              │               │              │             │
    │             │ conectar_solicitado()        │              │             │
    │             │─────────────▶│               │              │             │
    │             │              │               │              │             │
    │             │              │ emit conexion_solicitada()   │             │
    │             │              │──────────────▶│              │             │
    │             │              │               │              │             │
    │             │              │               │ obtener ip/puerto          │
    │             │              │◀──────────────│              │             │
    │             │              │               │              │             │
    │             │              │               │ crear_cliente(ip, port)    │
    │             │              │               │─────────────▶│             │
    │             │              │               │              │             │
    │             │              │               │ crear_servicio()           │
    │             │              │               │─────────────▶│             │
    │             │              │               │              │             │
    │             │              │               │◀─────────────│             │
    │             │              │               │              │             │
    │             │              │ set_servicio() │             │             │
    │             │              │◀──────────────│              │             │
    │             │              │               │              │             │
    │             │              │               │ servicio.iniciar()         │
    │             │              │               │────────────────────────────▶
    │             │              │               │              │             │
    │             │              │               │              │  generador.iniciar()
    │             │              │               │              │             │
    │             │              │               │              │  (QTimer periódico)
    │             │              │               │              │             │
```

---

## Diagrama de Secuencia: Envío Automático

```
┌────────┐     ┌──────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
│Servicio│     │Generador │     │ Cliente │     │Ephemeral│    │ISSE_Term.│
│ Envio  │     │ Batería  │     │ Batería │     │ Socket │    │ :11000   │
└───┬────┘     └────┬─────┘     └────┬────┘     └────┬────┘    └────┬─────┘
    │               │                │               │              │
    │  iniciar()    │                │               │              │
    │──────────────▶│                │               │              │
    │               │                │               │              │
    │               │ iniciar()      │               │              │
    │               │ (QTimer.start) │               │              │
    │               │                │               │              │
    │               │ ══════════════════════════════════════════════│
    │               │   Loop: cada intervalo_envio_ms               │
    │               │ ══════════════════════════════════════════════│
    │               │                │               │              │
    │               │──┐             │               │              │
    │               │  │ _on_timer() │               │              │
    │               │◀─┘             │               │              │
    │               │                │               │              │
    │               │ generar_valor()│               │              │
    │               │──┐             │               │              │
    │               │  │ (voltaje actual del slider) │              │
    │               │◀─┘             │               │              │
    │               │                │               │              │
    │  valor_generado(estado)        │               │              │
    │◀──────────────│                │               │              │
    │               │                │               │              │
    │               │  enviar_estado_async(estado)   │              │
    │               │ ──────────────▶│               │              │
    │               │                │               │              │
    │               │                │ send_async()  │              │
    │               │                │──────────────▶│              │
    │               │                │               │              │
    │               │                │               │──┐ connect() │
    │               │                │               │  │ send()    │
    │               │                │               │  │ close()   │
    │               │                │               │◀─┘           │
    │               │                │               │              │
    │               │                │               │   "4.20"     │
    │               │                │               │─────────────▶│
    │               │                │               │              │
    │               │                │  data_sent()  │              │
    │               │                │◀──────────────│              │
    │               │                │               │              │
    │               │ dato_enviado(4.20)             │              │
    │               │◀───────────────│               │              │
    │               │                │               │              │
    │ envio_exitoso(4.20)            │               │              │
    │◀──────────────│                │               │              │
    │               │                │               │              │
```

---

## Diagrama de Secuencia: Control Manual de Voltaje

```
┌────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│Usuario │  │CtrlControl│  │Coordinator│  │Generador │  │CtrlEstado│
└───┬────┘  └─────┬─────┘  └─────┬─────┘  └─────┬────┘  └─────┬────┘
    │             │              │               │             │
    │ mover       │              │               │             │
    │ slider      │              │               │             │
    │────────────▶│              │               │             │
    │             │              │               │             │
    │             │ slider_cambiado(paso)        │             │
    │             │──┐           │               │             │
    │             │  │ paso→voltaje               │             │
    │             │◀─┘           │               │             │
    │             │              │               │             │
    │             │ voltaje_cambiado(4.2)        │             │
    │             │─────────────▶│               │             │
    │             │              │               │             │
    │             │              │ set_voltaje(4.2)            │
    │             │              │──────────────▶│             │
    │             │              │               │             │
    │             │              │               │ voltaje_cambiado(4.2)
    │             │              │               │────────────▶│
    │             │              │               │             │
    │             │              │               │             │ actualizar_voltaje()
    │             │              │               │             │──┐
    │             │              │               │             │◀─┘
    │             │              │               │             │
    │             │              │               │             │ UI: "4.20 V"
    │             │              │               │             │
    │             │              │               │ generar_valor()
    │             │              │               │──┐          │
    │             │              │               │  │ (usa voltaje actual)
    │             │              │               │◀─┘          │
    │             │              │               │             │
```

---

## Protocolo de Comunicación

### Formato del Mensaje

```
┌─────────────────────────────────────────────────────────────┐
│  Simulador Batería  ───▶  ISSE_Termostato (:11000)          │
├─────────────────────────────────────────────────────────────┤
│  Formato:    "<voltaje>"                                    │
│  Ejemplo:    "4.20"  (batería llena)                        │
│              "3.50"  (batería media)                        │
│              "2.80"  (batería baja)                         │
│  Encoding:   UTF-8                                          │
│  Rango:      0.0V - 5.0V (sensor ADC)                       │
│  Patrón:     Efímero (conectar → enviar → cerrar)          │
└─────────────────────────────────────────────────────────────┘
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

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  run.py ────────────────────────────────────────────────────────────┐  │
│     │                                                                │  │
│     ▼                                                                ▼  │
│  ┌─────────────┐     ┌─────────────┐     ┌────────────────────────┐ │  │
│  │   Factory   │────▶│ Coordinator │────▶│   UIPrincipalCompositor│ │  │
│  └──────┬──────┘     └──────┬──────┘     └────────────────────────┘ │  │
│         │                   │                                        │  │
│         ▼                   ▼                                        │  │
│  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │              Controladores MVC (paneles/)                    │    │  │
│  │  ┌──────────┐ ┌───────────┐ ┌───────────────┐               │    │  │
│  │  │CtrlEstado│ │CtrlControl│ │CtrlConexion   │               │    │  │
│  │  └────┬─────┘ └─────┬─────┘ └──────┬────────┘               │    │  │
│  └───────┼─────────────┼──────────────┼────────────────────────┘    │  │
│          │             │              │                             │  │
│          ▼             ▼              ▼                             │  │
│  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │                     Modelos + Vistas MVC                       │  │  │
│  └───────────────────────────────────────────────────────────────┘  │  │
│          │                                                           │  │
│          ▼                                                           │  │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────────┐   │  │
│  │ Configuracion│   │   Dominio   │    │    Comunicacion       │   │  │
│  │             │───▶│ Generador   │───▶│ ServicioEnvio         │   │  │
│  │ ConfigManager│   │ Bateria     │    │ ClienteBateria        │   │  │
│  └─────────────┘    └─────────────┘    └───────────┬───────────┘   │  │
│                                                    │                │  │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─ ─ ─ ┘  │
│                                                    │                    │
│                      compartido/networking         │                    │
│                    ┌─────────────────┐             │                    │
│                    │ Ephemeral       │◀────────────┘                    │
│                    │ SocketClient    │                                  │
│                    └─────────────────┘                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
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

## Referencias

- [ESPECIFICACION_COMUNICACIONES.md](../../docs/ESPECIFICACION_COMUNICACIONES.md)
- [ADR-001: Separación Socket Clients](../../docs/ADR-001-separacion-socket-clients.md)
- [Reporte de Calidad de Diseño](reporte_calidad_diseno.md)
- [Plan de Tests Unitarios](plan_tests_unitarios.md)

---

**Versión:** 1.0
**Fecha:** 2026-01-16
**Estado:** Pre-release (Ready for v1.0)
