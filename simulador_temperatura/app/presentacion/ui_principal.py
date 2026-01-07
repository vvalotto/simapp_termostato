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

from .control_temperatura import ControlTemperatura, ParametrosSenoidal, RangosControl
from .grafico_temperatura import GraficoTemperatura, ConfigGrafico


@dataclass(frozen=True)
class ConfigVentana:
    """Configuracion de la ventana principal."""

    titulo: str = "Simulador de Temperatura"
    ancho: int = 1200
    alto: int = 700


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
    """

    parametros_cambiados = pyqtSignal(ParametrosSenoidal)
    temperatura_manual_cambiada = pyqtSignal(float)

    def __init__(
        self,
        config: Optional[ConfigVentana] = None,
        rangos_control: Optional[RangosControl] = None,
        config_grafico: Optional[ConfigGrafico] = None,
        config_panel_estado: Optional[ConfigPanelEstado] = None,
        tema: Optional[ConfigTemaOscuro] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa la ventana principal.

        Args:
            config: Configuracion de la ventana.
            rangos_control: Rangos para el control de temperatura.
            config_grafico: Configuracion del grafico.
            config_panel_estado: Configuracion del panel de estado.
            tema: Configuracion del tema visual.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigVentana()
        self._rangos_control = rangos_control
        self._config_grafico = config_grafico
        self._config_panel_estado = config_panel_estado
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

        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

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

        # Agregar layouts
        main_layout.addLayout(panel_izquierdo, stretch=1)
        main_layout.addWidget(self._grafico, stretch=2)

    def _setup_conexiones(self) -> None:
        """Configura las conexiones de signals."""
        # Conexion directa sin metodos relay
        self._control_temperatura.parametros_senoidal_cambiados.connect(
            self.parametros_cambiados.emit
        )
        self._control_temperatura.temperatura_manual_cambiada.connect(
            self.temperatura_manual_cambiada.emit
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
