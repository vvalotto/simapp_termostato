"""
Modelo de datos para el panel Power (Encendido/Apagado).

Este módulo define el modelo MVC que representa el estado del botón
de encendido/apagado del termostato.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PowerModelo:
    """
    Modelo inmutable que representa el estado del botón power.

    Attributes:
        encendido: Estado del termostato (True=encendido, False=apagado)
    """

    encendido: bool = False

    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.

        Returns:
            dict: Representación del modelo como diccionario
        """
        return {
            "encendido": self.encendido,
        }
