# Arquitectura del Simulador de Temperatura

## Visión General

El Simulador de Temperatura es un cliente TCP que genera valores de temperatura simulados y los envía al servidor ISSE_Termostato en el puerto 12000. Implementa una arquitectura en capas con patrones MVC, Factory y Coordinator.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Simulador de Temperatura (PyQt6)                                            │
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
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│  │  │CtrlEstado│  │CtrlControl   │  │CtrlGrafico│ │CtrlConexion      │ │   │
│  │  └──────────┘  └──────────────┘  └──────────┘  └──────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       │                    │                    │                           │
│       ▼                    ▼                    ▼                           │
│  ┌───────────┐      ┌───────────┐      ┌────────────────┐                  │
│  │  Dominio  │      │Comunicación│     │  Presentación  │                  │
│  │ Generador │      │ Cliente   │      │  Vistas        │                  │
│  │ Variacion │      │ Servicio  │      │  (PyQt6)       │                  │
│  └───────────┘      └─────┬─────┘      └────────────────┘                  │
│                           │                                                 │
└───────────────────────────┼─────────────────────────────────────────────────┘
                            │ TCP :12000
                            ▼
                  ┌─────────────────────┐
                  │  ISSE_Termostato    │
                  │  (Raspberry Pi)     │
                  └─────────────────────┘
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

```
┌─────────────────────────────────────────────────────────────────┐
│                     ComponenteFactory                            │
│                      (app/factory.py)                            │
├─────────────────────────────────────────────────────────────────┤
│ - _config: ConfigSimuladorTemperatura                           │
├─────────────────────────────────────────────────────────────────┤
│ + crear_generador() → GeneradorTemperatura                      │
│ + crear_cliente(host?, port?) → ClienteTemperatura              │
│ + crear_servicio(gen, cli) → ServicioEnvioTemperatura          │
│ + crear_controladores() → dict[str, Controlador]                │
│   └── {'estado', 'control', 'grafico', 'conexion'}             │
└─────────────────────────────────────────────────────────────────┘
```

**Responsabilidad:** Centraliza la creación de todos los componentes, permitiendo configuración consistente y facilitando testing con mocks.

### 2. Coordinator Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                   SimuladorCoordinator                           │
│                    (app/coordinator.py)                          │
├─────────────────────────────────────────────────────────────────┤
│ - _generador: GeneradorTemperatura                              │
│ - _servicio: ServicioEnvioTemperatura                           │
│ - _ctrl_*: Controladores MVC                                    │
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
│ Generador ←──→ CtrlEstado                                        │
│ Generador ←──→ CtrlGrafico                                       │
│ CtrlControl ──→ Generador (parámetros)                           │
│ CtrlConexion ──→ conexion_solicitada/desconexion_solicitada     │
│ Servicio ←──→ CtrlEstado (estado conexión)                       │
└──────────────────────────────────────────────────────────────────┘
```

**Responsabilidad:** Gestiona todas las conexiones de señales PyQt6 entre componentes, desacoplando la lógica de conexión del ciclo de vida.

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
│   ctrl_control: ControlTemperaturaControlador                   │
│   ctrl_grafico: GraficoControlador                              │
│   ctrl_conexion: PanelConexionControlador                       │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Compone vistas de controladores en layout:
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Panel Estado                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────┐ ┌────────────────────────────────┐ │
│  │     Panel Control       │ │        Panel Gráfico           │ │
│  │     Temperatura         │ │                                │ │
│  └─────────────────────────┘ └────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Panel Conexión                           │ │
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
│  │EstadoSimulacion │     │PanelEstadoVista │     │PanelEstado      │   │
│  │                 │     │                 │     │Controlador      │   │
│  │ temperatura     │     │ label_temp      │     │                 │   │
│  │ modo            │     │ label_modo      │     │ actualizar_     │   │
│  │ conectado       │     │ led_conexion    │     │   temperatura() │   │
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
│  ┌─────────────────────────┐      ┌─────────────────────────────────┐  │
│  │   EstadoTemperatura     │      │      VariacionSenoidal          │  │
│  │     <<dataclass>>       │      ├─────────────────────────────────┤  │
│  ├─────────────────────────┤      │ - _temperatura_base: float      │  │
│  │ + temperatura: float    │      │ - _amplitud: float              │  │
│  │ + timestamp: datetime   │      │ - _periodo_segundos: float      │  │
│  │ + en_rango: bool        │      ├─────────────────────────────────┤  │
│  ├─────────────────────────┤      │ + calcular_temperatura(t): float│  │
│  │ + to_string(): str      │      │ + actualizar_amplitud(a): None  │  │
│  │ + validar_rango(): None │      │ + actualizar_periodo(p): None   │  │
│  └─────────────────────────┘      │ + actualizar_base(t): None      │  │
│            ▲                      └─────────────────────────────────┘  │
│            │                                    ▲                       │
│            │           ┌────────────────────────┴──────────────────┐   │
│            │           │       GeneradorTemperatura                │   │
│            │           │           <<QObject>>                     │   │
│            │           ├───────────────────────────────────────────┤   │
│            │           │ - _config: ConfigSimuladorTemperatura     │   │
│            │           │ - _variacion: VariacionSenoidal           │   │
│            │           │ - _modo_manual: bool                      │   │
│            │           │ - _temperatura_manual: float              │   │
│            │           │ - _timer: QTimer                          │   │
│            │           ├───────────────────────────────────────────┤   │
│            └───────────│ + generar_valor(): EstadoTemperatura      │   │
│                        │ + set_temperatura_manual(temp): None      │   │
│                        │ + set_modo_automatico(): None             │   │
│                        │ + actualizar_variacion(**kwargs): None    │   │
│                        │ + iniciar(): None                         │   │
│                        │ + detener(): None                         │   │
│                        ├───────────────────────────────────────────┤   │
│                        │ <<signal>> valor_generado(EstadoTemp)     │   │
│                        │ <<signal>> temperatura_cambiada(float)    │   │
│                        └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

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
│  │    ClienteTemperatura         │    │  ServicioEnvioTemperatura   │  │
│  │       <<QObject>>             │◀───│        <<QObject>>          │  │
│  ├───────────────────────────────┤    ├─────────────────────────────┤  │
│  │ - _host: str                  │    │ - _generador: Generador...  │  │
│  │ - _port: int                  │    │ - _cliente: ClienteTemp...  │  │
│  │ - _cliente: EphemeralSocket..│    │ - _activo: bool             │  │
│  │ - _ultimo_valor: float        │    ├─────────────────────────────┤  │
│  ├───────────────────────────────┤    │ + iniciar(): None           │  │
│  │ + enviar_temperatura(t): bool │    │ + detener(): None           │  │
│  │ + enviar_temperatura_async(t) │    │ + activo: bool              │  │
│  │ + enviar_estado(estado): bool │    ├─────────────────────────────┤  │
│  │ + enviar_estado_async(estado) │    │ <<signal>> envio_exitoso    │  │
│  │ + host: str                   │    │ <<signal>> envio_fallido    │  │
│  │ + port: int                   │    │ <<signal>> servicio_iniciado│  │
│  ├───────────────────────────────┤    │ <<signal>> servicio_detenido│  │
│  │ <<signal>> dato_enviado(float)│    └─────────────────────────────┘  │
│  │ <<signal>> error_conexion(str)│                                      │
│  └───────────────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

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
│  │ + to_dict()     │  │ + actualizar()  │  │ - _modelo: ModeloBase   │ │
│  │ + from_dict()   │  │                 │  │ - _vista: VistaBase     │ │
│  └─────────────────┘  └─────────────────┘  │ + vista: VistaBase      │ │
│          ▲                    ▲            └─────────────────────────┘ │
│          │                    │                        ▲                │
│          │                    │                        │                │
│  ┌───────┴────────────────────┴────────────────────────┴───────────┐   │
│  │                    Implementaciones Concretas                    │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  Panel Estado:                                                   │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │EstadoSimulacion  │ │PanelEstadoVista  │ │PanelEstado       │ │   │
│  │  │ temperatura      │ │ lbl_temperatura  │ │Controlador       │ │   │
│  │  │ modo             │ │ lbl_modo         │ │ actualizar_temp()│ │   │
│  │  │ conectado        │ │ led_conexion     │ │ set_conectado()  │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  │  Panel Control:                                                  │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │ParametrosControl │ │ControlTemp       │ │ControlTemp       │ │   │
│  │  │ amplitud         │ │Vista             │ │Controlador       │ │   │
│  │  │ periodo          │ │ sliders          │ │ on_amplitud()    │ │   │
│  │  │ temp_base        │ │ spinboxes        │ │ on_periodo()     │ │   │
│  │  │ modo_manual      │ │ radio_buttons    │ │ on_modo()        │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  │  Panel Gráfico:                                                  │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │DatosGrafico      │ │GraficoTemp       │ │Grafico           │ │   │
│  │  │ temperaturas[]   │ │Vista             │ │Controlador       │ │   │
│  │  │ tiempos[]        │ │ plot_widget      │ │ agregar_punto()  │ │   │
│  │  │ max_puntos       │ │ curva            │ │ limpiar()        │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  │  Panel Conexión:                                                 │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │ConfigConexion    │ │PanelConexion     │ │PanelConexion     │ │   │
│  │  │ ip               │ │Vista             │ │Controlador       │ │   │
│  │  │ puerto           │ │ input_ip         │ │ on_conectar()    │ │   │
│  │  │ conectado        │ │ input_puerto     │ │ on_desconectar() │ │   │
│  │  │                  │ │ btn_conectar     │ │ validar_ip()     │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

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
```

---

## Diagrama de Secuencia: Envío Automático

```
┌────────┐     ┌──────────┐     ┌─────────┐     ┌────────┐     ┌──────────┐
│Servicio│     │Generador │     │ Cliente │     │Ephemeral│    │ISSE_Term.│
│ Envio  │     │   Temp   │     │  Temp   │     │ Socket │    │ :12000   │
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
    │               │  │             │               │              │
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
    │               │                │               │   "23.50"    │
    │               │                │               │─────────────▶│
    │               │                │               │              │
    │               │                │  data_sent()  │              │
    │               │                │◀──────────────│              │
    │               │                │               │              │
    │               │ dato_enviado(23.5)             │              │
    │               │◀───────────────│               │              │
    │               │                │               │              │
    │ envio_exitoso(23.5)            │               │              │
    │◀──────────────│                │               │              │
    │               │                │               │              │
```

---

## Protocolo de Comunicación

### Formato del Mensaje

```
┌─────────────────────────────────────────────────────────────┐
│  Simulador Temperatura  ───▶  ISSE_Termostato (:12000)      │
├─────────────────────────────────────────────────────────────┤
│  Formato:    "<temperatura>"                                │
│  Ejemplo:    "23.50"                                        │
│  Encoding:   UTF-8                                          │
│  Patrón:     Efímero (conectar → enviar → cerrar)          │
└─────────────────────────────────────────────────────────────┘
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
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────┐  │    │  │
│  │  │CtrlEstado│ │CtrlControl│ │CtrlGrafico│ │CtrlConexion  │  │    │  │
│  │  └────┬─────┘ └─────┬─────┘ └─────┬────┘ └──────┬────────┘  │    │  │
│  └───────┼─────────────┼─────────────┼─────────────┼───────────┘    │  │
│          │             │             │             │                 │  │
│          ▼             ▼             ▼             ▼                 │  │
│  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │                     Modelos + Vistas MVC                       │  │  │
│  └───────────────────────────────────────────────────────────────┘  │  │
│          │                                                           │  │
│          ▼                                                           │  │
│  ┌─────────────┐    ┌─────────────┐    ┌───────────────────────┐   │  │
│  │ Configuracion│   │   Dominio   │    │    Comunicacion       │   │  │
│  │             │───▶│ Generador   │───▶│ ServicioEnvio         │   │  │
│  │ ConfigManager│   │ Variacion   │    │ ClienteTemperatura    │   │  │
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

## Referencias

- [ESPECIFICACION_COMUNICACIONES.md](../../docs/ESPECIFICACION_COMUNICACIONES.md)
- [ADR-001: Separación Socket Clients](../../docs/ADR-001-separacion-socket-clients.md)
- [Informe de Calidad de Diseño](informe_calidad_diseno.md)
