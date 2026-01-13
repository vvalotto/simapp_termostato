"""Modelo de datos para el Panel de Control de Bateria.

Contiene el estado del control de voltaje sin conocimiento de la UI.
"""

from dataclasses import dataclass

from ..base import ModeloBase


@dataclass
class ControlPanelModelo(ModeloBase):
    """Modelo que representa el estado del control de voltaje.

    Attributes:
        voltaje: Valor actual del voltaje en Volts.
        voltaje_minimo: Valor minimo permitido.
        voltaje_maximo: Valor maximo permitido.
        precision: Precision del control (paso del slider).
    """

    voltaje: float = 4.2
    voltaje_minimo: float = 0.0
    voltaje_maximo: float = 5.0
    precision: float = 0.1

    def set_voltaje(self, voltaje: float) -> None:
        """Establece el voltaje validando el rango.

        Args:
            voltaje: Nuevo valor de voltaje en Volts.
        """
        self.voltaje = max(
            self.voltaje_minimo,
            min(self.voltaje_maximo, voltaje)
        )

    @property
    def voltaje_normalizado(self) -> float:
        """Retorna el voltaje normalizado (0.0 a 1.0).

        Returns:
            Valor normalizado entre 0 y 1.
        """
        rango = self.voltaje_maximo - self.voltaje_minimo
        if rango <= 0:
            return 0.0
        return (self.voltaje - self.voltaje_minimo) / rango

    @property
    def pasos_slider(self) -> int:
        """Retorna el numero de pasos del slider.

        Returns:
            Numero de pasos basado en el rango y precision.
        """
        rango = self.voltaje_maximo - self.voltaje_minimo
        if self.precision <= 0:
            return 0
        return int(rango / self.precision)

    def voltaje_a_paso(self, voltaje: float) -> int:
        """Convierte un voltaje a posicion del slider.

        Args:
            voltaje: Valor de voltaje en Volts.

        Returns:
            Posicion del slider (entero).
        """
        if self.precision <= 0:
            return 0
        return int((voltaje - self.voltaje_minimo) / self.precision)

    def paso_a_voltaje(self, paso: int) -> float:
        """Convierte una posicion del slider a voltaje.

        Args:
            paso: Posicion del slider (entero).

        Returns:
            Valor de voltaje en Volts.
        """
        return self.voltaje_minimo + (paso * self.precision)
