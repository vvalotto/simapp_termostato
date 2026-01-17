"""
Modelo de datos para el panel de Indicadores de Alerta.

Este módulo define el modelo MVC que representa el estado de los indicadores
LED de alerta del termostato (falla sensor y batería baja).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicadoresModelo:
    """
    Modelo inmutable que representa el estado de los indicadores de alerta.

    Attributes:
        falla_sensor: Indica si hay una falla en el sensor de temperatura
        bateria_baja: Indica si la batería del sistema está baja
    """

    falla_sensor: bool = False
    bateria_baja: bool = False

    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.

        Returns:
            dict: Representación del modelo como diccionario
        """
        return {
            "falla_sensor": self.falla_sensor,
            "bateria_baja": self.bateria_baja,
        }

    def tiene_alertas(self) -> bool:
        """
        Verifica si hay alguna alerta activa.

        Returns:
            bool: True si hay falla de sensor o batería baja, False en caso contrario
        """
        return self.falla_sensor or self.bateria_baja
