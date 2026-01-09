"""Ventana principal del Simulador de Temperatura."""
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from compartido.widgets.config_panel import ConfigPanel, ConfigPanelLabels
from .control_temperatura import ControlTemperatura, ParametrosSenoidal, RangosControl
from .grafico_temperatura import GraficoTemperatura, ConfigGrafico


@dataclass(frozen=True)
class ConfigVentana:
    """Configuracion de la ventana principal."""

    titulo: str = "Simulador de Temperatura"
    ancho: int = 1200
    alto: int = 700


@dataclass(frozen=True)
class ConfigConexion:
    """Configuracion de conexion por defecto."""

    ip: str = "127.0.0.1"
    puerto: int = 12000


@dataclass(frozen=True)
class ConfigPanelEstado:
    """Configuracion del panel de estado."""

    titulo: str = "Estado Actual"
    texto_conectado: str = "Conectado"
    texto_desconectado: str = "Desconectado"
    texto_sin_datos: str = "--.- °C"
    color_fondo: str = "#2d2d2d"
    color_texto: str = "#d4d4d4"
    color_temperatura: str = "#4fc3f7"
    color_conectado: str = "#81c784"
    color_desconectado: str = "#e57373"


class PanelEstado(QFrame):
    """Panel que muestra el estado actual de la simulacion."""

    def __init__(
        self,
        config: Optional[ConfigPanelEstado] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa el panel de estado.

        Args:
            config: Configuracion del panel.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigPanelEstado()
        self._envios_exitosos = 0
        self._envios_fallidos = 0
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura la interfaz del panel."""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self._config.color_fondo};
                border-radius: 8px;
                padding: 10px;
            }}
            QLabel {{
                color: {self._config.color_texto};
            }}
        """)

        layout = QVBoxLayout(self)

        # Titulo
        titulo = QLabel(self._config.titulo)
        titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Temperatura actual
        self._label_temperatura = QLabel(self._config.texto_sin_datos)
        self._label_temperatura.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self._label_temperatura.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_temperatura.setStyleSheet(
            f"color: {self._config.color_temperatura};"
        )
        layout.addWidget(self._label_temperatura)

        # Estado conexion
        self._label_conexion = QLabel(self._config.texto_desconectado)
        self._label_conexion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_conexion.setStyleSheet(
            f"color: {self._config.color_desconectado};"
        )
        layout.addWidget(self._label_conexion)

        # Contador de envios
        self._label_contador = QLabel("Envíos: 0 ✓  0 ✗")
        self._label_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_contador.setStyleSheet(f"color: {self._config.color_texto};")
        layout.addWidget(self._label_contador)

    def actualizar_temperatura(self, temperatura: float) -> None:
        """Actualiza la temperatura mostrada.

        Args:
            temperatura: Valor de temperatura a mostrar.
        """
        self._label_temperatura.setText(f"{temperatura:.1f} °C")

    def actualizar_estado_conexion(self, conectado: bool) -> None:
        """Actualiza el estado de conexion.

        Args:
            conectado: True si esta conectado.
        """
        if conectado:
            self._label_conexion.setText(self._config.texto_conectado)
            self._label_conexion.setStyleSheet(
                f"color: {self._config.color_conectado};"
            )
        else:
            self._label_conexion.setText(self._config.texto_desconectado)
            self._label_conexion.setStyleSheet(
                f"color: {self._config.color_desconectado};"
            )

    def incrementar_envios_exitosos(self) -> None:
        """Incrementa el contador de envios exitosos."""
        self._envios_exitosos += 1
        self._actualizar_contador()

    def incrementar_envios_fallidos(self) -> None:
        """Incrementa el contador de envios fallidos."""
        self._envios_fallidos += 1
        self._actualizar_contador()

    def reiniciar_contadores(self) -> None:
        """Reinicia los contadores de envios."""
        self._envios_exitosos = 0
        self._envios_fallidos = 0
        self._actualizar_contador()

    def _actualizar_contador(self) -> None:
        """Actualiza el label del contador."""
        self._label_contador.setText(
            f"Envíos: {self._envios_exitosos} ✓  {self._envios_fallidos} ✗"
        )

    @property
    def envios_exitosos(self) -> int:
        """Retorna el numero de envios exitosos."""
        return self._envios_exitosos

    @property
    def envios_fallidos(self) -> int:
        """Retorna el numero de envios fallidos."""
        return self._envios_fallidos


@dataclass(frozen=True)
class ConfigTemaOscuro:
    """Configuracion del tema oscuro de la aplicacion."""

    color_fondo: str = "#1e1e1e"
    color_texto: str = "#d4d4d4"


class UIPrincipal(QMainWindow):
    """Ventana principal del simulador de temperatura.

    Integra los widgets de control y visualizacion de temperatura.

    Signals:
        parametros_cambiados: Emitido cuando cambian los parametros senoidales.
        temperatura_manual_cambiada: Emitido cuando cambia la temperatura manual.
        conexion_solicitada: Emitido cuando se solicita conectar.
        desconexion_solicitada: Emitido cuando se solicita desconectar.
        config_conexion_cambiada: Emitido cuando cambia IP o puerto.
    """

    parametros_cambiados = pyqtSignal(ParametrosSenoidal)
    temperatura_manual_cambiada = pyqtSignal(float)
    conexion_solicitada = pyqtSignal()
    desconexion_solicitada = pyqtSignal()
    config_conexion_cambiada = pyqtSignal()

    def __init__(
        self,
        config: Optional[ConfigVentana] = None,
        rangos_control: Optional[RangosControl] = None,
        config_grafico: Optional[ConfigGrafico] = None,
        config_panel_estado: Optional[ConfigPanelEstado] = None,
        config_conexion: Optional[ConfigConexion] = None,
        tema: Optional[ConfigTemaOscuro] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa la ventana principal.

        Args:
            config: Configuracion de la ventana.
            rangos_control: Rangos para el control de temperatura.
            config_grafico: Configuracion del grafico.
            config_panel_estado: Configuracion del panel de estado.
            config_conexion: Configuracion de conexion (IP/puerto).
            tema: Configuracion del tema visual.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigVentana()
        self._rangos_control = rangos_control
        self._config_grafico = config_grafico
        self._config_panel_estado = config_panel_estado
        self._config_conexion = config_conexion or ConfigConexion()
        self._tema = tema or ConfigTemaOscuro()

        self._setup_ui()
        self._setup_conexiones()

    def _setup_ui(self) -> None:
        """Configura la interfaz de la ventana."""
        self.setWindowTitle(self._config.titulo)
        self.resize(self._config.ancho, self._config.alto)

        # Aplicar tema
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self._tema.color_fondo};
            }}
            QWidget {{
                background-color: {self._tema.color_fondo};
                color: {self._tema.color_texto};
            }}
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal vertical (config panel arriba, contenido abajo)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # Panel de configuración de conexión (arriba)
        labels = ConfigPanelLabels(
            ip_label="IP Servidor:",
            port_label="Puerto:",
            connect_text="Conectar",
            disconnect_text="Desconectar",
        )
        self._config_panel = ConfigPanel(
            default_ip=self._config_conexion.ip,
            default_port=self._config_conexion.puerto,
            labels=labels,
        )
        root_layout.addWidget(self._config_panel)

        # Layout horizontal para contenido principal
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Panel izquierdo (controles)
        panel_izquierdo = QVBoxLayout()

        self._control_temperatura = ControlTemperatura(
            rangos=self._rangos_control,
        )
        panel_izquierdo.addWidget(self._control_temperatura)

        self._panel_estado = PanelEstado(config=self._config_panel_estado)
        panel_izquierdo.addWidget(self._panel_estado)

        panel_izquierdo.addStretch()

        # Panel derecho (grafico)
        self._grafico = GraficoTemperatura(config=self._config_grafico)

        # Agregar layouts al contenido
        content_layout.addLayout(panel_izquierdo, stretch=1)
        content_layout.addWidget(self._grafico, stretch=2)

        root_layout.addLayout(content_layout, stretch=1)

    def _setup_conexiones(self) -> None:
        """Configura las conexiones de signals."""
        # Conexion directa sin metodos relay
        self._control_temperatura.parametros_senoidal_cambiados.connect(
            self.parametros_cambiados.emit
        )
        self._control_temperatura.temperatura_manual_cambiada.connect(
            self.temperatura_manual_cambiada.emit
        )

        # Conexiones del panel de configuración
        self._config_panel.connect_requested.connect(
            self.conexion_solicitada.emit
        )
        self._config_panel.disconnect_requested.connect(
            self.desconexion_solicitada.emit
        )
        self._config_panel.config_changed.connect(
            self.config_conexion_cambiada.emit
        )

    def agregar_punto_grafico(
        self, temperatura: float, timestamp: Optional[float] = None
    ) -> None:
        """Agrega un punto al grafico de temperatura.

        Args:
            temperatura: Valor de temperatura.
            timestamp: Timestamp opcional.
        """
        self._grafico.add_punto(temperatura, timestamp)

    def actualizar_temperatura_display(self, temperatura: float) -> None:
        """Actualiza la temperatura en el panel de estado.

        Args:
            temperatura: Valor de temperatura a mostrar.
        """
        self._panel_estado.actualizar_temperatura(temperatura)

    def limpiar_grafico(self) -> None:
        """Limpia el grafico de temperatura."""
        self._grafico.clear()

    def actualizar_estado_conexion(self, conectado: bool) -> None:
        """Actualiza el estado de conexion en el panel.

        Args:
            conectado: True si esta conectado.
        """
        self._panel_estado.actualizar_estado_conexion(conectado)
        self._config_panel.set_connected_state(conectado)

    def incrementar_envios_exitosos(self) -> None:
        """Incrementa el contador de envios exitosos."""
        self._panel_estado.incrementar_envios_exitosos()

    def incrementar_envios_fallidos(self) -> None:
        """Incrementa el contador de envios fallidos."""
        self._panel_estado.incrementar_envios_fallidos()

    def reiniciar_contadores(self) -> None:
        """Reinicia los contadores de envios."""
        self._panel_estado.reiniciar_contadores()

    def obtener_ip(self) -> str:
        """Obtiene la IP configurada en el panel.

        Returns:
            Direccion IP configurada.
        """
        return self._config_panel.get_ip()

    def obtener_puerto(self) -> int:
        """Obtiene el puerto configurado en el panel.

        Returns:
            Numero de puerto configurado.
        """
        return self._config_panel.get_port()

    def establecer_ip(self, ip: str) -> None:
        """Establece la IP en el panel de configuracion.

        Args:
            ip: Direccion IP a establecer.
        """
        self._config_panel.set_ip(ip)

    def establecer_puerto(self, puerto: int) -> None:
        """Establece el puerto en el panel de configuracion.

        Args:
            puerto: Numero de puerto a establecer.
        """
        self._config_panel.set_port(puerto)

    @property
    def control_temperatura(self) -> ControlTemperatura:
        """Retorna el widget de control de temperatura."""
        return self._control_temperatura

    @property
    def grafico(self) -> GraficoTemperatura:
        """Retorna el widget de grafico."""
        return self._grafico

    @property
    def panel_estado(self) -> PanelEstado:
        """Retorna el panel de estado."""
        return self._panel_estado

    @property
    def config_panel(self) -> ConfigPanel:
        """Retorna el panel de configuracion de conexion."""
        return self._config_panel
