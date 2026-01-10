"""Modelo de datos para el Panel de Gráfico.

Contiene el buffer de datos de temperatura y configuración.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from ..base import ModeloBase


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


@dataclass
class PuntoTemperatura:
    """Un punto de dato de temperatura."""

    tiempo: float  # tiempo relativo en segundos
    temperatura: float


@dataclass
class DatosGrafico(ModeloBase):
    """Modelo que almacena los datos del gráfico.

    Attributes:
        config: Configuración visual del gráfico.
        temp_min_referencia: Línea de referencia inferior.
        temp_max_referencia: Línea de referencia superior.
    """

    config: ConfigGrafico = field(default_factory=ConfigGrafico)
    temp_min_referencia: Optional[float] = None
    temp_max_referencia: Optional[float] = None

    def __post_init__(self) -> None:
        """Inicializa los buffers circulares."""
        self._timestamps: deque[float] = deque(maxlen=self.config.max_puntos)
        self._temperaturas: deque[float] = deque(maxlen=self.config.max_puntos)
        self._tiempo_inicio: Optional[float] = None

    def agregar_punto(self, temperatura: float, timestamp: float) -> float:
        """Agrega un nuevo punto de datos.

        Args:
            temperatura: Valor de temperatura.
            timestamp: Timestamp absoluto.

        Returns:
            Tiempo relativo del punto agregado.
        """
        if self._tiempo_inicio is None:
            self._tiempo_inicio = timestamp

        tiempo_relativo = timestamp - self._tiempo_inicio
        self._timestamps.append(tiempo_relativo)
        self._temperaturas.append(temperatura)

        return tiempo_relativo

    def limpiar(self) -> None:
        """Limpia todos los datos del buffer."""
        self._timestamps.clear()
        self._temperaturas.clear()
        self._tiempo_inicio = None

    def obtener_datos(self) -> Tuple[List[float], List[float]]:
        """Retorna los datos actuales.

        Returns:
            Tupla con (tiempos, temperaturas).
        """
        return list(self._timestamps), list(self._temperaturas)

    @property
    def cantidad_puntos(self) -> int:
        """Retorna la cantidad de puntos almacenados."""
        return len(self._timestamps)

    @property
    def ultima_temperatura(self) -> Optional[float]:
        """Retorna la última temperatura registrada."""
        if self._temperaturas:
            return self._temperaturas[-1]
        return None

    @property
    def ultimo_tiempo(self) -> Optional[float]:
        """Retorna el último tiempo registrado."""
        if self._timestamps:
            return self._timestamps[-1]
        return None

    @property
    def tiene_datos(self) -> bool:
        """Indica si hay datos en el buffer."""
        return len(self._timestamps) > 0
