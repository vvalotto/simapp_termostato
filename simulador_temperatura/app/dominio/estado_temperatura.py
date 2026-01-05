"""Modelo de datos para el estado de temperatura."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EstadoTemperatura:
    """Representa el estado actual de una lectura de temperatura.

    Attributes:
        temperatura: Valor de temperatura en grados Celsius.
        timestamp: Momento de la lectura.
        en_rango: Indica si la temperatura está dentro de los límites normales.
    """

    temperatura: float
    timestamp: datetime = field(default_factory=datetime.now)
    en_rango: bool = True

    def to_string(self) -> str:
        """Convierte la temperatura a formato de envío TCP.

        Returns:
            String con formato "<float>\n" con 1 decimal de precisión.
        """
        return f"{self.temperatura:.1f}\n"

    def validar_rango(self, temp_min: float, temp_max: float) -> bool:
        """Valida si la temperatura está dentro del rango especificado.

        Args:
            temp_min: Temperatura mínima permitida.
            temp_max: Temperatura máxima permitida.

        Returns:
            True si está en rango, False en caso contrario.
        """
        self.en_rango = temp_min <= self.temperatura <= temp_max
        return self.en_rango
