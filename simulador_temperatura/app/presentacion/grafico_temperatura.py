"""Widget de gráfico de temperatura en tiempo real."""
from collections import deque
from dataclasses import dataclass
from typing import Optional
import time

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
import pyqtgraph as pg


@dataclass(frozen=True)
class ConfigGrafico:
    """Configuración del gráfico de temperatura."""

    ventana_segundos: int = 60
    temp_min_display: float = -10.0
    temp_max_display: float = 50.0
    max_puntos: int = 600  # 10 min a 1 sample/seg
    color_linea: str = "#4fc3f7"
    color_referencia: str = "#ff5252"
    ancho_linea: int = 2


class GraficoTemperatura(QWidget):
    """Widget de gráfico de temperatura en tiempo real usando pyqtgraph.

    Muestra la evolución de la temperatura con líneas de referencia
    para los límites mínimo y máximo.

    Signals:
        punto_agregado: Emitido cuando se agrega un nuevo punto.
    """

    punto_agregado = pyqtSignal(float, float)  # timestamp, temperatura

    def __init__(
        self,
        config: Optional[ConfigGrafico] = None,
        temp_min_referencia: Optional[float] = None,
        temp_max_referencia: Optional[float] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa el gráfico de temperatura.

        Args:
            config: Configuración del gráfico.
            temp_min_referencia: Temperatura mínima de referencia.
            temp_max_referencia: Temperatura máxima de referencia.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigGrafico()
        self._temp_min_ref = temp_min_referencia
        self._temp_max_ref = temp_max_referencia

        # Buffers circulares para datos
        self._timestamps: deque[float] = deque(maxlen=self._config.max_puntos)
        self._temperaturas: deque[float] = deque(maxlen=self._config.max_puntos)
        self._tiempo_inicio: Optional[float] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configurar tema oscuro para pyqtgraph
        pg.setConfigOptions(
            background="#1e1e1e",
            foreground="#d4d4d4",
            antialias=True,
        )

        # Crear widget de gráfico
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setLabel("left", "Temperatura", units="°C")
        self._plot_widget.setLabel("bottom", "Tiempo", units="s")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Configurar rango Y
        self._plot_widget.setYRange(
            self._config.temp_min_display,
            self._config.temp_max_display,
        )

        # Curva de temperatura
        self._curva = self._plot_widget.plot(
            pen=pg.mkPen(
                color=self._config.color_linea,
                width=self._config.ancho_linea,
            )
        )

        # Líneas de referencia
        self._linea_min: Optional[pg.InfiniteLine] = None
        self._linea_max: Optional[pg.InfiniteLine] = None

        if self._temp_min_ref is not None:
            self._linea_min = self._crear_linea_referencia(self._temp_min_ref)
            self._plot_widget.addItem(self._linea_min)

        if self._temp_max_ref is not None:
            self._linea_max = self._crear_linea_referencia(self._temp_max_ref)
            self._plot_widget.addItem(self._linea_max)

        layout.addWidget(self._plot_widget)

    def _crear_linea_referencia(self, posicion: float) -> pg.InfiniteLine:
        """Crea una línea horizontal de referencia.

        Args:
            posicion: Posición vertical de la línea (valor de temperatura).

        Returns:
            InfiniteLine configurada con el estilo de referencia.
        """
        return pg.InfiniteLine(
            pos=posicion,
            angle=0,
            pen=pg.mkPen(
                color=self._config.color_referencia,
                width=1,
                style=pg.QtCore.Qt.PenStyle.DashLine,
            ),
        )

    def add_punto(self, temperatura: float, timestamp: Optional[float] = None) -> None:
        """Agrega un nuevo punto al gráfico.

        Args:
            temperatura: Valor de temperatura a agregar.
            timestamp: Timestamp opcional (usa tiempo actual si no se provee).
        """
        if timestamp is None:
            timestamp = time.time()

        if self._tiempo_inicio is None:
            self._tiempo_inicio = timestamp

        # Tiempo relativo al inicio
        tiempo_relativo = timestamp - self._tiempo_inicio

        self._timestamps.append(tiempo_relativo)
        self._temperaturas.append(temperatura)

        self._actualizar_grafico()
        self.punto_agregado.emit(timestamp, temperatura)

    def _actualizar_grafico(self) -> None:
        """Actualiza la visualización del gráfico."""
        if not self._timestamps:
            return

        tiempos = list(self._timestamps)
        temps = list(self._temperaturas)

        self._curva.setData(tiempos, temps)

        # Ajustar eje X para mostrar ventana de tiempo
        tiempo_actual = tiempos[-1] if tiempos else 0
        x_min = max(0, tiempo_actual - self._config.ventana_segundos)
        x_max = max(self._config.ventana_segundos, tiempo_actual)
        self._plot_widget.setXRange(x_min, x_max)

    def clear(self) -> None:
        """Limpia todos los datos del gráfico."""
        self._timestamps.clear()
        self._temperaturas.clear()
        self._tiempo_inicio = None
        self._curva.setData([], [])

    def set_limites_referencia(
        self,
        temp_min: Optional[float] = None,
        temp_max: Optional[float] = None,
    ) -> None:
        """Actualiza las líneas de referencia.

        Args:
            temp_min: Nueva temperatura mínima de referencia.
            temp_max: Nueva temperatura máxima de referencia.
        """
        if temp_min is not None:
            self._temp_min_ref = temp_min
            if self._linea_min is not None:
                self._linea_min.setValue(temp_min)
            else:
                self._linea_min = self._crear_linea_referencia(temp_min)
                self._plot_widget.addItem(self._linea_min)

        if temp_max is not None:
            self._temp_max_ref = temp_max
            if self._linea_max is not None:
                self._linea_max.setValue(temp_max)
            else:
                self._linea_max = self._crear_linea_referencia(temp_max)
                self._plot_widget.addItem(self._linea_max)

    def set_ventana_tiempo(self, segundos: int) -> None:
        """Cambia la ventana de tiempo visible.

        Args:
            segundos: Nuevos segundos a mostrar en el eje X.
        """
        self._config = ConfigGrafico(
            ventana_segundos=segundos,
            temp_min_display=self._config.temp_min_display,
            temp_max_display=self._config.temp_max_display,
            max_puntos=self._config.max_puntos,
            color_linea=self._config.color_linea,
            color_referencia=self._config.color_referencia,
            ancho_linea=self._config.ancho_linea,
        )
        self._actualizar_grafico()

    @property
    def cantidad_puntos(self) -> int:
        """Retorna la cantidad de puntos en el gráfico."""
        return len(self._timestamps)

    @property
    def ultima_temperatura(self) -> Optional[float]:
        """Retorna la última temperatura registrada."""
        if self._temperaturas:
            return self._temperaturas[-1]
        return None
