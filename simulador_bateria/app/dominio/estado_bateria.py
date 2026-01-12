"""Modelo de datos para el estado de bateria."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EstadoBateria:
    """Representa el estado actual de una lectura de voltaje.

    Attributes:
        voltaje: Valor de voltaje en Volts.
        timestamp: Momento de la lectura.
        en_rango: Indica si el voltaje esta dentro de los limites.
    """

    voltaje: float
    timestamp: datetime = field(default_factory=datetime.now)
    en_rango: bool = True

    def to_string(self) -> str:
        """Convierte el voltaje a formato de envio TCP.

        Returns:
            String con formato "<float>\n" con 2 decimales de precision.
        """
        return f"{self.voltaje:.2f}\n"

    def validar_rango(self, voltaje_min: float, voltaje_max: float) -> bool:
        """Valida si el voltaje esta dentro del rango especificado.

        Args:
            voltaje_min: Voltaje minimo permitido.
            voltaje_max: Voltaje maximo permitido.

        Returns:
            True si esta en rango, False en caso contrario.
        """
        self.en_rango = voltaje_min <= self.voltaje <= voltaje_max
        return self.en_rango
