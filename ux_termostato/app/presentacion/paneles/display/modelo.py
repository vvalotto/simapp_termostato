"""
Modelo de datos para el panel Display LCD.

Este módulo define el modelo MVC que representa el estado del display principal
del termostato, que muestra la temperatura actual o deseada.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DisplayModelo:
    """
    Modelo inmutable que representa el estado del display LCD.

    Attributes:
        temperatura: Valor de temperatura a mostrar (°C)
        modo_vista: Modo de visualización ("ambiente" | "deseada")
        encendido: Si el termostato está encendido
        error_sensor: Si hay error en el sensor de temperatura
    """

    temperatura: float = 0.0
    modo_vista: str = "ambiente"  # "ambiente" | "deseada"
    encendido: bool = True
    error_sensor: bool = False

    def __post_init__(self):
        """Valida los valores del modelo después de la inicialización."""
        if self.modo_vista not in ("ambiente", "deseada"):
            raise ValueError(
                f"modo_vista debe ser 'ambiente' o 'deseada', "
                f"recibido: {self.modo_vista}"
            )

    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.

        Returns:
            dict: Representación del modelo como diccionario
        """
        return {
            "temperatura": self.temperatura,
            "modo_vista": self.modo_vista,
            "encendido": self.encendido,
            "error_sensor": self.error_sensor,
        }
