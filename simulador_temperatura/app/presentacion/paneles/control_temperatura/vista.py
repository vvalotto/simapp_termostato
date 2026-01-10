"""Vista para el Panel de Control de Temperatura.

Responsable de la presentación de los controles de simulación.
"""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QComboBox,
    QStackedWidget,
)

from ..base import ModeloBase
from .modelo import ParametrosControl, ModoOperacion, RangosControl


class SliderConValor(QWidget):
    """Slider con label que muestra el valor actual."""

    valor_cambiado = pyqtSignal(float)

    def __init__(
        self,
        label: str,
        min_val: float,
        max_val: float,
        valor_inicial: float,
        sufijo: str = "",
        decimales: int = 1,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._sufijo = sufijo
        self._decimales = decimales
        self._factor = 10 ** decimales
        self._setup_ui(label, min_val, max_val, valor_inicial)

    def _setup_ui(
        self, label: str, min_val: float, max_val: float, valor_inicial: float
    ) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(label)
        self._label.setMinimumWidth(100)
        layout.addWidget(self._label)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(int(min_val * self._factor))
        self._slider.setMaximum(int(max_val * self._factor))
        self._slider.setValue(int(valor_inicial * self._factor))
        self._slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._slider, stretch=1)

        self._valor_label = QLabel()
        self._valor_label.setMinimumWidth(60)
        self._valor_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._actualizar_valor_label(valor_inicial)
        layout.addWidget(self._valor_label)

    def _on_slider_changed(self, valor_int: int) -> None:
        valor = valor_int / self._factor
        self._actualizar_valor_label(valor)
        self.valor_cambiado.emit(valor)

    def _actualizar_valor_label(self, valor: float) -> None:
        formato = f"{{:.{self._decimales}f}}"
        self._valor_label.setText(f"{formato.format(valor)}{self._sufijo}")

    @property
    def valor(self) -> float:
        return self._slider.value() / self._factor

    def set_valor(self, valor: float) -> None:
        self._slider.blockSignals(True)
        self._slider.setValue(int(valor * self._factor))
        self._actualizar_valor_label(valor)
        self._slider.blockSignals(False)


class ControlTemperaturaVista(QWidget):
    """Vista del panel de control de temperatura.

    Contiene selector de modo y paneles para parámetros
    senoidales (automático) y temperatura manual.

    Signals:
        modo_cambiado: Emitido cuando cambia el modo (True=manual).
        temperatura_base_cambiada: Emitido cuando cambia T_base.
        amplitud_cambiada: Emitido cuando cambia la amplitud.
        periodo_cambiado: Emitido cuando cambia el periodo.
        temperatura_manual_cambiada: Emitido cuando cambia T_manual.
    """

    modo_cambiado = pyqtSignal(bool)
    temperatura_base_cambiada = pyqtSignal(float)
    amplitud_cambiada = pyqtSignal(float)
    periodo_cambiado = pyqtSignal(float)
    temperatura_manual_cambiada = pyqtSignal(float)

    def __init__(
        self,
        rangos: Optional[RangosControl] = None,
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._rangos = rangos or RangosControl()
        self._setup_ui()
        self._conectar_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Selector de modo
        modo_layout = QHBoxLayout()
        modo_label = QLabel("Modo:")
        self._modo_combo = QComboBox()
        self._modo_combo.addItems(["Automático", "Manual"])
        modo_layout.addWidget(modo_label)
        modo_layout.addWidget(self._modo_combo, stretch=1)
        layout.addLayout(modo_layout)

        # Stack para paneles
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        # Panel automático (parámetros senoidales)
        self._panel_auto = QGroupBox("Parámetros de Variación Senoidal")
        panel_auto_layout = QVBoxLayout(self._panel_auto)

        self._slider_temp_base = SliderConValor(
            label="Temp. Base:",
            min_val=self._rangos.temp_min,
            max_val=self._rangos.temp_max,
            valor_inicial=22.0,
            sufijo="°C",
            decimales=1,
        )
        panel_auto_layout.addWidget(self._slider_temp_base)

        self._slider_amplitud = SliderConValor(
            label="Amplitud:",
            min_val=self._rangos.amplitud_min,
            max_val=self._rangos.amplitud_max,
            valor_inicial=5.0,
            sufijo="°C",
            decimales=1,
        )
        panel_auto_layout.addWidget(self._slider_amplitud)

        self._slider_periodo = SliderConValor(
            label="Periodo:",
            min_val=self._rangos.periodo_min,
            max_val=self._rangos.periodo_max,
            valor_inicial=60.0,
            sufijo="s",
            decimales=0,
        )
        panel_auto_layout.addWidget(self._slider_periodo)

        self._stack.addWidget(self._panel_auto)

        # Panel manual
        self._panel_manual = QGroupBox("Temperatura Manual")
        panel_manual_layout = QVBoxLayout(self._panel_manual)

        self._slider_manual = SliderConValor(
            label="Temperatura:",
            min_val=self._rangos.temp_min,
            max_val=self._rangos.temp_max,
            valor_inicial=22.0,
            sufijo="°C",
            decimales=1,
        )
        panel_manual_layout.addWidget(self._slider_manual)

        self._stack.addWidget(self._panel_manual)

    def _conectar_signals(self) -> None:
        self._modo_combo.currentIndexChanged.connect(self._on_modo_changed)
        self._slider_temp_base.valor_cambiado.connect(
            self.temperatura_base_cambiada.emit
        )
        self._slider_amplitud.valor_cambiado.connect(self.amplitud_cambiada.emit)
        self._slider_periodo.valor_cambiado.connect(self.periodo_cambiado.emit)
        self._slider_manual.valor_cambiado.connect(
            self.temperatura_manual_cambiada.emit
        )

    def _on_modo_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self.modo_cambiado.emit(index == 1)

    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo."""
        if not isinstance(modelo, ParametrosControl):
            return

        # Actualizar modo sin emitir signal
        self._modo_combo.blockSignals(True)
        self._modo_combo.setCurrentIndex(1 if modelo.es_manual else 0)
        self._stack.setCurrentIndex(1 if modelo.es_manual else 0)
        self._modo_combo.blockSignals(False)

        # Actualizar sliders
        self._slider_temp_base.set_valor(modelo.temperatura_base)
        self._slider_amplitud.set_valor(modelo.amplitud)
        self._slider_periodo.set_valor(modelo.periodo)
        self._slider_manual.set_valor(modelo.temperatura_manual)

    @property
    def temperatura_base(self) -> float:
        return self._slider_temp_base.valor

    @property
    def amplitud(self) -> float:
        return self._slider_amplitud.valor

    @property
    def periodo(self) -> float:
        return self._slider_periodo.valor

    @property
    def temperatura_manual(self) -> float:
        return self._slider_manual.valor

    @property
    def es_modo_manual(self) -> bool:
        return self._modo_combo.currentIndex() == 1
