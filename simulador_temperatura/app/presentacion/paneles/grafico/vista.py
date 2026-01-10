"""Vista para el Panel de Gráfico.

Responsable de la visualización del gráfico de temperatura.
"""

from typing import Optional, List

from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg

from ..base import ModeloBase
from .modelo import DatosGrafico, ConfigGrafico


class GraficoTemperaturaVista(QWidget):
    """Vista del gráfico de temperatura usando pyqtgraph.

    Muestra la evolución de la temperatura con líneas de referencia
    para los límites mínimo y máximo.

    Implementa la interfaz de VistaBase sin herencia directa
    para evitar conflictos de metaclase con QWidget.
    """

    def __init__(
        self,
        config: Optional[ConfigGrafico] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa la vista del gráfico.

        Args:
            config: Configuración visual del gráfico.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigGrafico()
        self._linea_min: Optional[pg.InfiniteLine] = None
        self._linea_max: Optional[pg.InfiniteLine] = None
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

        layout.addWidget(self._plot_widget)

    def _crear_linea_referencia(self, posicion: float) -> pg.InfiniteLine:
        """Crea una línea horizontal de referencia.

        Args:
            posicion: Posición vertical de la línea.

        Returns:
            InfiniteLine configurada.
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

    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo.

        Args:
            modelo: Instancia de DatosGrafico con los datos.
        """
        if not isinstance(modelo, DatosGrafico):
            return

        # Actualizar datos de la curva
        tiempos, temperaturas = modelo.obtener_datos()
        self._curva.setData(tiempos, temperaturas)

        # Ajustar eje X para mostrar ventana de tiempo
        if tiempos:
            tiempo_actual = tiempos[-1]
            x_min = max(0, tiempo_actual - modelo.config.ventana_segundos)
            x_max = max(modelo.config.ventana_segundos, tiempo_actual)
            self._plot_widget.setXRange(x_min, x_max)

        # Actualizar líneas de referencia
        self._actualizar_linea_referencia_min(modelo.temp_min_referencia)
        self._actualizar_linea_referencia_max(modelo.temp_max_referencia)

    def _actualizar_linea_referencia_min(self, valor: Optional[float]) -> None:
        """Actualiza la línea de referencia mínima."""
        if valor is not None:
            if self._linea_min is not None:
                self._linea_min.setValue(valor)
            else:
                self._linea_min = self._crear_linea_referencia(valor)
                self._plot_widget.addItem(self._linea_min)
        elif self._linea_min is not None:
            self._plot_widget.removeItem(self._linea_min)
            self._linea_min = None

    def _actualizar_linea_referencia_max(self, valor: Optional[float]) -> None:
        """Actualiza la línea de referencia máxima."""
        if valor is not None:
            if self._linea_max is not None:
                self._linea_max.setValue(valor)
            else:
                self._linea_max = self._crear_linea_referencia(valor)
                self._plot_widget.addItem(self._linea_max)
        elif self._linea_max is not None:
            self._plot_widget.removeItem(self._linea_max)
            self._linea_max = None

    def dibujar_datos(
        self, tiempos: List[float], temperaturas: List[float]
    ) -> None:
        """Dibuja los datos directamente en el gráfico.

        Args:
            tiempos: Lista de tiempos relativos.
            temperaturas: Lista de temperaturas.
        """
        self._curva.setData(tiempos, temperaturas)

        if tiempos:
            tiempo_actual = tiempos[-1]
            x_min = max(0, tiempo_actual - self._config.ventana_segundos)
            x_max = max(self._config.ventana_segundos, tiempo_actual)
            self._plot_widget.setXRange(x_min, x_max)

    def limpiar(self) -> None:
        """Limpia el gráfico."""
        self._curva.setData([], [])

    @property
    def plot_widget(self) -> pg.PlotWidget:
        """Retorna el widget de plot para acceso directo."""
        return self._plot_widget
