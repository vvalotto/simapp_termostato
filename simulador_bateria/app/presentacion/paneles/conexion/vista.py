"""Vista para el Panel de Conexion.

Responsable unicamente de la presentacion visual de la conexion TCP.
"""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from compartido.widgets import (
    ConfigPanel,
    ConfigPanelLabels,
    LEDColor,
    LEDStatusIndicator,
)
from ..base import ModeloBase
from .modelo import ConexionPanelModelo


@dataclass(frozen=True)
class ConfigConexionPanelVista:
    """Configuracion visual del panel de conexion."""

    titulo: str = "Conexion TCP"
    color_fondo: str = "#2d2d2d"
    color_texto: str = "#d4d4d4"
    texto_conectar: str = "Conectar"
    texto_desconectar: str = "Desconectar"


class ConexionPanelVista(QFrame):
    """Vista del panel de conexion TCP.

    Muestra:
    - Campo IP
    - Campo Puerto
    - Boton Conectar/Desconectar
    - LED indicador de estado

    Usa ConfigPanel de compartido/widgets internamente.

    Signals:
        conectar_clicked: Emitido cuando se presiona el boton conectar.
        desconectar_clicked: Emitido cuando se presiona desconectar.
    """

    conectar_clicked = pyqtSignal()
    desconectar_clicked = pyqtSignal()

    def __init__(
        self,
        config: Optional[ConfigConexionPanelVista] = None,
        default_ip: str = "localhost",
        default_port: int = 11000,
        parent=None
    ) -> None:
        """Inicializa la vista del panel de conexion.

        Args:
            config: Configuracion visual del panel.
            default_ip: IP por defecto.
            default_port: Puerto por defecto.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigConexionPanelVista()
        self._default_ip = default_ip
        self._default_port = default_port
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
            QLineEdit {{
                background-color: #3d3d3d;
                color: {self._config.color_texto};
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }}
            QSpinBox {{
                background-color: #3d3d3d;
                color: {self._config.color_texto};
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton {{
                background-color: #4fc3f7;
                color: #1a1a1a;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #81d4fa;
            }}
            QPushButton:pressed {{
                background-color: #29b6f6;
            }}
        """)

        layout = QVBoxLayout(self)

        # Titulo
        titulo = QLabel(self._config.titulo)
        titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # ConfigPanel compartido
        labels = ConfigPanelLabels(
            ip_label="IP:",
            port_label="Puerto:",
            connect_text=self._config.texto_conectar,
            disconnect_text=self._config.texto_desconectar
        )
        status_indicator = LEDStatusIndicator(color=LEDColor.GREEN)

        self._config_panel = ConfigPanel(
            default_ip=self._default_ip,
            default_port=self._default_port,
            labels=labels,
            status_indicator=status_indicator
        )

        # Conectar signals del ConfigPanel
        self._config_panel.connect_requested.connect(self._on_conectar)
        self._config_panel.disconnect_requested.connect(self._on_desconectar)

        layout.addWidget(self._config_panel)

    def _on_conectar(self) -> None:
        """Callback cuando se solicita conexion."""
        self.conectar_clicked.emit()

    def _on_desconectar(self) -> None:
        """Callback cuando se solicita desconexion."""
        self.desconectar_clicked.emit()

    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo.

        Args:
            modelo: Instancia de ConexionPanelModelo con los datos.
        """
        if not isinstance(modelo, ConexionPanelModelo):
            return

        # Actualizar campos solo si no esta conectado
        if not modelo.conectado:
            self._config_panel.set_ip(modelo.ip)
            self._config_panel.set_port(modelo.puerto)

        # Actualizar estado de conexion
        self._config_panel.set_connected_state(modelo.conectado)

    def get_ip(self) -> str:
        """Retorna la IP actual del campo.

        Returns:
            Direccion IP ingresada.
        """
        return self._config_panel.get_ip()

    def get_puerto(self) -> int:
        """Retorna el puerto actual del campo.

        Returns:
            Numero de puerto ingresado.
        """
        return self._config_panel.get_port()

    def set_conectado(self, conectado: bool) -> None:
        """Actualiza el estado visual de conexion.

        Args:
            conectado: True si esta conectado.
        """
        self._config_panel.set_connected_state(conectado)
