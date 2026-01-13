"""Vista para el Panel de Control de Bateria.

Responsable unicamente de la presentacion visual del control de voltaje.
"""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame, QSlider, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..base import ModeloBase
from .modelo import ControlPanelModelo


@dataclass(frozen=True)
class ConfigControlPanelVista:
    """Configuracion visual del panel de control de bateria."""

    titulo: str = "Control de Voltaje"
    unidad: str = "V"
    color_fondo: str = "#2d2d2d"
    color_texto: str = "#d4d4d4"
    color_valor: str = "#4fc3f7"
    color_slider: str = "#4fc3f7"


class ControlPanelVista(QFrame):
    """Vista del panel de control de voltaje.

    Muestra:
    - Slider para controlar el voltaje (0-5V)
    - Valor actual junto al slider

    Signals:
        slider_cambiado: Emitido cuando el usuario mueve el slider.
    """

    slider_cambiado = pyqtSignal(int)

    def __init__(
        self,
        config: Optional[ConfigControlPanelVista] = None,
        parent=None
    ) -> None:
        """Inicializa la vista del panel de control.

        Args:
            config: Configuracion visual del panel.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigControlPanelVista()
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
            QSlider::groove:horizontal {{
                border: 1px solid #555;
                height: 8px;
                background: #3d3d3d;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self._config.color_slider};
                border: 1px solid #4fc3f7;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {self._config.color_slider};
                border-radius: 4px;
            }}
        """)

        layout = QVBoxLayout(self)

        # Titulo
        titulo = QLabel(self._config.titulo)
        titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        # Layout horizontal para slider y valor
        slider_layout = QHBoxLayout()

        # Etiqueta minimo
        self._label_min = QLabel("0.0V")
        self._label_min.setStyleSheet(f"color: {self._config.color_texto};")
        slider_layout.addWidget(self._label_min)

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(50)  # 0-5V con precision 0.1V
        self._slider.setValue(42)   # 4.2V inicial
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider.setTickInterval(10)  # Tick cada 1V
        self._slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self._slider, stretch=1)

        # Etiqueta maximo
        self._label_max = QLabel("5.0V")
        self._label_max.setStyleSheet(f"color: {self._config.color_texto};")
        slider_layout.addWidget(self._label_max)

        layout.addLayout(slider_layout)

        # Valor actual
        self._label_valor = QLabel("4.2V")
        self._label_valor.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self._label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_valor.setStyleSheet(f"color: {self._config.color_valor};")
        layout.addWidget(self._label_valor)

    def _on_slider_changed(self, value: int) -> None:
        """Callback cuando cambia el slider.

        Args:
            value: Nuevo valor del slider.
        """
        self.slider_cambiado.emit(value)

    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo.

        Args:
            modelo: Instancia de ControlPanelModelo con los datos.
        """
        if not isinstance(modelo, ControlPanelModelo):
            return

        # Actualizar slider sin disparar signal
        self._slider.blockSignals(True)
        paso = modelo.voltaje_a_paso(modelo.voltaje)
        self._slider.setValue(paso)
        self._slider.blockSignals(False)

        # Actualizar label de valor
        self._label_valor.setText(f"{modelo.voltaje:.1f}{self._config.unidad}")

        # Actualizar etiquetas min/max
        self._label_min.setText(f"{modelo.voltaje_minimo:.1f}V")
        self._label_max.setText(f"{modelo.voltaje_maximo:.1f}V")

    def get_slider_value(self) -> int:
        """Retorna el valor actual del slider.

        Returns:
            Valor entero del slider.
        """
        return self._slider.value()
