# Plan de Implementación ST-39, ST-40, ST-41

## Interfaz PyQt6 del Simulador de Temperatura

**Epic:** ST-31 - Simulador de Temperatura
**Estado:** Por hacer
**Branch:** `development/Simulador-de-temperatura-UI`
**Prioridad:** Medium

---

## Tickets Incluidos

| Ticket | Historia de Usuario | Descripción |
|--------|---------------------|-------------|
| ST-39 | HU-2.8 | Widget control de temperatura |
| ST-40 | HU-2.9 | Gráfico de temperatura en tiempo real |
| ST-41 | HU-2.10 | Interfaz principal PyQt6 |

**Justificación de agrupación:** Los tres tickets están fuertemente acoplados - ST-41 integra los widgets de ST-39 y ST-40. Desarrollarlos juntos evita fricciones de integración y permite iterar sobre el diseño de forma cohesiva.

---

## ST-39: Widget Control de Temperatura

### Descripción

Como usuario, quiero tener controles para ajustar los parámetros de simulación de temperatura.

### Criterios de Aceptación

- [ ] Widget `ControlTemperatura` en `app/presentacion/`
- [ ] Slider para temperatura base (rango configurable)
- [ ] Slider para amplitud de variación senoidal
- [ ] Slider para periodo del ciclo
- [ ] Selector modo: Automático / Manual
- [ ] En modo Manual: slider directo de temperatura
- [ ] Señales para notificar cambios de parámetros
- [ ] Estilo visual consistente con dark_theme.qss

### Diseño Técnico

```
ControlTemperatura (QWidget)
    │
    ├── QComboBox: selector de modo (Automático/Manual)
    │
    ├── Panel Modo Automático (QGroupBox)
    │   ├── QSlider + QLabel: temperatura_base (-10°C a 50°C)
    │   ├── QSlider + QLabel: amplitud (0°C a 20°C)
    │   └── QSlider + QLabel: periodo (10s a 300s)
    │
    └── Panel Modo Manual (QGroupBox)
        └── QSlider + QLabel: temperatura (-10°C a 50°C)
```

### Señales Qt

| Señal | Parámetros | Descripción |
|-------|------------|-------------|
| `modo_cambiado` | `bool` | True=manual, False=automático |
| `temperatura_manual_cambiada` | `float` | Nueva temperatura en modo manual |
| `parametros_automatico_cambiados` | `float, float, float` | base, amplitud, periodo |

### Archivo

`simulador_temperatura/app/presentacion/control_temperatura.py`

---

## ST-40: Gráfico de Temperatura en Tiempo Real

### Descripción

Como usuario, quiero ver un gráfico de la temperatura en tiempo real para visualizar el comportamiento histórico durante la simulación.

### Criterios de Aceptación

- [ ] Widget `GraficoTemperatura` en `app/presentacion/`
- [ ] Usar pyqtgraph para renderizado eficiente
- [ ] Eje X: tiempo (últimos N segundos configurable)
- [ ] Eje Y: temperatura (rango configurable, ej: -10°C a 50°C)
- [ ] Línea de temperatura actual en tiempo real
- [ ] Líneas horizontales de referencia: TEMP_MIN, TEMP_MAX
- [ ] Método `add_punto(timestamp, temperatura)`
- [ ] Buffer circular para limitar uso de memoria
- [ ] Estilo visual oscuro consistente con dark_theme.qss
- [ ] Actualización fluida sin parpadeo

### Diseño Técnico

```
GraficoTemperatura (QWidget)
    │
    ├── PlotWidget (pyqtgraph)
    │   ├── PlotCurveItem: línea de temperatura
    │   ├── InfiniteLine: TEMP_MIN (horizontal, rojo)
    │   └── InfiniteLine: TEMP_MAX (horizontal, rojo)
    │
    ├── Buffer circular (collections.deque)
    │   ├── timestamps: deque(maxlen=N)
    │   └── temperaturas: deque(maxlen=N)
    │
    └── Configuración
        ├── ventana_segundos: int (default: 60)
        ├── temp_min_display: float (default: -10)
        └── temp_max_display: float (default: 50)
```

### Métodos Públicos

| Método | Parámetros | Descripción |
|--------|------------|-------------|
| `add_punto` | `timestamp: float, temperatura: float` | Agrega punto al gráfico |
| `clear` | - | Limpia el gráfico |
| `set_limites_referencia` | `temp_min: float, temp_max: float` | Actualiza líneas de referencia |
| `set_ventana_tiempo` | `segundos: int` | Cambia ventana de visualización |

### Estilo Oscuro pyqtgraph

```python
# Configuración de colores para tema oscuro
pg.setConfigOptions(background='#1e1e1e', foreground='#d4d4d4')
plot.getAxis('left').setPen('#d4d4d4')
plot.getAxis('bottom').setPen('#d4d4d4')
curve.setPen(pg.mkPen(color='#4fc3f7', width=2))
```

### Archivo

`simulador_temperatura/app/presentacion/grafico_temperatura.py`

---

## ST-41: Interfaz Principal PyQt6

### Descripción

Como usuario, quiero tener una interfaz gráfica completa del simulador de temperatura para controlar la simulación y visualizar los datos.

### Criterios de Aceptación

- [ ] Clase `UIPrincipal` en `app/presentacion/ui_principal.py`
- [ ] Hereda de QMainWindow
- [ ] Integra `ConfigPanel` (compartido) para IP y puerto
- [ ] Integra `ControlTemperatura` para ajustar parámetros
- [ ] Integra `GraficoTemperatura` para histórico
- [ ] Integra `LogViewer` (compartido) para logs de comunicación
- [ ] Display digital de temperatura actual (estilo LCD)
- [ ] Botón Iniciar/Detener simulación
- [ ] LED de estado de conexión
- [ ] Título de ventana: "Simulador de Temperatura - ISSE"
- [ ] Aplicar dark_theme.qss al iniciar
- [ ] Layout organizado y responsive

### Diseño de Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Simulador de Temperatura - ISSE                        [─][□][×] │
├─────────────────────────────────────────────────────────────┤
│ ┌─── Configuración ───┐  ┌─── Estado ─────────────────────┐ │
│ │ IP: [192.168.1.100] │  │     ┌───────────────┐          │ │
│ │ Puerto: [12000    ] │  │     │   25.5 °C     │  [LED]   │ │
│ │ [Conectar]          │  │     └───────────────┘          │ │
│ └─────────────────────┘  │  [ Iniciar ]  [ Detener ]      │ │
│                          └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─── Control ─────────────────┐ ┌─── Gráfico ────────────┐ │
│ │ Modo: [Automático ▼]        │ │                        │ │
│ │ ─────────────────────────── │ │    /\    /\    /\     │ │
│ │ Temp Base: ══════○══ 20°C   │ │   /  \  /  \  /  \    │ │
│ │ Amplitud:  ═══○═════  5°C   │ │  /    \/    \/    \   │ │
│ │ Periodo:   ════○════ 60s    │ │ ─────────────────────  │ │
│ └─────────────────────────────┘ └────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ┌─── Log de Comunicación ─────────────────────────────────┐ │
│ │ [10:15:32] [INFO] Enviado: 25.5°C                       │ │
│ │ [10:15:33] [INFO] Enviado: 25.7°C                       │ │
│ │ [10:15:34] [WARN] Timeout de conexión                   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Integración de Componentes

| Componente | Origen | Uso |
|------------|--------|-----|
| `ConfigPanel` | `compartido/widgets` | Configuración IP/Puerto |
| `LEDIndicator` | `compartido/widgets` | Estado de conexión |
| `LogViewer` | `compartido/widgets` | Logs de comunicación |
| `ControlTemperatura` | ST-39 (nuevo) | Ajuste de parámetros |
| `GraficoTemperatura` | ST-40 (nuevo) | Visualización histórica |
| `GeneradorTemperatura` | `app/dominio` | Lógica de generación |
| `ServicioEnvioTemperatura` | `app/comunicacion` | Envío TCP |

### Conexión de Señales

```python
# ConfigPanel → Servicio
config_panel.connection_requested.connect(self._on_conectar)
config_panel.disconnection_requested.connect(self._on_desconectar)

# ControlTemperatura → Generador
control.modo_cambiado.connect(self._on_modo_cambiado)
control.temperatura_manual_cambiada.connect(generador.set_temperatura_manual)
control.parametros_automatico_cambiados.connect(self._on_parametros_cambiados)

# Generador → UI
generador.temperatura_cambiada.connect(self._actualizar_display)
generador.temperatura_cambiada.connect(grafico.add_punto)

# ServicioEnvio → LogViewer
servicio.envio_exitoso.connect(lambda t: log_viewer.add_log(f"Enviado: {t}°C", LogLevel.INFO))
servicio.envio_fallido.connect(lambda e: log_viewer.add_log(e, LogLevel.ERROR))
```

### Archivo

`simulador_temperatura/app/presentacion/ui_principal.py`

---

## Pasos de Implementación

### Fase 1: ST-39 - Widget ControlTemperatura

1. **Crear clase base del widget**
   - Archivo: `app/presentacion/control_temperatura.py`
   - Heredar de QWidget
   - Definir señales Qt

2. **Implementar selector de modo**
   - QComboBox con opciones "Automático" / "Manual"
   - Conectar cambio a mostrar/ocultar paneles

3. **Implementar panel modo automático**
   - QGroupBox con sliders para: temp_base, amplitud, periodo
   - Labels que muestren valores actuales
   - Conectar valueChanged a señal

4. **Implementar panel modo manual**
   - QGroupBox con slider de temperatura directa
   - Conectar a señal temperatura_manual_cambiada

5. **Tests unitarios**
   - `tests/test_control_temperatura.py`
   - Probar señales, rangos, cambio de modo

### Fase 2: ST-40 - Widget GraficoTemperatura

1. **Crear widget con pyqtgraph**
   - Archivo: `app/presentacion/grafico_temperatura.py`
   - Configurar PlotWidget con tema oscuro

2. **Implementar buffer circular**
   - Usar `collections.deque` con maxlen
   - Timestamps y temperaturas sincronizados

3. **Implementar líneas de referencia**
   - InfiniteLine horizontal para TEMP_MIN
   - InfiniteLine horizontal para TEMP_MAX

4. **Implementar método add_punto**
   - Agregar datos al buffer
   - Actualizar curva del gráfico
   - Ajustar eje X para ventana de tiempo

5. **Tests unitarios**
   - `tests/test_grafico_temperatura.py`
   - Probar buffer circular, actualización de datos

### Fase 3: ST-41 - Interfaz Principal

1. **Crear clase UIPrincipal**
   - Archivo: `app/presentacion/ui_principal.py`
   - Heredar de QMainWindow
   - Aplicar tema oscuro

2. **Crear layout principal**
   - QVBoxLayout principal
   - Secciones: config/estado, control/gráfico, logs

3. **Integrar widgets compartidos**
   - ConfigPanel, LEDIndicator, LogViewer
   - Configurar labels y parámetros

4. **Integrar widgets nuevos**
   - ControlTemperatura, GraficoTemperatura
   - Display LCD de temperatura

5. **Conectar señales**
   - Flujo de datos entre componentes
   - Actualización de UI en tiempo real

6. **Implementar lógica de control**
   - Botones Iniciar/Detener
   - Gestión de estado de conexión

7. **Actualizar run.py**
   - Instanciar UIPrincipal en lugar de placeholder

8. **Tests unitarios**
   - `tests/test_ui_principal.py`
   - Probar integración y flujo de eventos

### Fase 4: Validación Final

1. **Ejecutar todos los tests**
   ```bash
   cd simulador_temperatura
   pytest tests/ -v
   ```

2. **Verificar quality gates**
   ```bash
   python quality/scripts/calculate_metrics.py app
   python quality/scripts/validate_gates.py quality/reports/quality_*.json
   ```

3. **Prueba manual de integración**
   ```bash
   python run.py
   ```

---

## Dependencias

| Componente | Archivo | Estado |
|------------|---------|--------|
| `ConfigPanel` | `compartido/widgets/config_panel.py` | Existente |
| `LEDIndicator` | `compartido/widgets/led_indicator.py` | Existente |
| `LogViewer` | `compartido/widgets/log_viewer.py` | Existente |
| `GeneradorTemperatura` | `app/dominio/generador_temperatura.py` | Existente (ST-37) |
| `ServicioEnvioTemperatura` | `app/comunicacion/servicio_envio.py` | Existente (ST-38) |
| `ConfigSimuladorTemperatura` | `app/configuracion/config.py` | Existente |
| `pyqtgraph` | `requirements.txt` | Instalado |
| `PyQt6` | `requirements.txt` | Instalado |

---

## Constantes Utilizadas

```python
# Desde app/configuracion/constantes.py
TEMP_ABSOLUTA_MIN = -40.0  # Límite técnico sensor
TEMP_ABSOLUTA_MAX = 125.0  # Límite técnico sensor
DEFAULT_TEMP_MIN = -10.0   # Rango operativo
DEFAULT_TEMP_MAX = 50.0    # Rango operativo
DEFAULT_TEMP_INICIAL = 20.0
DEFAULT_VARIACION_AMPLITUD = 5.0
DEFAULT_VARIACION_PERIODO = 60.0  # segundos
```

---

## Archivos a Crear

| Archivo | Ticket | Descripción |
|---------|--------|-------------|
| `app/presentacion/control_temperatura.py` | ST-39 | Widget de control |
| `app/presentacion/grafico_temperatura.py` | ST-40 | Widget de gráfico |
| `app/presentacion/ui_principal.py` | ST-41 | Ventana principal |
| `tests/test_control_temperatura.py` | ST-39 | Tests del control |
| `tests/test_grafico_temperatura.py` | ST-40 | Tests del gráfico |
| `tests/test_ui_principal.py` | ST-41 | Tests de integración |

---

## Notas

- El tema oscuro se aplica via `compartido/estilos/theme_loader.py`
- pyqtgraph requiere configuración especial para tema oscuro
- Los sliders usan valores enteros internamente, se convierten a float para display
- El buffer circular del gráfico tiene un maxlen de 600 puntos (10 min a 1 sample/seg)
- La ventana de tiempo por defecto es 60 segundos
- El display LCD puede usar `QLCDNumber` o un `QLabel` con fuente monospace grande

---

## Verificación Final

- [ ] Tests ST-39 pasan al 100%
- [ ] Tests ST-40 pasan al 100%
- [ ] Tests ST-41 pasan al 100%
- [ ] Quality gates cumplidos - Calificación: **A**
- [ ] Aplicación ejecuta correctamente con `python run.py`
- [ ] Interfaz responde fluidamente sin lag
- [ ] Gráfico actualiza en tiempo real
- [ ] Conexión TCP funciona correctamente
