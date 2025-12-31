"""
Widgets reutilizables para las aplicaciones del proyecto.

Este módulo contiene componentes visuales PyQt6 compartidos
entre los simuladores y la interfaz UX.
"""
from .led_color_provider import LEDColor, LEDColorProvider, DefaultLEDColorProvider
from .led_indicator import LEDIndicator

__all__ = [
    "LEDIndicator",
    "LEDColor",
    "LEDColorProvider",
    "DefaultLEDColorProvider",
]
