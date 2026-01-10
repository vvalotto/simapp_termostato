"""Ventana principal como Compositor - usa controladores MVC.

Esta es la nueva implementación de la UI principal que recibe
controladores MVC en lugar de crear widgets directamente.
"""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from ..presentacion.paneles.estado import PanelEstadoControlador
from ..presentacion.paneles.control_temperatura import ControlTemperaturaControlador
from ..presentacion.paneles.grafico import GraficoControlador
from ..presentacion.paneles.conexion import PanelConexionControlador


@dataclass(frozen=True)
class ConfigVentanaCompositor:
    """Configuración de la ventana principal."""

    titulo: str = "Simulador de Temperatura"
    ancho: int = 1200
    alto: int = 700
    color_fondo: str = "#1e1e1e"
    color_texto: str = "#d4d4d4"


class UIPrincipalCompositor(QMainWindow):
    """Ventana principal del simulador - Compositor de paneles MVC.

    Esta clase es responsable únicamente del layout y composición visual.
    Toda la lógica está en los controladores MVC.
    """

    def __init__(
        self,
        ctrl_estado: PanelEstadoControlador,
        ctrl_control: ControlTemperaturaControlador,
        ctrl_grafico: GraficoControlador,
        ctrl_conexion: PanelConexionControlador,
        config: Optional[ConfigVentanaCompositor] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa la ventana principal.

        Args:
            ctrl_estado: Controlador del panel de estado.
            ctrl_control: Controlador de control de temperatura.
            ctrl_grafico: Controlador del gráfico.
            ctrl_conexion: Controlador del panel de conexión.
            config: Configuración de la ventana.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigVentanaCompositor()

        # Almacenar referencias a controladores
        self._ctrl_estado = ctrl_estado
        self._ctrl_control = ctrl_control
        self._ctrl_grafico = ctrl_grafico
        self._ctrl_conexion = ctrl_conexion

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura la interfaz de la ventana."""
        self.setWindowTitle(self._config.titulo)
        self.resize(self._config.ancho, self._config.alto)

        # Aplicar tema oscuro
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self._config.color_fondo};
            }}
            QWidget {{
                background-color: {self._config.color_fondo};
                color: {self._config.color_texto};
            }}
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal vertical (conexión arriba, contenido abajo)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # Panel de conexión arriba
        root_layout.addWidget(self._ctrl_conexion.vista)

        # Layout horizontal para contenido principal
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Panel izquierdo (controles)
        panel_izquierdo = QVBoxLayout()

        # Vista del control de temperatura
        panel_izquierdo.addWidget(self._ctrl_control.vista)

        # Vista del panel de estado
        panel_izquierdo.addWidget(self._ctrl_estado.vista)

        panel_izquierdo.addStretch()

        # Panel derecho (gráfico)
        content_layout.addLayout(panel_izquierdo, stretch=1)
        content_layout.addWidget(self._ctrl_grafico.vista, stretch=2)

        root_layout.addLayout(content_layout, stretch=1)

    # -- Acceso a controladores --

    @property
    def ctrl_estado(self) -> PanelEstadoControlador:
        """Retorna el controlador del panel de estado."""
        return self._ctrl_estado

    @property
    def ctrl_control(self) -> ControlTemperaturaControlador:
        """Retorna el controlador de control de temperatura."""
        return self._ctrl_control

    @property
    def ctrl_grafico(self) -> GraficoControlador:
        """Retorna el controlador del gráfico."""
        return self._ctrl_grafico

    @property
    def ctrl_conexion(self) -> PanelConexionControlador:
        """Retorna el controlador del panel de conexión."""
        return self._ctrl_conexion
