"""Widget de control de parámetros de simulación de temperatura."""
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


@dataclass(frozen=True)
class ParametrosSenoidal:
    """Parámetros de variación senoidal."""

    temperatura_base: float
    amplitud: float
    periodo: float


@dataclass(frozen=True)
class RangosControl:
    """Rangos configurables para los controles de temperatura."""

    temp_min: float = -10.0
    temp_max: float = 50.0
    amplitud_min: float = 0.0
    amplitud_max: float = 20.0
    periodo_min: float = 10.0
    periodo_max: float = 300.0


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


class PanelParametrosSenoidal(QGroupBox):
    """Panel con controles para parámetros de variación senoidal.

    Responsabilidad única: gestionar los 3 sliders de modo automático.
    """

    parametros_cambiados = pyqtSignal(object)  # ParametrosSenoidal

    def __init__(
        self,
        parametros_iniciales: ParametrosSenoidal,
        rangos: RangosControl,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__("Parámetros de Variación Senoidal", parent)
        self._rangos = rangos
        self._setup_ui(parametros_iniciales)
        self._conectar_signals()

    def _setup_ui(self, parametros: ParametrosSenoidal) -> None:
        layout = QVBoxLayout(self)

        self._slider_temp_base = SliderConValor(
            label="Temp. Base:",
            min_val=self._rangos.temp_min,
            max_val=self._rangos.temp_max,
            valor_inicial=parametros.temperatura_base,
            sufijo="°C",
            decimales=1,
        )
        layout.addWidget(self._slider_temp_base)

        self._slider_amplitud = SliderConValor(
            label="Amplitud:",
            min_val=self._rangos.amplitud_min,
            max_val=self._rangos.amplitud_max,
            valor_inicial=parametros.amplitud,
            sufijo="°C",
            decimales=1,
        )
        layout.addWidget(self._slider_amplitud)

        self._slider_periodo = SliderConValor(
            label="Periodo:",
            min_val=self._rangos.periodo_min,
            max_val=self._rangos.periodo_max,
            valor_inicial=parametros.periodo,
            sufijo="s",
            decimales=0,
        )
        layout.addWidget(self._slider_periodo)

    def _conectar_signals(self) -> None:
        self._slider_temp_base.valor_cambiado.connect(self._on_parametro_changed)
        self._slider_amplitud.valor_cambiado.connect(self._on_parametro_changed)
        self._slider_periodo.valor_cambiado.connect(self._on_parametro_changed)

    def _on_parametro_changed(self, _: float) -> None:
        self.parametros_cambiados.emit(self.parametros)

    @property
    def parametros(self) -> ParametrosSenoidal:
        return ParametrosSenoidal(
            temperatura_base=self._slider_temp_base.valor,
            amplitud=self._slider_amplitud.valor,
            periodo=self._slider_periodo.valor,
        )

    def set_parametros(self, parametros: ParametrosSenoidal) -> None:
        self._slider_temp_base.set_valor(parametros.temperatura_base)
        self._slider_amplitud.set_valor(parametros.amplitud)
        self._slider_periodo.set_valor(parametros.periodo)


class PanelTemperaturaManual(QGroupBox):
    """Panel con control de temperatura manual.

    Responsabilidad única: gestionar el slider de temperatura manual.
    """

    temperatura_cambiada = pyqtSignal(float)

    def __init__(
        self,
        temperatura_inicial: float,
        rangos: RangosControl,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__("Temperatura Manual", parent)
        self._setup_ui(temperatura_inicial, rangos)

    def _setup_ui(self, temperatura_inicial: float, rangos: RangosControl) -> None:
        layout = QVBoxLayout(self)

        self._slider = SliderConValor(
            label="Temperatura:",
            min_val=rangos.temp_min,
            max_val=rangos.temp_max,
            valor_inicial=temperatura_inicial,
            sufijo="°C",
            decimales=1,
        )
        self._slider.valor_cambiado.connect(self.temperatura_cambiada.emit)
        layout.addWidget(self._slider)

    @property
    def temperatura(self) -> float:
        return self._slider.valor

    def set_temperatura(self, temperatura: float) -> None:
        self._slider.set_valor(temperatura)


class ControlTemperatura(QWidget):
    """Widget compositor para controlar parámetros de simulación.

    Coordina el selector de modo y los paneles de configuración.
    Sigue el principio de composición sobre herencia.

    Signals:
        modo_cambiado: Emitido cuando cambia el modo (True=manual).
        temperatura_manual_cambiada: Emitido en modo manual.
        parametros_senoidal_cambiados: Emitido en modo automático.
    """

    modo_cambiado = pyqtSignal(bool)
    temperatura_manual_cambiada = pyqtSignal(float)
    parametros_senoidal_cambiados = pyqtSignal(object)  # ParametrosSenoidal

    def __init__(
        self,
        temperatura_inicial: float = 20.0,
        amplitud_inicial: float = 5.0,
        periodo_inicial: float = 60.0,
        rangos: Optional[RangosControl] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._rangos = rangos or RangosControl()
        self._parametros_iniciales = ParametrosSenoidal(
            temperatura_base=temperatura_inicial,
            amplitud=amplitud_inicial,
            periodo=periodo_inicial,
        )
        self._temperatura_inicial = temperatura_inicial

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

        # Paneles delegados
        self._panel_senoidal = PanelParametrosSenoidal(
            parametros_iniciales=self._parametros_iniciales,
            rangos=self._rangos,
        )
        self._stack.addWidget(self._panel_senoidal)

        self._panel_manual = PanelTemperaturaManual(
            temperatura_inicial=self._temperatura_inicial,
            rangos=self._rangos,
        )
        self._stack.addWidget(self._panel_manual)

    def _conectar_signals(self) -> None:
        self._modo_combo.currentIndexChanged.connect(self._on_modo_changed)
        self._panel_senoidal.parametros_cambiados.connect(
            self.parametros_senoidal_cambiados.emit
        )
        self._panel_manual.temperatura_cambiada.connect(
            self.temperatura_manual_cambiada.emit
        )

    def _on_modo_changed(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        self.modo_cambiado.emit(index == 1)

    @property
    def es_modo_manual(self) -> bool:
        return self._modo_combo.currentIndex() == 1

    @property
    def parametros_senoidal(self) -> ParametrosSenoidal:
        return self._panel_senoidal.parametros

    @property
    def temperatura_manual(self) -> float:
        return self._panel_manual.temperatura

    # Propiedades de conveniencia para acceso directo
    @property
    def temperatura_base(self) -> float:
        return self._panel_senoidal.parametros.temperatura_base

    @property
    def amplitud(self) -> float:
        return self._panel_senoidal.parametros.amplitud

    @property
    def periodo(self) -> float:
        return self._panel_senoidal.parametros.periodo

    def set_modo(self, manual: bool) -> None:
        self._modo_combo.blockSignals(True)
        self._modo_combo.setCurrentIndex(1 if manual else 0)
        self._stack.setCurrentIndex(1 if manual else 0)
        self._modo_combo.blockSignals(False)

    def set_parametros_senoidal(self, parametros: ParametrosSenoidal) -> None:
        self._panel_senoidal.set_parametros(parametros)

    def set_temperatura_manual(self, temperatura: float) -> None:
        self._panel_manual.set_temperatura(temperatura)
