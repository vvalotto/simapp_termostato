"""
Modelo de datos para el panel Control de Temperatura.

Este módulo define el modelo MVC que representa el estado del panel
de control de temperatura (botones aumentar/disminuir).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlTempModelo:
    """
    Modelo inmutable que representa el estado del control de temperatura.

    Attributes:
        temperatura_deseada: Temperatura objetivo en °C (rango: 15.0 a 35.0)
        habilitado: Si el panel está activo (depende del estado power)
        temp_min: Temperatura mínima permitida en °C (15.0)
        temp_max: Temperatura máxima permitida en °C (35.0)
        incremento: Paso de incremento/decremento en °C (0.5)

    Example:
        >>> modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        >>> modelo.puede_aumentar()
        True
        >>> modelo.puede_disminuir()
        True
    """

    temperatura_deseada: float = 22.0
    habilitado: bool = False
    temp_min: float = 15.0
    temp_max: float = 35.0
    incremento: float = 0.5

    def puede_aumentar(self) -> bool:
        """
        Verifica si se puede aumentar la temperatura.

        Returns:
            True si el panel está habilitado y la temperatura actual
            es menor que el máximo permitido, False en caso contrario.

        Example:
            >>> modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=True)
            >>> modelo.puede_aumentar()
            False
            >>> modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
            >>> modelo.puede_aumentar()
            True
        """
        return self.habilitado and self.temperatura_deseada < self.temp_max

    def puede_disminuir(self) -> bool:
        """
        Verifica si se puede disminuir la temperatura.

        Returns:
            True si el panel está habilitado y la temperatura actual
            es mayor que el mínimo permitido, False en caso contrario.

        Example:
            >>> modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=True)
            >>> modelo.puede_disminuir()
            False
            >>> modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
            >>> modelo.puede_disminuir()
            True
        """
        return self.habilitado and self.temperatura_deseada > self.temp_min

    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.

        Returns:
            dict: Representación del modelo como diccionario con todas
                  las propiedades.

        Example:
            >>> modelo = ControlTempModelo(
            ...     temperatura_deseada=23.5, habilitado=True
            ... )
            >>> modelo.to_dict()
            {'temperatura_deseada': 23.5, 'habilitado': True,
             'temp_min': 15.0, 'temp_max': 35.0, 'incremento': 0.5}
        """
        return {
            "temperatura_deseada": self.temperatura_deseada,
            "habilitado": self.habilitado,
            "temp_min": self.temp_min,
            "temp_max": self.temp_max,
            "incremento": self.incremento,
        }
