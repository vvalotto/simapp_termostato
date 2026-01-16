# Plan de Refactorización: ux_termostato

## Estado
**Propuesto** - Pendiente de implementación

**Fecha:** 2026-01-16
**Autor:** Victor Valotto
**Objetivo:** Refactorizar ux_termostato aplicando arquitectura de referencia MVC + Factory/Coordinator

---

## 1. Contexto

### 1.1 Situación Actual

El simulador `ux_termostato` actualmente tiene una arquitectura más simple que los otros simuladores:

```
ux_termostato/
└── app/
    ├── configuracion/
    ├── datos/
    ├── general/
    └── servicios/
```

**Limitaciones:**
- Sin separación MVC clara
- Sin Factory/Coordinator patterns
- Dificultad para testing unitario
- Menor consistencia con simulador_temperatura y simulador_bateria

### 1.2 Documentos de Referencia

1. **ADR-003**: Arquitectura de referencia MVC + Factory/Coordinator
2. **Prototipo visual**: React/TypeScript en `/Users/victor/Downloads/termostato`
3. **Diseño técnico**: `DISENO_SIMULADORES_UX_DESKTOP.md`

---

## 2. Análisis del Prototipo Visual

### 2.1 Componentes Identificados en el Prototipo

Del código React (`thermostat.tsx`), se identifican estos componentes visuales:

#### Estado de la Aplicación
```typescript
const [isOn, setIsOn] = useState(true);              // Encendido/apagado
const [currentTemp, setCurrentTemp] = useState(22);   // Temperatura actual
const [targetTemp, setTargetTemp] = useState(24);    // Temperatura deseada
const [viewMode, setViewMode] = useState("current"); // Vista actual/deseada
const [sensorFault, setSensorFault] = useState(false); // Falla de sensor
const [lowBattery, setLowBattery] = useState(false);  // Batería baja
```

#### Secciones de UI

1. **Indicadores Superiores** (LEDs de estado)
   - LED Sensor (rojo cuando falla)
   - LED Batería (amarillo cuando baja)

2. **Panel de Estado del Climatizador**
   - Icono Calefacción (🔥 naranja, animado)
   - Icono Reposo (🌬️ verde)
   - Icono Refrigeración (❄️ azul, animado)

3. **Display LCD Principal**
   - Etiqueta: "Temperatura Ambiente" o "Temperatura Deseada"
   - Valor temperatura: Grande, formato X.X °C
   - Estado ERROR cuando hay falla

4. **Botón de Cambio de Vista**
   - Toggle entre vista ambiente/deseada

5. **Controles de Temperatura**
   - Botón BAJAR (azul, con ChevronDown)
   - Botón SUBIR (rojo, con ChevronUp)
   - Rango: 15°C - 35°C
   - Step: 0.5°C

6. **Botón Power**
   - ENCENDER/APAGAR (verde cuando ON)

7. **Información de Estado** (Footer)
   - Modo: Activo/Inactivo
   - Estado: Calentando/Enfriando/Estable

---

## 3. Mapeo a Arquitectura MVC

### 3.1 Identificación de Paneles MVC

Siguiendo el patrón de los simuladores de referencia, `ux_termostato` debe organizarse en estos paneles:

```
presentacion/paneles/
├── indicadores/      # Panel LEDs superiores (sensor, batería)
├── climatizador/     # Panel estado climatizador (calor/reposo/frío)
├── display/          # Panel LCD principal
├── control_temp/     # Panel botones subir/bajar
├── selector_vista/   # Panel botón cambio de vista
├── power/            # Panel botón encendido/apagado
├── estado_footer/    # Panel información inferior
└── conexion/         # Panel configuración IP/puerto
```

### 3.2 Diseño MVC por Panel

#### Panel 1: Indicadores (LEDs de estado)

```python
# modelo.py
@dataclass(frozen=True)
class IndicadoresModelo:
    """Estado de los LEDs superiores."""
    falla_sensor: bool = False
    bateria_baja: bool = False
```

```python
# vista.py
class IndicadoresVista(QWidget):
    """Vista con LEDs circulares."""
    def __init__(self):
        # LED sensor (izquierda)
        self.led_sensor = LedIndicator()  # de compartido/widgets
        self.label_sensor = QLabel("Sensor")

        # LED batería (derecha)
        self.led_bateria = LedIndicator()
        self.label_bateria = QLabel("Batería")

    def actualizar(self, modelo: IndicadoresModelo):
        # Rojo si falla, gris normal
        self.led_sensor.set_estado(
            "error" if modelo.falla_sensor else "inactivo"
        )
        # Amarillo si baja, gris normal
        self.led_bateria.set_estado(
            "warning" if modelo.bateria_baja else "inactivo"
        )
```

```python
# controlador.py
class IndicadoresControlador(ControladorBase):
    """Controla LEDs de estado."""

    def actualizar_sensor(self, hay_falla: bool):
        nuevo_modelo = replace(self._modelo, falla_sensor=hay_falla)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)

    def actualizar_bateria(self, es_baja: bool):
        nuevo_modelo = replace(self._modelo, bateria_baja=es_baja)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)
```

#### Panel 2: Climatizador (Estado calor/reposo/frío)

```python
# modelo.py
@dataclass(frozen=True)
class ClimatizadorModelo:
    """Estado del climatizador."""
    estado: str = "reposo"  # "calentando" | "enfriando" | "reposo" | "apagado"
```

```python
# vista.py
class ClimatizadorVista(QWidget):
    """Vista con 3 iconos: calor, reposo, frío."""
    def __init__(self):
        # Frame contenedor
        self.frame_calor = QFrame()      # Con icono 🔥
        self.frame_reposo = QFrame()     # Con icono 🌬️
        self.frame_frio = QFrame()       # Con icono ❄️

    def actualizar(self, modelo: ClimatizadorModelo):
        # Resetear todos
        self._reset_estilos()

        # Activar el correspondiente
        if modelo.estado == "calentando":
            self._activar_calor()
        elif modelo.estado == "enfriando":
            self._activar_frio()
        elif modelo.estado == "reposo":
            self._activar_reposo()
```

```python
# controlador.py
class ClimatizadorControlador(ControladorBase):
    """Controla estado del climatizador."""

    def actualizar_estado(self, estado: str):
        nuevo_modelo = replace(self._modelo, estado=estado)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)
```

#### Panel 3: Display LCD

```python
# modelo.py
@dataclass(frozen=True)
class DisplayModelo:
    """Estado del display principal."""
    temperatura: float = 0.0
    modo_vista: str = "ambiente"  # "ambiente" | "deseada"
    encendido: bool = True
    error_sensor: bool = False
```

```python
# vista.py
class DisplayVista(QWidget):
    """Display LCD tipo termostato."""
    def __init__(self):
        # Fondo verde oscuro simulando LCD
        self.setStyleSheet("""
            background-color: #065f46;
            border: 2px solid #047857;
            border-radius: 12px;
        """)

        self.label_modo = QLabel("Temperatura Ambiente")
        self.label_temp = QLabel("22.5")  # Fuente grande
        self.label_unidad = QLabel("°C")
        self.label_error = QLabel("ERROR")  # Oculto por defecto

    def actualizar(self, modelo: DisplayModelo):
        if not modelo.encendido:
            self.label_temp.setText("---")
            self.label_modo.setText("APAGADO")
        elif modelo.error_sensor:
            self.label_temp.setVisible(False)
            self.label_error.setVisible(True)
        else:
            self.label_temp.setText(f"{modelo.temperatura:.1f}")
            etiqueta = "Temperatura Ambiente" if modelo.modo_vista == "ambiente" else "Temperatura Deseada"
            self.label_modo.setText(etiqueta)
```

```python
# controlador.py
class DisplayControlador(ControladorBase):
    """Controla display LCD."""

    def actualizar_temperatura(self, temp: float):
        nuevo_modelo = replace(self._modelo, temperatura=temp)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)

    def cambiar_modo_vista(self, modo: str):
        nuevo_modelo = replace(self._modelo, modo_vista=modo)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)

    def set_encendido(self, encendido: bool):
        nuevo_modelo = replace(self._modelo, encendido=encendido)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)
```

#### Panel 4: Control Temperatura (Botones ▲/▼)

```python
# modelo.py
@dataclass(frozen=True)
class ControlTempModelo:
    """Estado de controles de temperatura."""
    habilitado: bool = True
    temp_deseada: float = 24.0
    temp_minima: float = 15.0
    temp_maxima: float = 35.0
    paso: float = 0.5
```

```python
# vista.py
class ControlTempVista(QWidget):
    """Vista con botones Subir/Bajar."""
    def __init__(self):
        self.btn_bajar = QPushButton("Bajar")
        self.btn_bajar.setIcon(QIcon.fromTheme("go-down"))
        self.btn_bajar.setObjectName("btnBajar")  # Para CSS

        self.btn_subir = QPushButton("Subir")
        self.btn_subir.setIcon(QIcon.fromTheme("go-up"))
        self.btn_subir.setObjectName("btnSubir")  # Para CSS

        # Conectar señales internas
        self.btn_bajar.clicked.connect(lambda: self.bajar_clicked.emit())
        self.btn_subir.clicked.connect(lambda: self.subir_clicked.emit())

    bajar_clicked = pyqtSignal()
    subir_clicked = pyqtSignal()

    def actualizar(self, modelo: ControlTempModelo):
        self.btn_bajar.setEnabled(modelo.habilitado)
        self.btn_subir.setEnabled(modelo.habilitado)
```

```python
# controlador.py
class ControlTempControlador(ControladorBase):
    """Controla botones de temperatura."""

    # Señales de negocio
    temperatura_aumentada = pyqtSignal(float)  # Nueva temp deseada
    temperatura_disminuida = pyqtSignal(float)

    def __init__(self, modelo, vista):
        super().__init__(modelo, vista)
        # Conectar vista → controlador
        self._vista.bajar_clicked.connect(self._on_bajar)
        self._vista.subir_clicked.connect(self._on_subir)

    def _on_bajar(self):
        nuevo_valor = self._modelo.temp_deseada - self._modelo.paso
        if nuevo_valor >= self._modelo.temp_minima:
            nuevo_modelo = replace(self._modelo, temp_deseada=nuevo_valor)
            self._modelo = nuevo_modelo
            self.temperatura_disminuida.emit(nuevo_valor)

    def _on_subir(self):
        nuevo_valor = self._modelo.temp_deseada + self._modelo.paso
        if nuevo_valor <= self._modelo.temp_maxima:
            nuevo_modelo = replace(self._modelo, temp_deseada=nuevo_valor)
            self._modelo = nuevo_modelo
            self.temperatura_aumentada.emit(nuevo_valor)

    def set_habilitado(self, habilitado: bool):
        nuevo_modelo = replace(self._modelo, habilitado=habilitado)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)
```

#### Panel 5: Selector Vista (Botón cambio ambiente/deseada)

```python
# modelo.py
@dataclass(frozen=True)
class SelectorVistaModelo:
    """Estado del selector de vista."""
    modo_actual: str = "ambiente"  # "ambiente" | "deseada"
    habilitado: bool = True
```

```python
# vista.py
class SelectorVistaVista(QWidget):
    """Botón para cambiar vista."""
    def __init__(self):
        self.btn_cambiar = QPushButton("Ver Temperatura Deseada")
        self.btn_cambiar.clicked.connect(lambda: self.cambiar_clicked.emit())

    cambiar_clicked = pyqtSignal()

    def actualizar(self, modelo: SelectorVistaModelo):
        texto = "Ver Temperatura Ambiente" if modelo.modo_actual == "deseada" else "Ver Temperatura Deseada"
        self.btn_cambiar.setText(texto)
        self.btn_cambiar.setEnabled(modelo.habilitado)
```

```python
# controlador.py
class SelectorVistaControlador(ControladorBase):
    """Controla selector de vista."""

    modo_cambiado = pyqtSignal(str)  # Nuevo modo

    def __init__(self, modelo, vista):
        super().__init__(modelo, vista)
        self._vista.cambiar_clicked.connect(self._on_cambiar)

    def _on_cambiar(self):
        nuevo_modo = "deseada" if self._modelo.modo_actual == "ambiente" else "ambiente"
        nuevo_modelo = replace(self._modelo, modo_actual=nuevo_modo)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)
        self.modo_cambiado.emit(nuevo_modo)
```

#### Panel 6: Power (Botón encender/apagar)

```python
# modelo.py
@dataclass(frozen=True)
class PowerModelo:
    """Estado del botón power."""
    encendido: bool = True
```

```python
# vista.py
class PowerVista(QWidget):
    """Botón de encendido/apagado."""
    def __init__(self):
        self.btn_power = QPushButton("APAGAR")
        self.btn_power.setIcon(QIcon.fromTheme("system-shutdown"))
        self.btn_power.clicked.connect(lambda: self.power_clicked.emit())

    power_clicked = pyqtSignal()

    def actualizar(self, modelo: PowerModelo):
        texto = "APAGAR" if modelo.encendido else "ENCENDER"
        self.btn_power.setText(texto)
        # CSS: verde cuando ON, gris cuando OFF
        estado_css = "on" if modelo.encendido else "off"
        self.btn_power.setProperty("powerState", estado_css)
        self.btn_power.style().unpolish(self.btn_power)
        self.btn_power.style().polish(self.btn_power)
```

```python
# controlador.py
class PowerControlador(ControladorBase):
    """Controla botón power."""

    estado_cambiado = pyqtSignal(bool)  # True=encendido, False=apagado

    def __init__(self, modelo, vista):
        super().__init__(modelo, vista)
        self._vista.power_clicked.connect(self._on_toggle)

    def _on_toggle(self):
        nuevo_estado = not self._modelo.encendido
        nuevo_modelo = replace(self._modelo, encendido=nuevo_estado)
        self._modelo = nuevo_modelo
        self._vista.actualizar(nuevo_modelo)
        self.estado_cambiado.emit(nuevo_estado)
```

---

## 4. Capa de Dominio

### 4.1 Modelos de Datos

```python
# app/dominio/estado_termostato.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class EstadoTermostato:
    """
    Estado completo del termostato recibido desde Raspberry Pi.

    Corresponde al JSON recibido por socket en puerto 14001.
    """
    timestamp: int
    temp_actual: float
    temp_deseada: float
    estado_climatizador: str  # "calentando" | "enfriando" | "reposo" | "apagado"
    falla_sensor: bool
    bateria_baja: bool
    nivel_bateria: int  # 0-100
    tiempo_en_estado: int  # segundos

    @classmethod
    def desde_json(cls, data: dict) -> 'EstadoTermostato':
        """Construye desde dict JSON."""
        return cls(
            timestamp=data['timestamp'],
            temp_actual=data['temp_actual'],
            temp_deseada=data['temp_deseada'],
            estado_climatizador=data['estado_climatizador'],
            falla_sensor=data['falla_sensor'],
            bateria_baja=data['bateria_baja'],
            nivel_bateria=data['nivel_bateria'],
            tiempo_en_estado=data['tiempo_en_estado']
        )
```

```python
# app/dominio/comando_termostato.py
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass(frozen=True)
class ComandoTermostato:
    """
    Comando enviado al Raspberry Pi.

    Enviado por socket en puerto 14000.
    """
    comando: str  # "set_temp_deseada" | "power" | "set_modo_display"
    valor: float | str | None = None
    estado: str | None = None
    modo: str | None = None
    timestamp: int = None

    def to_json(self) -> str:
        """Serializa a JSON."""
        data = {"comando": self.comando}
        if self.valor is not None:
            data["valor"] = self.valor
        if self.estado is not None:
            data["estado"] = self.estado
        if self.modo is not None:
            data["modo"] = self.modo
        if self.timestamp is not None:
            data["timestamp"] = self.timestamp
        return json.dumps(data)
```

---

## 5. Capa de Comunicación

### 5.1 Servidor (Recepción de estado desde RPi)

```python
# app/comunicacion/servidor_estado.py
from PyQt6.QtCore import QObject, pyqtSignal
from compartido.networking import BaseSocketServer
from app.dominio.estado_termostato import EstadoTermostato
import json

class ServidorEstado(QObject):
    """
    Servidor que escucha en puerto 14001 para recibir estado del RPi.

    Similar a los simuladores pero en modo servidor.
    """

    estado_recibido = pyqtSignal(EstadoTermostato)
    error_recepcion = pyqtSignal(str)
    servidor_iniciado = pyqtSignal()
    servidor_detenido = pyqtSignal()

    def __init__(self, puerto: int = 14001):
        super().__init__()
        self._servidor = BaseSocketServer(puerto=puerto)
        self._servidor.data_received.connect(self._on_data_received)
        self._activo = False

    def iniciar(self):
        """Inicia el servidor."""
        try:
            self._servidor.start()
            self._activo = True
            self.servidor_iniciado.emit()
        except Exception as e:
            self.error_recepcion.emit(f"Error al iniciar servidor: {e}")

    def detener(self):
        """Detiene el servidor."""
        self._servidor.stop()
        self._activo = False
        self.servidor_detenido.emit()

    def _on_data_received(self, data: str):
        """Procesa datos recibidos."""
        try:
            json_data = json.loads(data)
            estado = EstadoTermostato.desde_json(json_data)
            self.estado_recibido.emit(estado)
        except Exception as e:
            self.error_recepcion.emit(f"Error al parsear JSON: {e}")
```

### 5.2 Cliente (Envío de comandos a RPi)

```python
# app/comunicacion/cliente_comandos.py
from PyQt6.QtCore import QObject, pyqtSignal
from compartido.networking import EphemeralSocketClient
from app.dominio.comando_termostato import ComandoTermostato

class ClienteComandos(QObject):
    """
    Cliente que envía comandos al RPi en puerto 14000.

    Similar a ClienteBateria/ClienteTemperatura.
    """

    comando_enviado = pyqtSignal(str)
    error_envio = pyqtSignal(str)

    def __init__(self, host: str, puerto: int = 14000):
        super().__init__()
        self._cliente = EphemeralSocketClient(host, puerto)
        self._cliente.data_sent.connect(lambda: self.comando_enviado.emit("OK"))
        self._cliente.error_occurred.connect(self.error_envio.emit)

    def enviar_comando(self, comando: ComandoTermostato) -> bool:
        """Envía comando al RPi."""
        mensaje = comando.to_json()
        return self._cliente.send(mensaje)
```

---

## 6. Factory Pattern

```python
# app/factory.py
from app.configuracion.config import ConfigUXTermostato
from app.comunicacion.servidor_estado import ServidorEstado
from app.comunicacion.cliente_comandos import ClienteComandos
from app.presentacion.paneles.indicadores.controlador import IndicadoresControlador
from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo
from app.presentacion.paneles.indicadores.vista import IndicadoresVista
# ... imports de otros paneles

class ComponenteFactoryUX:
    """Factory para crear componentes de ux_termostato."""

    def __init__(self, config: ConfigUXTermostato):
        self._config = config

    def crear_servidor_estado(self) -> ServidorEstado:
        """Crea servidor para recibir estado."""
        return ServidorEstado(puerto=self._config.puerto_recepcion)

    def crear_cliente_comandos(self) -> ClienteComandos:
        """Crea cliente para enviar comandos."""
        return ClienteComandos(
            host=self._config.raspberry_ip,
            puerto=self._config.puerto_control
        )

    def crear_controladores(self) -> dict:
        """Crea todos los controladores MVC."""
        return {
            'indicadores': self._crear_ctrl_indicadores(),
            'climatizador': self._crear_ctrl_climatizador(),
            'display': self._crear_ctrl_display(),
            'control_temp': self._crear_ctrl_control_temp(),
            'selector_vista': self._crear_ctrl_selector_vista(),
            'power': self._crear_ctrl_power(),
            'estado_footer': self._crear_ctrl_estado_footer(),
            'conexion': self._crear_ctrl_conexion(),
        }

    def _crear_ctrl_indicadores(self) -> IndicadoresControlador:
        modelo = IndicadoresModelo()
        vista = IndicadoresVista()
        return IndicadoresControlador(modelo, vista)

    # ... resto de métodos _crear_ctrl_*
```

---

## 7. Coordinator Pattern

```python
# app/coordinator.py
from PyQt6.QtCore import QObject, pyqtSignal
from app.comunicacion.servidor_estado import ServidorEstado
from app.comunicacion.cliente_comandos import ClienteComandos
from app.dominio.estado_termostato import EstadoTermostato
from app.dominio.comando_termostato import ComandoTermostato
import time

class UXCoordinator(QObject):
    """
    Coordinador que conecta señales entre componentes.

    Similar a SimuladorCoordinator pero con servidor + cliente.
    """

    def __init__(self, servidor: ServidorEstado, cliente: ClienteComandos, controladores: dict):
        super().__init__()
        self._servidor = servidor
        self._cliente = cliente
        self._ctrl = controladores
        self._conectar_señales()

    def _conectar_señales(self):
        """Conecta señales entre componentes."""

        # Servidor → Controladores (datos entrantes)
        self._servidor.estado_recibido.connect(self._on_estado_recibido)

        # Controladores → Cliente (comandos salientes)
        self._ctrl['control_temp'].temperatura_aumentada.connect(self._on_temp_aumentada)
        self._ctrl['control_temp'].temperatura_disminuida.connect(self._on_temp_disminuida)
        self._ctrl['selector_vista'].modo_cambiado.connect(self._on_modo_cambiado)
        self._ctrl['power'].estado_cambiado.connect(self._on_power_cambiado)

        # Coordinación entre controladores
        self._ctrl['selector_vista'].modo_cambiado.connect(
            self._ctrl['display'].cambiar_modo_vista
        )
        self._ctrl['power'].estado_cambiado.connect(
            self._ctrl['display'].set_encendido
        )
        self._ctrl['power'].estado_cambiado.connect(
            self._ctrl['control_temp'].set_habilitado
        )

    def _on_estado_recibido(self, estado: EstadoTermostato):
        """Procesa estado recibido del RPi."""
        # Actualizar display
        temp_a_mostrar = estado.temp_actual  # O temp_deseada según modo
        self._ctrl['display'].actualizar_temperatura(temp_a_mostrar)

        # Actualizar indicadores
        self._ctrl['indicadores'].actualizar_sensor(estado.falla_sensor)
        self._ctrl['indicadores'].actualizar_bateria(estado.bateria_baja)

        # Actualizar climatizador
        self._ctrl['climatizador'].actualizar_estado(estado.estado_climatizador)

        # Actualizar footer
        self._ctrl['estado_footer'].actualizar_estado(estado)

    def _on_temp_aumentada(self, nueva_temp: float):
        """Usuario aumentó temperatura deseada."""
        comando = ComandoTermostato(
            comando="set_temp_deseada",
            valor=nueva_temp,
            timestamp=int(time.time())
        )
        self._cliente.enviar_comando(comando)

    def _on_temp_disminuida(self, nueva_temp: float):
        """Usuario disminuyó temperatura deseada."""
        comando = ComandoTermostato(
            comando="set_temp_deseada",
            valor=nueva_temp,
            timestamp=int(time.time())
        )
        self._cliente.enviar_comando(comando)

    def _on_modo_cambiado(self, modo: str):
        """Usuario cambió vista ambiente/deseada."""
        comando = ComandoTermostato(
            comando="set_modo_display",
            modo=modo,
            timestamp=int(time.time())
        )
        self._cliente.enviar_comando(comando)

    def _on_power_cambiado(self, encendido: bool):
        """Usuario cambió encendido/apagado."""
        comando = ComandoTermostato(
            comando="power",
            estado="on" if encendido else "off",
            timestamp=int(time.time())
        )
        self._cliente.enviar_comando(comando)
```

---

## 8. Compositor Pattern

```python
# app/presentacion/ui_compositor.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout

class UIUXCompositor(QMainWindow):
    """
    Compositor que ensambla todos los paneles.

    Similar a UIPrincipalCompositor de los simuladores.
    """

    def __init__(self, controladores: dict):
        super().__init__()
        self._controladores = controladores
        self.setWindowTitle("Termostato Inteligente - UX Desktop")
        self.setMinimumSize(400, 700)
        self._componer_layout()

    def _componer_layout(self):
        """Ensambla el layout de la UI."""
        layout_principal = QVBoxLayout()

        # Indicadores superiores (LEDs)
        layout_principal.addWidget(
            self._controladores['indicadores'].vista
        )

        # Estado climatizador
        layout_principal.addWidget(
            self._controladores['climatizador'].vista
        )

        # Display LCD principal
        layout_principal.addWidget(
            self._controladores['display'].vista
        )

        # Botón selector vista
        layout_principal.addWidget(
            self._controladores['selector_vista'].vista
        )

        # Controles temperatura (botones subir/bajar en horizontal)
        layout_controles = QHBoxLayout()
        layout_controles.addWidget(
            self._controladores['control_temp'].vista.btn_bajar
        )
        layout_controles.addWidget(
            self._controladores['control_temp'].vista.btn_subir
        )
        layout_principal.addLayout(layout_controles)

        # Botón power
        layout_principal.addWidget(
            self._controladores['power'].vista
        )

        # Estado footer
        layout_principal.addWidget(
            self._controladores['estado_footer'].vista
        )

        # Panel conexión (opcional, colapsable)
        layout_principal.addWidget(
            self._controladores['conexion'].vista
        )

        # Widget central
        central = QWidget()
        central.setLayout(layout_principal)
        self.setCentralWidget(central)
```

---

## 9. Entry Point (run.py)

```python
# run.py
import sys
from PyQt6.QtWidgets import QApplication
from app.configuracion.config import ConfigManager
from app.factory import ComponenteFactoryUX
from app.coordinator import UXCoordinator
from app.presentacion.ui_compositor import UIUXCompositor
from compartido.estilos import ThemeProvider

def main():
    """Entry point de la aplicación."""
    app = QApplication(sys.argv)

    # Aplicar tema oscuro
    theme = ThemeProvider()
    app.setStyleSheet(theme.get_stylesheet())

    # 1. Cargar configuración
    config_manager = ConfigManager()
    config = config_manager.cargar_config()

    # 2. Factory: crear componentes
    factory = ComponenteFactoryUX(config)
    servidor = factory.crear_servidor_estado()
    cliente = factory.crear_cliente_comandos()
    controladores = factory.crear_controladores()

    # 3. Coordinator: conectar señales
    coordinator = UXCoordinator(servidor, cliente, controladores)

    # 4. Compositor: ensamblar UI
    compositor = UIUXCompositor(controladores)

    # 5. Iniciar servidor
    servidor.iniciar()

    # 6. Mostrar ventana
    compositor.show()

    # 7. Event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

---

## 10. Estructura de Directorios Propuesta

```
ux_termostato/
├── run.py                          # Entry point refactorizado
├── app/
│   ├── factory.py                  # ComponenteFactoryUX
│   ├── coordinator.py              # UXCoordinator
│   │
│   ├── configuracion/
│   │   ├── config.py               # ConfigManager, ConfigUXTermostato
│   │   └── constantes.py
│   │
│   ├── dominio/
│   │   ├── estado_termostato.py    # EstadoTermostato (dataclass)
│   │   └── comando_termostato.py   # ComandoTermostato (dataclass)
│   │
│   ├── comunicacion/
│   │   ├── servidor_estado.py      # ServidorEstado (recibe de RPi)
│   │   └── cliente_comandos.py     # ClienteComandos (envía a RPi)
│   │
│   └── presentacion/
│       ├── ui_compositor.py        # UIUXCompositor
│       │
│       └── paneles/
│           ├── base.py             # Clases base MVC
│           │
│           ├── indicadores/        # Panel LEDs
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           ├── climatizador/       # Panel estado calor/frío/reposo
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           ├── display/            # Panel LCD principal
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           ├── control_temp/       # Panel botones subir/bajar
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           ├── selector_vista/     # Panel botón cambiar vista
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           ├── power/              # Panel botón power
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           ├── estado_footer/      # Panel info inferior
│           │   ├── modelo.py
│           │   ├── vista.py
│           │   └── controlador.py
│           │
│           └── conexion/           # Panel config IP/puerto
│               ├── modelo.py
│               ├── vista.py
│               └── controlador.py
│
├── tests/                          # Tests unitarios
│   ├── conftest.py
│   ├── test_dominio/
│   ├── test_comunicacion/
│   └── test_presentacion/
│
├── quality/                        # Scripts de calidad
│   ├── scripts/
│   └── reports/
│
└── docs/
    └── arquitectura.md
```

---

## 11. Plan de Implementación (Fases)

### Fase 1: Preparación (2 horas)
- [ ] Crear estructura de directorios nueva
- [ ] Implementar clases base MVC en `paneles/base.py`
- [ ] Copiar `compartido/` necesarios (LedIndicator, etc.)
- [ ] Configurar pytest para nueva estructura

### Fase 2: Dominio y Comunicación (3 horas)
- [ ] Implementar `EstadoTermostato` y `ComandoTermostato`
- [ ] Implementar `ServidorEstado` (recepción)
- [ ] Implementar `ClienteComandos` (envío)
- [ ] Tests unitarios de dominio y comunicación

### Fase 3: Paneles MVC - Núcleo (4 horas)
- [ ] Panel Display (MVC completo)
- [ ] Panel Control Temp (MVC completo)
- [ ] Panel Power (MVC completo)
- [ ] Tests unitarios de cada panel

### Fase 4: Paneles MVC - Complementarios (3 horas)
- [ ] Panel Indicadores (MVC completo)
- [ ] Panel Climatizador (MVC completo)
- [ ] Panel Selector Vista (MVC completo)
- [ ] Panel Estado Footer (MVC completo)
- [ ] Tests unitarios

### Fase 5: Factory y Coordinator (2 horas)
- [ ] Implementar `ComponenteFactoryUX`
- [ ] Implementar `UXCoordinator`
- [ ] Conectar señales entre componentes
- [ ] Tests de integración

### Fase 6: Compositor y UI (2 horas)
- [ ] Implementar `UIUXCompositor`
- [ ] Aplicar estilos (QSS)
- [ ] Ajustar layout y spacing
- [ ] Tests de UI con pytest-qt

### Fase 7: Refactorizar run.py (1 hora)
- [ ] Actualizar entry point con nueva arquitectura
- [ ] Manejar argumentos CLI
- [ ] Logging y error handling

### Fase 8: Testing y Validación (3 horas)
- [ ] Coverage > 95%
- [ ] Pylint ≥ 8.0
- [ ] CC ≤ 10, MI > 20
- [ ] Tests de integración end-to-end
- [ ] Pruebas manuales con RPi

### Fase 9: Documentación (2 horas)
- [ ] Actualizar `docs/arquitectura.md`
- [ ] Actualizar CLAUDE.md
- [ ] Crear CHANGELOG.md
- [ ] Manual de usuario

**Total estimado:** ~22 horas

---

## 12. Beneficios Esperados

### 12.1 Calidad de Código
- Arquitectura consistente con otros simuladores
- Separación clara de responsabilidades (MVC)
- Testabilidad: componentes aislados

### 12.2 Mantenibilidad
- Fácil agregar nuevos paneles
- Cambios localizados (bajo ripple effect)
- Código predecible y estructurado

### 12.3 Escalabilidad
- Agregar gráfico histórico: nuevo panel MVC
- Agregar log viewer: nuevo panel MVC
- Multi-termostato: replicar factory/coordinator

### 12.4 Métricas
- Target coverage: 95%+
- Target Pylint: ≥ 8.5
- Target CC: ≤ 5 promedio
- Target MI: > 50

---

## 13. Riesgos y Mitigaciones

### Riesgo 1: Mayor complejidad inicial
**Mitigación:** Documentación exhaustiva, ejemplos en ADR-003, soporte de simuladores existentes

### Riesgo 2: Curva de aprendizaje
**Mitigación:** Implementación incremental, tests desde el inicio, revisiones de código

### Riesgo 3: Over-engineering para UI simple
**Mitigación:** Arquitectura probada en prod, facilita extensiones futuras (gráfico, múltiples termostatos)

### Riesgo 4: Tiempo de desarrollo mayor
**Mitigación:** Reuso de código de `compartido/`, factory/coordinator similares a otros simuladores

---

## 14. Validación de Cumplimiento

Al finalizar, validar que:

- [ ] Estructura de directorios coincide con propuesta
- [ ] Todos los paneles siguen patrón MVC
- [ ] Factory crea todos los componentes
- [ ] Coordinator conecta señales sin acoplamiento
- [ ] Compositor ensambla UI sin lógica
- [ ] Tests > 95% coverage
- [ ] Pylint ≥ 8.0
- [ ] CC ≤ 10, MI > 20
- [ ] Comunicación con RPi funciona
- [ ] UI coincide con prototipo visual

---

## 15. Referencias

- [ADR-003: Arquitectura de Referencia](../../docs/ADR-003-arquitectura-referencia-simuladores.md)
- [simulador_bateria/docs/arquitectura.md](../../simulador_bateria/docs/arquitectura.md)
- [simulador_temperatura/docs/arquitectura.md](../../simulador_temperatura/docs/arquitectura.md)
- [Prototipo visual React](/Users/victor/Downloads/termostato)
- [DISENO_SIMULADORES_UX_DESKTOP.md](/Users/victor/Downloads/termostato/DISENO_SIMULADORES_UX_DESKTOP.md)

---

**Versión:** 1.0
**Fecha:** 2026-01-16
**Estado:** Propuesto - Listo para implementación incremental
