"""Controlador para el Panel de Gráfico.

Coordina la comunicación entre el modelo de datos y la vista.
"""

import time
from typing import Optional, List, Tuple

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import DatosGrafico, ConfigGrafico
from .vista import GraficoTemperaturaVista


class GraficoControlador(ControladorBase[DatosGrafico, GraficoTemperaturaVista]):
    """Controlador del panel de gráfico de temperatura.

    Gestiona la adición de puntos y la actualización de la vista.

    Signals:
        punto_agregado: Emitido cuando se agrega un punto (timestamp, temp).
        grafico_limpiado: Emitido cuando se limpia el gráfico.
    """

    punto_agregado = pyqtSignal(float, float)  # timestamp, temperatura
    grafico_limpiado = pyqtSignal()

    def __init__(
        self,
        modelo: Optional[DatosGrafico] = None,
        vista: Optional[GraficoTemperaturaVista] = None,
        config: Optional[ConfigGrafico] = None,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador.

        Args:
            modelo: Modelo de datos, se crea uno si no se provee.
            vista: Vista del panel, se crea una si no se provee.
            config: Configuración del gráfico.
            parent: Objeto padre Qt opcional.
        """
        config = config or ConfigGrafico()
        modelo = modelo or DatosGrafico(config=config)
        vista = vista or GraficoTemperaturaVista(config=config)
        super().__init__(modelo, vista, parent)

    def _conectar_signals(self) -> None:
        """Conecta las señales (no hay señales de entrada en esta vista)."""
        pass

    def agregar_punto(
        self, temperatura: float, timestamp: Optional[float] = None
    ) -> None:
        """Agrega un nuevo punto al gráfico.

        Args:
            temperatura: Valor de temperatura a agregar.
            timestamp: Timestamp opcional (usa tiempo actual si no se provee).
        """
        if timestamp is None:
            timestamp = time.time()

        tiempo_relativo = self._modelo.agregar_punto(temperatura, timestamp)
        self._actualizar_vista()
        self.punto_agregado.emit(timestamp, temperatura)
        self.modelo_cambiado.emit(self._modelo)

    def limpiar(self) -> None:
        """Limpia todos los datos del gráfico."""
        self._modelo.limpiar()
        self._vista.limpiar()
        self.grafico_limpiado.emit()
        self.modelo_cambiado.emit(self._modelo)

    def set_limites_referencia(
        self,
        temp_min: Optional[float] = None,
        temp_max: Optional[float] = None
    ) -> None:
        """Actualiza las líneas de referencia.

        Args:
            temp_min: Nueva temperatura mínima de referencia.
            temp_max: Nueva temperatura máxima de referencia.
        """
        if temp_min is not None:
            self._modelo.temp_min_referencia = temp_min
        if temp_max is not None:
            self._modelo.temp_max_referencia = temp_max
        self._actualizar_vista()
        self.modelo_cambiado.emit(self._modelo)

    def obtener_datos(self) -> Tuple[List[float], List[float]]:
        """Retorna los datos actuales del gráfico.

        Returns:
            Tupla con (tiempos, temperaturas).
        """
        return self._modelo.obtener_datos()

    @property
    def cantidad_puntos(self) -> int:
        """Retorna la cantidad de puntos en el gráfico."""
        return self._modelo.cantidad_puntos

    @property
    def ultima_temperatura(self) -> Optional[float]:
        """Retorna la última temperatura registrada."""
        return self._modelo.ultima_temperatura

    @property
    def tiene_datos(self) -> bool:
        """Indica si hay datos en el gráfico."""
        return self._modelo.tiene_datos

    @property
    def config(self) -> ConfigGrafico:
        """Retorna la configuración del gráfico."""
        return self._modelo.config
