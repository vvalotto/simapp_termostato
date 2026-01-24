# Plan de Implementación - SPRINT 2: Paneles Finales

**Historias:** US-011 + US-015 + US-013 (3 historias en una sesión)
**Puntos:** 8 (3 + 2 + 3)
**Prioridad:** ALTA
**Estado:** 🔲 PENDIENTE

---

## Descripción

Implementar los 3 paneles finales de la UI en una sola sesión:

1. **US-011: SelectorVista** - Toggle ambiente/deseada
2. **US-015: EstadoConexion** - Indicador de conexión con RPi
3. **US-013: Conexion** - Configuración IP/puerto del RPi

**Estrategia:**
- ✅ Implementar los 3 paneles MVC completos (sin tests)
- ✅ Actualizar Factory con métodos de creación
- ✅ Actualizar Coordinator con conexiones de señales
- ✅ Extender ConfigManager para persistencia de IP
- ✅ Crear script de validación visual
- ➡️ Tests unitarios después, de a uno (US-011 → US-015 → US-013)

**Dependencias:**
- ✅ US-020 (EstadoTermostato, Comandos)
- ✅ US-021 (ServidorEstado, ClienteComandos)
- ✅ US-022 (Factory, Coordinator, ConfigUX)

---

## Orden de Implementación

### Fase 1: Paneles MVC (4h - SIN TESTS)

#### 1.1. US-011: Panel SelectorVista (~1h)

**Objetivo:** Toggle entre vista "ambiente" y "deseada"

**Componentes:**
- `app/presentacion/paneles/selector_vista/modelo.py`
- `app/presentacion/paneles/selector_vista/vista.py`
- `app/presentacion/paneles/selector_vista/controlador.py`
- `app/presentacion/paneles/selector_vista/__init__.py`

**Detalles de implementación:**

**SelectorVistaModelo:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SelectorVistaModelo:
    """Modelo del selector de vista (ambiente vs deseada)."""
    modo: str  # "ambiente" o "deseada"
    habilitado: bool = True

    def __post_init__(self):
        # Validar que modo sea válido
        if self.modo not in ["ambiente", "deseada"]:
            raise ValueError(f"Modo inválido: {self.modo}")
```

**SelectorVistaVista:**
```python
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QButtonGroup
from PyQt6.QtCore import Qt

class SelectorVistaVista(QWidget):
    """Vista del selector de vista."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inicializar_ui()

    def _inicializar_ui(self):
        # Layout horizontal
        layout = QHBoxLayout(self)

        # Label
        self._label = QLabel("Vista:")

        # Botones tipo toggle (ButtonGroup para exclusividad)
        self._btn_ambiente = QPushButton("🌡️ Ambiente")
        self._btn_deseada = QPushButton("🎯 Deseada")

        # Configurar como checkable
        self._btn_ambiente.setCheckable(True)
        self._btn_deseada.setCheckable(True)

        # ButtonGroup para exclusividad
        self._grupo = QButtonGroup()
        self._grupo.addButton(self._btn_ambiente)
        self._grupo.addButton(self._btn_deseada)

        # Layout
        layout.addWidget(self._label)
        layout.addWidget(self._btn_ambiente)
        layout.addWidget(self._btn_deseada)
        layout.addStretch()

        # Estilos
        self._aplicar_estilos()

    def _aplicar_estilos(self):
        # Botón ambiente (checked = verde)
        self._btn_ambiente.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #28a745;
                border-color: #28a745;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
            }
        """)

        # Botón deseada (checked = azul)
        self._btn_deseada.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:checked {
                background-color: #007bff;
                border-color: #007bff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
            }
        """)

    def actualizar(self, modelo: SelectorVistaModelo):
        """Actualiza la vista desde el modelo."""
        # Seleccionar botón según modo
        if modelo.modo == "ambiente":
            self._btn_ambiente.setChecked(True)
        else:
            self._btn_deseada.setChecked(True)

        # Habilitar/deshabilitar
        self.setEnabled(modelo.habilitado)

    @property
    def boton_ambiente(self):
        return self._btn_ambiente

    @property
    def boton_deseada(self):
        return self._btn_deseada
```

**SelectorVistaControlador:**
```python
from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import replace
import logging

class SelectorVistaControlador(QObject):
    """Controlador del selector de vista."""

    # Señales
    modo_cambiado = pyqtSignal(str)  # "ambiente" o "deseada"

    def __init__(self, modelo: SelectorVistaModelo, vista: SelectorVistaVista, parent=None):
        super().__init__(parent)
        self._modelo = modelo
        self._vista = vista
        self._logger = logging.getLogger(__name__)

        # Conectar señales
        self._conectar_signals()

        # Inicializar vista
        self._vista.actualizar(self._modelo)

    def _conectar_signals(self):
        """Conecta señales de la vista."""
        self._vista.boton_ambiente.clicked.connect(self._on_ambiente_clicked)
        self._vista.boton_deseada.clicked.connect(self._on_deseada_clicked)

    def _on_ambiente_clicked(self):
        """Handler de click en botón ambiente."""
        if self._modelo.modo != "ambiente":
            self._cambiar_modo("ambiente")

    def _on_deseada_clicked(self):
        """Handler de click en botón deseada."""
        if self._modelo.modo != "deseada":
            self._cambiar_modo("deseada")

    def _cambiar_modo(self, nuevo_modo: str):
        """Cambia el modo y notifica."""
        # Actualizar modelo
        self._modelo = replace(self._modelo, modo=nuevo_modo)

        # Actualizar vista
        self._vista.actualizar(self._modelo)

        # Emitir señal
        self.modo_cambiado.emit(nuevo_modo)
        self._logger.info("Modo cambiado a: %s", nuevo_modo)

    def setEnabled(self, habilitado: bool):
        """Habilita/deshabilita el selector."""
        self._modelo = replace(self._modelo, habilitado=habilitado)
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self):
        return self._modelo
```

**__init__.py:**
```python
"""Panel selector de vista (ambiente/deseada)."""

from .modelo import SelectorVistaModelo
from .vista import SelectorVistaVista
from .controlador import SelectorVistaControlador

__all__ = [
    "SelectorVistaModelo",
    "SelectorVistaVista",
    "SelectorVistaControlador",
]
```

---

#### 1.2. US-015: Panel EstadoConexion (~1h)

**Objetivo:** Indicador visual del estado de conexión con RPi

**Componentes:**
- `app/presentacion/paneles/estado_conexion/modelo.py`
- `app/presentacion/paneles/estado_conexion/vista.py`
- `app/presentacion/paneles/estado_conexion/controlador.py`
- `app/presentacion/paneles/estado_conexion/__init__.py`

**Detalles de implementación:**

**EstadoConexionModelo:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class EstadoConexionModelo:
    """Modelo del estado de conexión."""
    estado: str  # "conectado", "desconectado", "conectando"
    direccion_ip: str = ""

    def __post_init__(self):
        # Validar estado
        if self.estado not in ["conectado", "desconectado", "conectando"]:
            raise ValueError(f"Estado inválido: {self.estado}")
```

**EstadoConexionVista:**
```python
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from compartido.widgets.led_indicator import LedIndicator

class EstadoConexionVista(QWidget):
    """Vista del estado de conexión."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer_pulso = None
        self._inicializar_ui()

    def _inicializar_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Label "Estado:"
        self._label = QLabel("Estado:")
        self._label.setStyleSheet("color: #cccccc; font-weight: bold;")

        # LED indicator
        self._led = LedIndicator()
        self._led.setFixedSize(16, 16)

        # Label texto estado
        self._label_estado = QLabel("Desconectado")
        self._label_estado.setStyleSheet("color: #cccccc;")

        layout.addWidget(self._label)
        layout.addWidget(self._led)
        layout.addWidget(self._label_estado)
        layout.addStretch()

    def actualizar(self, modelo: EstadoConexionModelo):
        """Actualiza la vista desde el modelo."""
        # Detener animación si existe
        self._detener_pulso()

        if modelo.estado == "conectado":
            self._led.set_color("green")
            self._led.set_active(True)
            self._label_estado.setText("Conectado")
            self._label_estado.setStyleSheet("color: #28a745; font-weight: bold;")

        elif modelo.estado == "desconectado":
            self._led.set_color("red")
            self._led.set_active(False)
            self._label_estado.setText("Desconectado")
            self._label_estado.setStyleSheet("color: #dc3545;")

        elif modelo.estado == "conectando":
            self._led.set_color("yellow")
            self._label_estado.setText("Conectando...")
            self._label_estado.setStyleSheet("color: #ffc107;")
            # Iniciar animación pulsante
            self._iniciar_pulso()

    def _iniciar_pulso(self):
        """Inicia animación pulsante."""
        self._pulso_activo = True
        self._timer_pulso = QTimer()
        self._timer_pulso.timeout.connect(self._toggle_pulso)
        self._timer_pulso.start(500)  # 500ms

    def _detener_pulso(self):
        """Detiene animación pulsante."""
        if self._timer_pulso:
            self._timer_pulso.stop()
            self._timer_pulso = None
        self._pulso_activo = False

    def _toggle_pulso(self):
        """Toggle del LED para animación."""
        if hasattr(self, '_pulso_activo') and self._pulso_activo:
            self._led.set_active(not self._led.is_active)
```

**EstadoConexionControlador:**
```python
from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import replace
import logging

class EstadoConexionControlador(QObject):
    """Controlador del estado de conexión."""

    # Señales (para futuro uso)
    estado_cambiado = pyqtSignal(str)

    def __init__(self, modelo: EstadoConexionModelo, vista: EstadoConexionVista, parent=None):
        super().__init__(parent)
        self._modelo = modelo
        self._vista = vista
        self._logger = logging.getLogger(__name__)

        # Inicializar vista
        self._vista.actualizar(self._modelo)

    def actualizar_estado(self, nuevo_estado: str, ip: str = ""):
        """Actualiza el estado de conexión."""
        # Actualizar modelo
        self._modelo = replace(self._modelo, estado=nuevo_estado, direccion_ip=ip)

        # Actualizar vista
        self._vista.actualizar(self._modelo)

        # Emitir señal
        self.estado_cambiado.emit(nuevo_estado)
        self._logger.info("Estado conexión: %s (IP: %s)", nuevo_estado, ip)

    def conexion_establecida(self, direccion: str):
        """Notifica que la conexión fue establecida."""
        self.actualizar_estado("conectado", direccion)

    def conexion_perdida(self, direccion: str = ""):
        """Notifica que la conexión se perdió."""
        self.actualizar_estado("desconectado", direccion)

    def conectando(self):
        """Notifica que se está intentando conectar."""
        self.actualizar_estado("conectando")

    @property
    def modelo(self):
        return self._modelo
```

**__init__.py:**
```python
"""Panel de estado de conexión."""

from .modelo import EstadoConexionModelo
from .vista import EstadoConexionVista
from .controlador import EstadoConexionControlador

__all__ = [
    "EstadoConexionModelo",
    "EstadoConexionVista",
    "EstadoConexionControlador",
]
```

---

#### 1.3. US-013: Panel Conexion (~2h - MÁS COMPLEJO)

**Objetivo:** Configuración de IP/puerto del RPi con validación y persistencia

**Componentes:**
- `app/presentacion/paneles/conexion/modelo.py`
- `app/presentacion/paneles/conexion/vista.py`
- `app/presentacion/paneles/conexion/controlador.py`
- `app/presentacion/paneles/conexion/__init__.py`

**Detalles de implementación:**

**ConexionModelo:**
```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class ConexionModelo:
    """Modelo del panel de conexión."""
    ip: str
    puerto_recv: int
    puerto_send: int
    ip_valida: bool = True
    mensaje_error: str = ""

    def __post_init__(self):
        # Validar puerto recv
        if not (1024 <= self.puerto_recv <= 65535):
            raise ValueError(f"Puerto recv inválido: {self.puerto_recv}")

        # Validar puerto send
        if not (1024 <= self.puerto_send <= 65535):
            raise ValueError(f"Puerto send inválido: {self.puerto_send}")

    @staticmethod
    def validar_ip(ip: str) -> tuple[bool, str]:
        """Valida formato de IP.

        Returns:
            tuple (es_valida, mensaje_error)
        """
        # Regex para IPv4
        patron = r"^(\d{1,3}\.){3}\d{1,3}$"

        if not re.match(patron, ip):
            return False, "Formato inválido (xxx.xxx.xxx.xxx)"

        # Validar rango de octetos
        octetos = ip.split(".")
        for octeto in octetos:
            valor = int(octeto)
            if not (0 <= valor <= 255):
                return False, f"Octeto fuera de rango: {octeto}"

        return True, ""
```

**ConexionVista:**
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

class ConexionVista(QWidget):
    """Vista del panel de conexión."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inicializar_ui()

    def _inicializar_ui(self):
        layout = QVBoxLayout(self)

        # GroupBox
        group = QGroupBox("Configuración de Conexión")
        group_layout = QFormLayout()

        # Campo IP
        self._input_ip = QLineEdit()
        self._input_ip.setPlaceholderText("192.168.1.50")
        self._input_ip.setMaxLength(15)

        # Label de validación
        self._label_validacion = QLabel("")
        self._label_validacion.setStyleSheet("color: #dc3545; font-size: 11px;")

        # Layout IP + validación
        ip_layout = QVBoxLayout()
        ip_layout.addWidget(self._input_ip)
        ip_layout.addWidget(self._label_validacion)

        # Puerto recv (read-only)
        self._input_puerto_recv = QLineEdit()
        self._input_puerto_recv.setReadOnly(True)
        self._input_puerto_recv.setStyleSheet("background-color: #1a1a1a; color: #888888;")

        # Puerto send (read-only)
        self._input_puerto_send = QLineEdit()
        self._input_puerto_send.setReadOnly(True)
        self._input_puerto_send.setStyleSheet("background-color: #1a1a1a; color: #888888;")

        # Form layout
        group_layout.addRow("IP Raspberry Pi:", ip_layout)
        group_layout.addRow("Puerto Recepción:", self._input_puerto_recv)
        group_layout.addRow("Puerto Envío:", self._input_puerto_send)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Botón aplicar
        self._btn_aplicar = QPushButton("✓ Aplicar Configuración")
        self._btn_aplicar.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        layout.addWidget(self._btn_aplicar)

        # Stretch
        layout.addStretch()

        # Estilos del input IP
        self._aplicar_estilos()

    def _aplicar_estilos(self):
        """Aplica estilos al input de IP."""
        self._input_ip.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)

    def actualizar(self, modelo: ConexionModelo):
        """Actualiza la vista desde el modelo."""
        # IP
        self._input_ip.setText(modelo.ip)

        # Puertos
        self._input_puerto_recv.setText(str(modelo.puerto_recv))
        self._input_puerto_send.setText(str(modelo.puerto_send))

        # Validación visual
        if modelo.ip_valida:
            # Borde verde
            self._input_ip.setStyleSheet("""
                QLineEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
            self._label_validacion.setText("")
            self._btn_aplicar.setEnabled(True)
        else:
            # Borde rojo
            self._input_ip.setStyleSheet("""
                QLineEdit {
                    background-color: #2d2d2d;
                    color: white;
                    border: 2px solid #dc3545;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
            self._label_validacion.setText(f"❌ {modelo.mensaje_error}")
            self._btn_aplicar.setEnabled(False)

    @property
    def input_ip(self):
        return self._input_ip

    @property
    def boton_aplicar(self):
        return self._btn_aplicar
```

**ConexionControlador:**
```python
from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import replace
import logging

class ConexionControlador(QObject):
    """Controlador del panel de conexión."""

    # Señales
    ip_cambiada = pyqtSignal(str)  # Nueva IP aplicada

    def __init__(self, modelo: ConexionModelo, vista: ConexionVista, parent=None):
        super().__init__(parent)
        self._modelo = modelo
        self._vista = vista
        self._logger = logging.getLogger(__name__)

        # Conectar señales
        self._conectar_signals()

        # Inicializar vista
        self._vista.actualizar(self._modelo)

    def _conectar_signals(self):
        """Conecta señales de la vista."""
        self._vista.input_ip.textChanged.connect(self._on_ip_changed)
        self._vista.boton_aplicar.clicked.connect(self._on_aplicar_clicked)

    def _on_ip_changed(self, texto: str):
        """Handler de cambio de texto en input IP."""
        # Validar IP
        valida, mensaje = ConexionModelo.validar_ip(texto)

        # Actualizar modelo
        self._modelo = replace(
            self._modelo,
            ip=texto,
            ip_valida=valida,
            mensaje_error=mensaje
        )

        # Actualizar vista
        self._vista.actualizar(self._modelo)

    def _on_aplicar_clicked(self):
        """Handler de click en botón Aplicar."""
        if self._modelo.ip_valida:
            # Emitir señal con la nueva IP
            self.ip_cambiada.emit(self._modelo.ip)
            self._logger.info("Nueva IP aplicada: %s", self._modelo.ip)
        else:
            self._logger.warning("Intento de aplicar IP inválida: %s", self._modelo.ip)

    @property
    def modelo(self):
        return self._modelo
```

**__init__.py:**
```python
"""Panel de configuración de conexión."""

from .modelo import ConexionModelo
from .vista import ConexionVista
from .controlador import ConexionControlador

__all__ = [
    "ConexionModelo",
    "ConexionVista",
    "ConexionControlador",
]
```

---

### Fase 2: Actualizar Factory (~30min)

**Archivo:** `app/factory.py`

**Métodos a agregar:**

```python
def crear_panel_selector_vista(self) -> tuple[SelectorVistaModelo, SelectorVistaVista, SelectorVistaControlador]:
    """Crea el panel selector de vista (ambiente/deseada)."""
    from app.presentacion.paneles.selector_vista import (
        SelectorVistaModelo, SelectorVistaVista, SelectorVistaControlador
    )

    # Modelo con modo inicial "ambiente"
    modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)

    # Vista
    vista = SelectorVistaVista()

    # Controlador
    controlador = SelectorVistaControlador(modelo, vista)

    logger.debug("Panel selector_vista creado")
    return (modelo, vista, controlador)


def crear_panel_estado_conexion(self) -> tuple[EstadoConexionModelo, EstadoConexionVista, EstadoConexionControlador]:
    """Crea el panel de estado de conexión."""
    from app.presentacion.paneles.estado_conexion import (
        EstadoConexionModelo, EstadoConexionVista, EstadoConexionControlador
    )

    # Modelo con estado inicial "desconectado"
    modelo = EstadoConexionModelo(estado="desconectado", direccion_ip="")

    # Vista
    vista = EstadoConexionVista()

    # Controlador
    controlador = EstadoConexionControlador(modelo, vista)

    logger.debug("Panel estado_conexion creado")
    return (modelo, vista, controlador)


def crear_panel_conexion(self) -> tuple[ConexionModelo, ConexionVista, ConexionControlador]:
    """Crea el panel de configuración de conexión."""
    from app.presentacion.paneles.conexion import (
        ConexionModelo, ConexionVista, ConexionControlador
    )

    # Modelo con config actual
    modelo = ConexionModelo(
        ip=self._config.ip_raspberry,
        puerto_recv=self._config.puerto_recv,
        puerto_send=self._config.puerto_send,
        ip_valida=True,
        mensaje_error=""
    )

    # Vista
    vista = ConexionVista()

    # Controlador
    controlador = ConexionControlador(modelo, vista)

    logger.debug("Panel conexion creado")
    return (modelo, vista, controlador)
```

**Actualizar método `crear_todos_paneles()`:**

```python
def crear_todos_paneles(self) -> dict[str, tuple]:
    """Crea todos los paneles de la UI."""
    return {
        "display": self.crear_panel_display(),
        "climatizador": self.crear_panel_climatizador(),
        "indicadores": self.crear_panel_indicadores(),
        "power": self.crear_panel_power(),
        "control_temp": self.crear_panel_control_temp(),
        "selector_vista": self.crear_panel_selector_vista(),         # NUEVO
        "estado_conexion": self.crear_panel_estado_conexion(),       # NUEVO
        "conexion": self.crear_panel_conexion(),                     # NUEVO
    }
```

---

### Fase 3: Actualizar Coordinator (~45min)

**Archivo:** `app/coordinator.py`

**Métodos a agregar:**

```python
def _conectar_selector_vista(self) -> None:
    """Conecta señales del panel selector de vista."""
    ctrl_selector = self._paneles["selector_vista"][2]
    ctrl_display = self._paneles["display"][2]

    # SelectorVista → Display (cambiar label)
    ctrl_selector.modo_cambiado.connect(self._on_modo_vista_cambiado)

    # SelectorVista → Cliente (enviar comando al RPi)
    ctrl_selector.modo_cambiado.connect(self._enviar_comando_modo_display)

    logger.info("Señales de selector_vista conectadas")


def _conectar_estado_conexion(self) -> None:
    """Conecta señales al panel de estado de conexión."""
    ctrl_estado = self._paneles["estado_conexion"][2]

    # Servidor → EstadoConexion
    self._servidor.conexion_establecida.connect(ctrl_estado.conexion_establecida)
    self._servidor.conexion_perdida.connect(ctrl_estado.conexion_perdida)

    # Al iniciar servidor → estado "conectando"
    ctrl_estado.conectando()

    logger.info("Señales de estado_conexion conectadas")


def _conectar_conexion(self) -> None:
    """Conecta señales del panel de conexión."""
    ctrl_conexion = self._paneles["conexion"][2]

    # Conexion → Reconectar servicios
    ctrl_conexion.ip_cambiada.connect(self._on_ip_cambiada)

    logger.info("Señales de conexion conectadas")


# -- Callbacks NUEVOS --

def _on_modo_vista_cambiado(self, modo: str) -> None:
    """Handler de cambio de modo de vista."""
    # Actualizar display (futuro - cuando Display soporte cambio de label)
    self._logger.info("Modo de vista cambiado a: %s", modo)


def _enviar_comando_modo_display(self, modo: str) -> None:
    """Envía comando de cambio de modo de display al RPi."""
    from app.dominio.comandos import ComandoSetModoDisplay

    cmd = ComandoSetModoDisplay(modo=modo)
    exito = self._cliente.enviar_comando(cmd)
    self._logger.info("Comando set_modo_display=%s enviado: %s", modo, exito)


def _on_ip_cambiada(self, nueva_ip: str) -> None:
    """Handler de cambio de IP."""
    # 1. Persistir en config
    self._persistir_ip(nueva_ip)

    # 2. Reconectar servicios
    self._reconectar_servicios(nueva_ip)

    self._logger.info("IP actualizada a: %s", nueva_ip)


def _persistir_ip(self, nueva_ip: str) -> None:
    """Persiste la nueva IP en config.json."""
    # NOTA: Requiere extender ConfigManager con método guardar_config()
    # Por ahora, solo logging
    self._logger.info("Persistiendo IP en config.json: %s", nueva_ip)
    # TODO: Implementar en ConfigManager


def _reconectar_servicios(self, nueva_ip: str) -> None:
    """Reconecta servidor y cliente con nueva IP."""
    # 1. Detener servidor actual
    if hasattr(self._servidor, 'detener'):
        self._servidor.detener()

    # 2. Actualizar IP del cliente
    # NOTA: Requiere que ClienteComandos permita cambiar IP
    # Por ahora, solo logging
    self._logger.info("Reconectando con IP: %s", nueva_ip)
    # TODO: Implementar reconexión
```

**Actualizar método `_conectar_signals()`:**

```python
def _conectar_signals(self) -> None:
    """Conecta todas las señales entre componentes."""
    self._conectar_servidor_estado()
    self._conectar_power()
    self._conectar_control_temp()
    self._conectar_selector_vista()       # NUEVO
    self._conectar_estado_conexion()      # NUEVO
    self._conectar_conexion()             # NUEVO
    logger.info("Todas las señales conectadas")
```

---

### Fase 4: Extender ConfigManager (~30min)

**Archivo:** `app/configuracion/config.py`

**Métodos a agregar:**

```python
def actualizar_ip(self, nueva_ip: str) -> None:
    """Actualiza la IP del Raspberry Pi y persiste en config.json.

    Args:
        nueva_ip: Nueva dirección IP

    Raises:
        ValueError: Si la IP no es válida
    """
    # Validar formato
    from app.presentacion.paneles.conexion import ConexionModelo
    valida, mensaje = ConexionModelo.validar_ip(nueva_ip)

    if not valida:
        raise ValueError(f"IP inválida: {mensaje}")

    # Actualizar en memoria
    # NOTA: ConfigUX es frozen, necesitamos reemplazar
    object.__setattr__(self, 'ip_raspberry', nueva_ip)

    # Persistir en disco
    self._guardar_config()

    logger.info("IP actualizada a: %s", nueva_ip)


def _guardar_config(self) -> None:
    """Guarda la configuración actual en config.json."""
    import json
    from pathlib import Path

    # Leer config.json actual
    config_path = Path(__file__).parent.parent.parent.parent / "config.json"

    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Actualizar IP
    data["raspberry_pi"]["ip"] = self.ip_raspberry

    # Guardar
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Configuración guardada en config.json")
```

**NOTA:** Como ConfigUX es `frozen=True`, necesitamos estrategia diferente. Alternativa:

**Opción 1 (Recomendada):** Crear `ConfigManager` separado:

```python
# app/configuracion/manager.py

import json
from pathlib import Path
from .config import ConfigUX

class ConfigManager:
    """Gestor de configuración con capacidad de persistencia."""

    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._config = self._cargar()

    def _cargar(self) -> ConfigUX:
        """Carga configuración de config.json."""
        with open(self._config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ConfigUX.from_dict(data)

    @property
    def config(self) -> ConfigUX:
        """Configuración actual (read-only)."""
        return self._config

    def actualizar_ip(self, nueva_ip: str) -> ConfigUX:
        """Actualiza IP y retorna nueva configuración."""
        # Validar
        from app.presentacion.paneles.conexion import ConexionModelo
        valida, mensaje = ConexionModelo.validar_ip(nueva_ip)

        if not valida:
            raise ValueError(f"IP inválida: {mensaje}")

        # Actualizar en disco
        with open(self._config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data["raspberry_pi"]["ip"] = nueva_ip

        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Recargar config
        self._config = self._cargar()

        return self._config
```

---

### Fase 5: Script de Validación Visual (~1h)

**Archivo:** `ux_termostato/validacion_visual_sprint2.py`

```python
"""Script de validación visual para paneles del Sprint 2.

Crea una ventana con los 3 paneles y simula datos del RPi.
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.configuracion.config import ConfigUX
from app.factory import ComponenteFactoryUX

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VentanaValidacion(QMainWindow):
    """Ventana de validación visual."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validación Visual - Sprint 2")
        self.setGeometry(100, 100, 700, 600)

        # Crear factory
        config = self._crear_config_mock()
        self.factory = ComponenteFactoryUX(config)

        # Crear paneles
        self.paneles = {
            "selector_vista": self.factory.crear_panel_selector_vista(),
            "estado_conexion": self.factory.crear_panel_estado_conexion(),
            "conexion": self.factory.crear_panel_conexion(),
        }

        # Crear UI
        self._crear_ui()

        # Conectar señales para logging
        self._conectar_signals()

        # Timer para simular cambios de estado
        self._iniciar_simulacion()

    def _crear_config_mock(self) -> ConfigUX:
        """Crea configuración mock."""
        return ConfigUX(
            ip_raspberry="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
            intervalo_recepcion_ms=500,
            intervalo_actualizacion_ui_ms=100,
            temperatura_min_setpoint=15.0,
            temperatura_max_setpoint=30.0,
            temperatura_setpoint_inicial=22.0
        )

    def _crear_ui(self):
        """Crea la interfaz."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)

        # Título
        from PyQt6.QtWidgets import QLabel
        titulo = QLabel("Paneles del Sprint 2")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(titulo)

        # Panel 1: Selector Vista
        layout.addWidget(self._crear_seccion("US-011: Selector Vista"))
        layout.addWidget(self.paneles["selector_vista"][1])  # Vista

        # Panel 2: Estado Conexión
        layout.addWidget(self._crear_seccion("US-015: Estado Conexión"))
        layout.addWidget(self.paneles["estado_conexion"][1])  # Vista

        # Botones de simulación de estado
        btn_layout = QHBoxLayout()

        btn_conectado = QPushButton("Simular: Conectado")
        btn_conectado.clicked.connect(lambda: self._simular_estado("conectado"))

        btn_desconectado = QPushButton("Simular: Desconectado")
        btn_desconectado.clicked.connect(lambda: self._simular_estado("desconectado"))

        btn_conectando = QPushButton("Simular: Conectando")
        btn_conectando.clicked.connect(lambda: self._simular_estado("conectando"))

        btn_layout.addWidget(btn_conectado)
        btn_layout.addWidget(btn_desconectado)
        btn_layout.addWidget(btn_conectando)
        layout.addLayout(btn_layout)

        # Panel 3: Conexión
        layout.addWidget(self._crear_seccion("US-013: Configuración IP"))
        layout.addWidget(self.paneles["conexion"][1])  # Vista

        layout.addStretch()

        # Aplicar tema oscuro
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

    def _crear_seccion(self, titulo: str) -> QWidget:
        """Crea un separador de sección."""
        from PyQt6.QtWidgets import QLabel, QFrame
        label = QLabel(titulo)
        label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #00aaff;
            padding: 5px;
            border-bottom: 2px solid #555555;
        """)
        return label

    def _conectar_signals(self):
        """Conecta señales para logging."""
        # SelectorVista
        ctrl_selector = self.paneles["selector_vista"][2]
        ctrl_selector.modo_cambiado.connect(
            lambda modo: logger.info("✓ Señal modo_cambiado: %s", modo)
        )

        # EstadoConexion
        ctrl_estado = self.paneles["estado_conexion"][2]
        ctrl_estado.estado_cambiado.connect(
            lambda estado: logger.info("✓ Señal estado_cambiado: %s", estado)
        )

        # Conexion
        ctrl_conexion = self.paneles["conexion"][2]
        ctrl_conexion.ip_cambiada.connect(
            lambda ip: logger.info("✓ Señal ip_cambiada: %s", ip)
        )

    def _iniciar_simulacion(self):
        """Inicia timer de simulación de estados."""
        self.simulacion_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._ciclo_simulacion)
        # No iniciamos automáticamente, solo con botones

    def _simular_estado(self, estado: str):
        """Simula un estado de conexión."""
        ctrl_estado = self.paneles["estado_conexion"][2]

        if estado == "conectado":
            ctrl_estado.conexion_establecida("192.168.1.50:14001")
        elif estado == "desconectado":
            ctrl_estado.conexion_perdida()
        elif estado == "conectando":
            ctrl_estado.conectando()

    def _ciclo_simulacion(self):
        """Ciclo de simulación automática."""
        estados = ["conectando", "conectado", "desconectado"]
        estado = estados[self.simulacion_index % len(estados)]
        self._simular_estado(estado)
        self.simulacion_index += 1


def main():
    """Entry point."""
    app = QApplication(sys.argv)
    ventana = VentanaValidacion()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## Checklist de Progreso

### Fase 1: Implementación Paneles (SIN TESTS)
- [ ] US-011: Panel SelectorVista
  - [ ] modelo.py
  - [ ] vista.py
  - [ ] controlador.py
  - [ ] __init__.py
- [ ] US-015: Panel EstadoConexion
  - [ ] modelo.py
  - [ ] vista.py
  - [ ] controlador.py
  - [ ] __init__.py
- [ ] US-013: Panel Conexion
  - [ ] modelo.py
  - [ ] vista.py
  - [ ] controlador.py
  - [ ] __init__.py

### Fase 2: Factory
- [ ] Método `crear_panel_selector_vista()`
- [ ] Método `crear_panel_estado_conexion()`
- [ ] Método `crear_panel_conexion()`
- [ ] Actualizar `crear_todos_paneles()`

### Fase 3: Coordinator
- [ ] Método `_conectar_selector_vista()`
- [ ] Método `_conectar_estado_conexion()`
- [ ] Método `_conectar_conexion()`
- [ ] Callbacks: `_on_modo_vista_cambiado()`, `_enviar_comando_modo_display()`, `_on_ip_cambiada()`
- [ ] Actualizar `_conectar_signals()`

### Fase 4: ConfigManager
- [ ] Crear `ConfigManager` (manager.py)
- [ ] Método `actualizar_ip()`
- [ ] Método `_guardar_config()`
- [ ] Tests manuales de persistencia

### Fase 5: Script Validación
- [ ] Script `validacion_visual_sprint2.py`
- [ ] Ejecutar y validar visualmente los 3 paneles
- [ ] Verificar señales en log

### Fase 6: Git Commits
- [ ] Commit 1: `feat(US-011): implementar panel SelectorVista`
- [ ] Commit 2: `feat(US-015): implementar panel EstadoConexion`
- [ ] Commit 3: `feat(US-013): implementar panel Conexion`
- [ ] Commit 4: `feat(Sprint-2): actualizar Factory y Coordinator`

---

## Tests Unitarios (DESPUÉS - De a Uno)

### US-011: Tests SelectorVista (~2h)
- [ ] test_selector_vista_modelo.py
  - TestCreacion (2 tests)
  - TestValidaciones (2 tests)
- [ ] test_selector_vista_vista.py
  - TestCreacion (2 tests)
  - TestActualizacion (3 tests)
  - TestEstilos (2 tests)
- [ ] test_selector_vista_controlador.py
  - TestCreacion (2 tests)
  - TestCambioModo (3 tests)
  - TestSignals (2 tests)
  - TestHabilitacion (2 tests)
- [ ] test_selector_vista_integracion.py
  - TestFlujoCompleto (3 tests)

**Total:** ~20 tests

---

### US-015: Tests EstadoConexion (~2h)
- [ ] test_estado_conexion_modelo.py
  - TestCreacion (2 tests)
  - TestValidaciones (2 tests)
- [ ] test_estado_conexion_vista.py
  - TestCreacion (2 tests)
  - TestActualizacion (3 tests - conectado/desconectado/conectando)
  - TestAnimacionPulso (2 tests)
- [ ] test_estado_conexion_controlador.py
  - TestCreacion (2 tests)
  - TestActualizarEstado (3 tests)
  - TestMetodosConveniencia (3 tests - conexion_establecida, conexion_perdida, conectando)
  - TestSignals (2 tests)
- [ ] test_estado_conexion_integracion.py
  - TestFlujoCompleto (3 tests)

**Total:** ~22 tests

---

### US-013: Tests Conexion (~3h)
- [ ] test_conexion_modelo.py
  - TestCreacion (2 tests)
  - TestValidaciones (4 tests - puertos, IP)
  - TestValidarIP (6 tests - válidas, inválidas, rangos)
- [ ] test_conexion_vista.py
  - TestCreacion (2 tests)
  - TestActualizacion (3 tests)
  - TestValidacionVisual (3 tests - válida, inválida, mensaje error)
  - TestBotones (2 tests)
- [ ] test_conexion_controlador.py
  - TestCreacion (2 tests)
  - TestValidacionIP (4 tests)
  - TestAplicarConfiguracion (3 tests)
  - TestSignals (2 tests)
- [ ] test_conexion_integracion.py
  - TestFlujoCompleto (4 tests)
- [ ] test_config_manager.py (NUEVO)
  - TestActualizarIP (3 tests)
  - TestPersistencia (3 tests)
  - TestValidaciones (2 tests)

**Total:** ~35 tests

---

## Estimación de Tiempos

### Implementación (sin tests)
- Panel SelectorVista: 1h
- Panel EstadoConexion: 1h
- Panel Conexion: 2h
- Factory: 30min
- Coordinator: 45min
- ConfigManager: 30min
- Script validación: 1h
- **Subtotal:** 6.75h

### Tests (después, de a uno)
- US-011 tests: 2h
- US-015 tests: 2h
- US-013 tests: 3h
- **Subtotal:** 7h

**Total estimado:** ~14h (6.75h implementación + 7h tests)

---

## Quality Gates

Cada panel debe cumplir:
- **Coverage:** ≥ 95%
- **Pylint:** ≥ 8.0
- **CC:** ≤ 10
- **MI:** > 20

---

## Dependencias Críticas

- ✅ US-020 (EstadoTermostato, Comandos)
- ✅ US-021 (ServidorEstado, ClienteComandos)
- ✅ US-022 (Factory, Coordinator, ConfigUX)
- ⚠️ compartido/widgets/led_indicator.py (para US-015)
- ⚠️ config.json (para persistencia en US-013)

---

## Próximos Pasos Después del Sprint 2

Una vez completados US-011, US-015, US-013:
- ➡️ US-023: UICompositor (ensambla layout con TODOS los paneles)
- ➡️ US-024: VentanaPrincipal (main window + lifecycle)
- ➡️ US-025: run.py (entry point final)

---

## Criterios de Aceptación del Sprint 2

- [ ] Paneles SelectorVista, EstadoConexion, Conexion implementados
- [ ] Factory actualizado con métodos de creación
- [ ] Coordinator actualizado con conexiones de señales
- [ ] ConfigManager con persistencia de IP
- [ ] Script de validación visual ejecuta correctamente
- [ ] Todos los paneles visibles y funcionales
- [ ] Señales PyQt funcionan correctamente
- [ ] Validación manual exitosa
- [ ] Commits git realizados (4 commits)
- [ ] Tests unitarios (implementados después, de a uno)
- [ ] Coverage ≥ 95% por panel
- [ ] Pylint ≥ 8.0 por panel

---

**Versión:** 1.0
**Fecha:** 2026-01-24
**Estado:** 🔲 PENDIENTE
**Estrategia:** Implementación completa → Validación visual → Tests de a uno
