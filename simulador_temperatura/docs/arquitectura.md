# Arquitectura del Simulador de Temperatura

## Visión General

El Simulador de Temperatura es un cliente TCP que genera valores de temperatura simulados y los envía al servidor ISSE_Termostato en el puerto 12000.

```
┌─────────────────────────────────────────────────────────────────┐
│  Simulador de Temperatura (PyQt6)                               │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ Configuracion│───▶│   Dominio    │───▶│   Comunicacion    │  │
│  │             │    │              │    │                   │  │
│  │ ConfigManager│    │ Generador    │    │ ClienteTemperatura│  │
│  │             │    │ Temperatura  │    │                   │  │
│  └─────────────┘    └──────────────┘    └─────────┬─────────┘  │
│                                                   │             │
└───────────────────────────────────────────────────┼─────────────┘
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
├── app/
│   ├── configuracion/          # Capa de configuración
│   │   ├── config.py           # ConfigManager (Singleton)
│   │   └── constantes.py       # Valores por defecto
│   │
│   ├── dominio/                # Capa de lógica de negocio
│   │   ├── estado_temperatura.py    # Modelo de datos
│   │   ├── variacion_senoidal.py    # Algoritmo de variación
│   │   └── generador_temperatura.py # Generador de valores
│   │
│   └── comunicacion/           # Capa de comunicación TCP
│       ├── cliente_temperatura.py   # Cliente TCP
│       └── servicio_envio.py        # Integración gen+cliente
│
├── tests/                      # Tests unitarios
└── docs/                       # Documentación
```

---

## Diagrama de Clases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURACION                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────┐      ┌─────────────────────────────────┐  │
│  │ ConfigSimuladorTemperatura│      │        ConfigManager            │  │
│  │ <<dataclass, frozen>>   │      │        <<Singleton>>            │  │
│  ├─────────────────────────┤      ├─────────────────────────────────┤  │
│  │ + ip_raspberry: str     │      │ - _instance: ConfigManager      │  │
│  │ + puerto: int           │      │ - _config: ConfigSimulador...   │  │
│  │ + intervalo_envio_ms: int│◀────│                                 │  │
│  │ + temperatura_minima: float│    ├─────────────────────────────────┤  │
│  │ + temperatura_maxima: float│    │ + obtener_instancia(): ConfigMgr│  │
│  │ + temperatura_inicial: float│   │ + cargar(): ConfigSimulador...  │  │
│  │ + variacion_amplitud: float│    │ + config: ConfigSimulador...    │  │
│  │ + variacion_periodo: float│     └─────────────────────────────────┘  │
│  ├─────────────────────────┤                                            │
│  │ + desde_defaults()      │                                            │
│  └─────────────────────────┘                                            │
└─────────────────────────────────────────────────────────────────────────┘

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
│  │ + to_string(): str      │      │ + temperatura_maxima: float     │  │
│  │ + validar_rango(): None │      │ + temperatura_minima: float     │  │
│  └─────────────────────────┘      └─────────────────────────────────┘  │
│            ▲                                    ▲                       │
│            │                                    │                       │
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
│                        │ + iniciar(): None                         │   │
│                        │ + detener(): None                         │   │
│                        │ + temperatura_actual: float               │   │
│                        │ + modo_manual: bool                       │   │
│                        ├───────────────────────────────────────────┤   │
│                        │ <<signal>> valor_generado(EstadoTemp)     │   │
│                        │ <<signal>> temperatura_cambiada(float)    │   │
│                        └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

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
    │               │ ══════════════════════════════════════════════│
    │               │   Fin Loop                                    │
    │               │ ══════════════════════════════════════════════│
```

---

## Diagrama de Flujo: Generación de Temperatura

```
                    ┌─────────────────┐
                    │     INICIO      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ ¿Modo Manual?   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ SÍ                          │ NO
              ▼                             ▼
    ┌─────────────────────┐    ┌─────────────────────────┐
    │ temp = temperatura  │    │ t = tiempo transcurrido │
    │       _manual       │    └────────────┬────────────┘
    └──────────┬──────────┘                 │
               │                            ▼
               │               ┌─────────────────────────┐
               │               │ temp = T_base +         │
               │               │   A * sin(2π * t / P)   │
               │               └────────────┬────────────┘
               │                            │
               └──────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Crear Estado    │
                    │ Temperatura     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Validar rango   │
                    │ (min, max)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Emitir señales  │
                    │ Qt              │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Retornar Estado │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      FIN        │
                    └─────────────────┘
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

### Flujo de Conexión

```
    Cliente                              Servidor
       │                                    │
       │  1. socket.connect(:12000)         │
       │───────────────────────────────────▶│
       │                                    │
       │  2. send("23.50")                  │
       │───────────────────────────────────▶│
       │                                    │
       │  3. socket.close()                 │
       │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─▶│
       │                                    │
       │                     4. float("23.50")
       │                     5. Procesar temperatura
```

---

## Dependencias entre Módulos

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│    configuracion          dominio              comunicacion         │
│   ┌─────────────┐     ┌─────────────┐      ┌─────────────────┐     │
│   │ConfigManager│────▶│ Generador   │─────▶│ Servicio        │     │
│   │             │     │ Temperatura │      │ EnvioTemperatura│     │
│   └─────────────┘     └──────┬──────┘      └────────┬────────┘     │
│                              │                      │               │
│                              ▼                      ▼               │
│                       ┌─────────────┐      ┌─────────────────┐     │
│                       │ Variacion   │      │ Cliente         │     │
│                       │ Senoidal    │      │ Temperatura     │     │
│                       └─────────────┘      └────────┬────────┘     │
│                              │                      │               │
│                              ▼                      │               │
│                       ┌─────────────┐               │               │
│                       │ Estado      │◀──────────────┘               │
│                       │ Temperatura │                               │
│                       └─────────────┘                               │
│                                                                     │
│   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    │
│                                                                     │
│                         compartido/networking                       │
│                       ┌─────────────────┐                           │
│                       │ Ephemeral       │                           │
│                       │ SocketClient    │                           │
│                       └─────────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
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
| `ServicioEnvioTemperatura` | `servicio_iniciado` | - | Servicio activo |
| `ServicioEnvioTemperatura` | `servicio_detenido` | - | Servicio detenido |

---

## Tickets Relacionados

| Ticket | Descripción | Estado |
|--------|-------------|--------|
| ST-34 | Modelo de datos EstadoTemperatura | Completado |
| ST-35 | Lógica de variación senoidal | Completado |
| ST-37 | Generador de valores de temperatura | Completado |
| ST-38 | Cliente TCP puerto 12000 | Completado |

---

## Referencias

- [ESPECIFICACION_COMUNICACIONES.md](../../docs/ESPECIFICACION_COMUNICACIONES.md)
- [plan_ST-38.md](./plan_ST-38.md)
- [ADR-001: Separación Socket Clients](../../docs/ADR-001-separacion-socket-clients.md)
