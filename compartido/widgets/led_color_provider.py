"""
Proveedores de colores para LEDIndicator.

Define el enum de colores, el protocolo para proveer colores de LED
y una implementación por defecto, permitiendo extensibilidad sin
modificar LEDIndicator.
"""
# pylint: disable=no-name-in-module,unnecessary-ellipsis
from enum import Enum
from typing import Protocol
from PyQt6.QtGui import QColor


class LEDColor(Enum):
    """Colores disponibles para el LED."""
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"


class LEDColorProvider(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para proveedores de colores de LED.

    Permite inyectar diferentes paletas de colores al LEDIndicator
    sin modificar la clase, cumpliendo con el principio Open/Closed.

    Example:
        class CustomColorProvider:
            def get_color_on(self, color: LEDColor) -> QColor:
                # Colores personalizados para estado encendido
                ...

            def get_color_off(self, color: LEDColor) -> QColor:
                # Colores personalizados para estado apagado
                ...

        led = LEDIndicator(color_provider=CustomColorProvider())
    """

    def get_color_on(self, color: LEDColor) -> QColor:
        """
        Retorna el color para el estado encendido.

        Args:
            color: Tipo de color del LED.

        Returns:
            QColor para el estado encendido.
        """
        ...

    def get_color_off(self, color: LEDColor) -> QColor:
        """
        Retorna el color para el estado apagado.

        Args:
            color: Tipo de color del LED.

        Returns:
            QColor para el estado apagado.
        """
        ...


class DefaultLEDColorProvider:
    """
    Proveedor de colores por defecto para LEDIndicator.

    Implementa los colores estándar para LEDs: rojo, verde,
    amarillo y azul, tanto encendidos como apagados.
    """

    _COLORS_ON = {
        LEDColor.RED: QColor(255, 0, 0),
        LEDColor.GREEN: QColor(0, 255, 0),
        LEDColor.YELLOW: QColor(255, 255, 0),
        LEDColor.BLUE: QColor(0, 120, 255),
    }

    _COLORS_OFF = {
        LEDColor.RED: QColor(80, 0, 0),
        LEDColor.GREEN: QColor(0, 80, 0),
        LEDColor.YELLOW: QColor(80, 80, 0),
        LEDColor.BLUE: QColor(0, 40, 80),
    }

    def get_color_on(self, color: LEDColor) -> QColor:
        """Retorna el color para el estado encendido."""
        return QColor(self._COLORS_ON.get(color, self._COLORS_ON[LEDColor.GREEN]))

    def get_color_off(self, color: LEDColor) -> QColor:
        """Retorna el color para el estado apagado."""
        return QColor(self._COLORS_OFF.get(color, self._COLORS_OFF[LEDColor.GREEN]))
