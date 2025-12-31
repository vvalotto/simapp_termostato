"""
Protocolo y adaptadores para indicadores de estado visual.

Define la abstracción para indicadores de estado binario y proporciona
un adaptador para LEDIndicator, permitiendo extensibilidad sin modificar
los widgets que usan indicadores.
"""
# pylint: disable=unnecessary-ellipsis
from typing import Protocol

from PyQt6.QtWidgets import QWidget  # pylint: disable=no-name-in-module

from .led_indicator import LEDIndicator
from .led_color_provider import LEDColor, LEDColorProvider


class StatusIndicator(Protocol):
    """
    Protocolo para indicadores de estado visual.

    Permite inyectar diferentes implementaciones de indicadores
    de estado sin modificar los widgets consumidores (OCP/DIP).

    Example:
        class CustomIndicator:
            def get_widget(self) -> QWidget:
                return self._my_widget

            def set_state(self, active: bool) -> None:
                self._my_widget.setActive(active)

        panel = ConfigPanel(status_indicator=CustomIndicator())
    """

    def get_widget(self) -> QWidget:
        """
        Retorna el widget visual del indicador.

        Returns:
            Widget Qt que representa el indicador.
        """
        ...

    def set_state(self, active: bool) -> None:
        """
        Establece el estado del indicador.

        Args:
            active: True para estado activo, False para inactivo.
        """
        ...


class LEDStatusIndicator:
    """
    Adaptador que envuelve LEDIndicator como StatusIndicator.

    Permite usar LEDIndicator en cualquier contexto que requiera
    un StatusIndicator, manteniendo la compatibilidad con el
    protocolo mientras aprovecha la funcionalidad existente.

    Example:
        indicator = LEDStatusIndicator(color=LEDColor.GREEN, size=16)
        panel = ConfigPanel(status_indicator=indicator)
    """

    def __init__(
        self,
        color: LEDColor = LEDColor.GREEN,
        size: int = 16,
        color_provider: LEDColorProvider | None = None
    ):
        """
        Inicializa el adaptador con un LEDIndicator.

        Args:
            color: Color del LED.
            size: Tamaño del LED en píxeles.
            color_provider: Proveedor de colores opcional.
        """
        self._led = LEDIndicator(
            color=color,
            size=size,
            color_provider=color_provider
        )

    def get_widget(self) -> QWidget:
        """Retorna el widget LEDIndicator."""
        return self._led

    def set_state(self, active: bool) -> None:
        """Establece el estado del LED."""
        self._led.set_state(active)

    @property
    def led(self) -> LEDIndicator:
        """Acceso directo al LEDIndicator subyacente."""
        return self._led
