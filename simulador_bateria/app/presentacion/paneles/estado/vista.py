"""Vista para el Panel de Estado de Bateria.

Responsable unicamente de la presentacion visual del estado.
"""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..base import ModeloBase
from .modelo import EstadoBateriaPanelModelo


@dataclass(frozen=True)
class ConfigPanelEstadoVista:
    """Configuracion visual del panel de estado de bateria."""

    titulo: str = "Estado Bateria"
    texto_conectado: str = "Conectado"
    texto_desconectado: str = "Desconectado"
    texto_sin_datos: str = "-.- V"
    color_fondo: str = "#2d2d2d"
    color_texto: str = "#d4d4d4"
    color_voltaje: str = "#4fc3f7"
    color_porcentaje: str = "#81c784"
    color_conectado: str = "#81c784"
    color_desconectado: str = "#e57373"


class PanelEstadoVista(QFrame):
    """Vista del panel de estado de la bateria.

    Muestra:
    - Voltaje actual en formato X.XV
    - Porcentaje equivalente (0-100%)
    - Estado de conexion
    - Contadores de envios exitosos/fallidos

    Implementa la interfaz de VistaBase sin herencia directa
    para evitar conflictos de metaclase con QFrame.
    """

    def __init__(
        self,
        config: Optional[ConfigPanelEstadoVista] = None,
        parent=None
    ) -> None:
        """Inicializa la vista del panel de estado.

        Args:
            config: Configuracion visual del panel.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigPanelEstadoVista()
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

        # Voltaje actual
        self._label_voltaje = QLabel(self._config.texto_sin_datos)
        self._label_voltaje.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self._label_voltaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_voltaje.setStyleSheet(
            f"color: {self._config.color_voltaje};"
        )
        layout.addWidget(self._label_voltaje)

        # Porcentaje equivalente
        self._label_porcentaje = QLabel("0%")
        self._label_porcentaje.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self._label_porcentaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_porcentaje.setStyleSheet(
            f"color: {self._config.color_porcentaje};"
        )
        layout.addWidget(self._label_porcentaje)

        # Estado conexion
        self._label_conexion = QLabel(self._config.texto_desconectado)
        self._label_conexion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_conexion.setStyleSheet(
            f"color: {self._config.color_desconectado};"
        )
        layout.addWidget(self._label_conexion)

        # Contador de envios
        self._label_contador = QLabel("Envios: 0 / 0")
        self._label_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_contador.setStyleSheet(
            f"color: {self._config.color_texto};"
        )
        layout.addWidget(self._label_contador)

    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo.

        Args:
            modelo: Instancia de EstadoBateriaPanelModelo con los datos.
        """
        if not isinstance(modelo, EstadoBateriaPanelModelo):
            return

        # Actualizar voltaje
        self._label_voltaje.setText(f"{modelo.voltaje_actual:.1f}V")

        # Actualizar porcentaje
        self._label_porcentaje.setText(f"{modelo.porcentaje:.0f}%")

        # Actualizar estado de conexion
        if modelo.conectado:
            self._label_conexion.setText(self._config.texto_conectado)
            self._label_conexion.setStyleSheet(
                f"color: {self._config.color_conectado};"
            )
        else:
            self._label_conexion.setText(self._config.texto_desconectado)
            self._label_conexion.setStyleSheet(
                f"color: {self._config.color_desconectado};"
            )

        # Actualizar contadores
        self._label_contador.setText(
            f"Envios: {modelo.envios_exitosos} / {modelo.envios_fallidos}"
        )

    def mostrar_sin_datos(self) -> None:
        """Muestra el estado inicial sin datos."""
        self._label_voltaje.setText(self._config.texto_sin_datos)
        self._label_porcentaje.setText("0%")
