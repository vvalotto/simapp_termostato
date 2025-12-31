"""
Widget LEDIndicator para mostrar estados binarios.

Proporciona un indicador visual circular tipo LED que puede estar
encendido o apagado, con colores configurables y efecto de brillo.
"""
# pylint: disable=no-name-in-module
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen

from .led_color_provider import LEDColor, LEDColorProvider, DefaultLEDColorProvider


class LEDIndicator(QWidget):
    """
    Widget que simula un indicador LED.

    Muestra un círculo que puede estar encendido o apagado,
    con efecto de brillo cuando está activo.

    El color del LED se obtiene mediante un LEDColorProvider inyectable,
    permitiendo personalizar los colores sin modificar esta clase (OCP).

    Attributes:
        state_changed: Señal emitida cuando cambia el estado.

    Example:
        led = LEDIndicator(color=LEDColor.GREEN)
        led.set_state(True)  # Enciende el LED
        led.state_changed.connect(on_led_changed)

        # Con proveedor de colores personalizado:
        led = LEDIndicator(color_provider=CustomColorProvider())
    """

    state_changed = pyqtSignal(bool)

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        parent: QWidget | None = None,
        color: LEDColor = LEDColor.GREEN,
        size: int = 20,
        state: bool = False,
        color_provider: LEDColorProvider | None = None
    ):
        """
        Inicializa el indicador LED.

        Args:
            parent: Widget padre.
            color: Color del LED (LEDColor).
            size: Diámetro del LED en píxeles.
            state: Estado inicial (True=encendido, False=apagado).
            color_provider: Proveedor de colores (opcional).
                           Si no se especifica, usa DefaultLEDColorProvider.
        """
        super().__init__(parent)
        self._color = color
        self._size = size
        self._state = state
        self._color_provider = color_provider or DefaultLEDColorProvider()

        self.setFixedSize(size, size)

    @property
    def state(self) -> bool:
        """Retorna el estado actual del LED."""
        return self._state

    @state.setter
    def state(self, value: bool) -> None:
        """Establece el estado del LED."""
        self.set_state(value)

    @property
    def color(self) -> LEDColor:
        """Retorna el color actual del LED."""
        return self._color

    @color.setter
    def color(self, value: LEDColor) -> None:
        """Establece el color del LED."""
        self.set_color(value)

    @property
    def led_size(self) -> int:
        """Retorna el tamaño del LED."""
        return self._size

    @led_size.setter
    def led_size(self, value: int) -> None:
        """Establece el tamaño del LED."""
        self.set_size(value)

    @property
    def color_provider(self) -> LEDColorProvider:
        """Retorna el proveedor de colores actual."""
        return self._color_provider

    def set_state(self, state: bool) -> None:
        """
        Cambia el estado del LED.

        Args:
            state: True para encender, False para apagar.
        """
        if self._state != state:
            self._state = state
            self.state_changed.emit(state)
            self.update()

    def set_color(self, color: LEDColor) -> None:
        """
        Cambia el color del LED.

        Args:
            color: Nuevo color (LEDColor).
        """
        if self._color != color:
            self._color = color
            self.update()

    def set_size(self, size: int) -> None:
        """
        Cambia el tamaño del LED.

        Args:
            size: Nuevo diámetro en píxeles.
        """
        if self._size != size:
            self._size = size
            self.setFixedSize(size, size)
            self.update()

    def set_color_provider(self, provider: LEDColorProvider) -> None:
        """
        Cambia el proveedor de colores.

        Args:
            provider: Nuevo proveedor de colores.
        """
        self._color_provider = provider
        self.update()

    def toggle(self) -> None:
        """Invierte el estado actual del LED."""
        self.set_state(not self._state)

    def sizeHint(self) -> QSize:  # pylint: disable=invalid-name
        """Retorna el tamaño sugerido del widget."""
        return QSize(self._size, self._size)

    def minimumSizeHint(self) -> QSize:  # pylint: disable=invalid-name
        """Retorna el tamaño mínimo del widget."""
        return QSize(self._size, self._size)

    def paintEvent(self, event) -> None:  # pylint: disable=invalid-name,unused-argument
        """Dibuja el LED con efecto de brillo si está encendido."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calcular dimensiones
        margin = 2
        diameter = self._size - (margin * 2)
        center_x = self._size / 2
        center_y = self._size / 2
        radius = diameter / 2

        if self._state:
            self._draw_led_on(painter, center_x, center_y, radius)
        else:
            self._draw_led_off(painter, center_x, center_y, radius)

        painter.end()

    def _draw_led_on(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        radius: float
    ) -> None:
        """Dibuja el LED en estado encendido con efecto de brillo."""
        base_color = self._color_provider.get_color_on(self._color)

        # Efecto de resplandor exterior (glow)
        glow_gradient = QRadialGradient(center_x, center_y, radius * 1.3)
        glow_color = QColor(base_color)
        glow_color.setAlpha(100)
        glow_gradient.setColorAt(0, glow_color)
        glow_color_transparent = QColor(base_color)
        glow_color_transparent.setAlpha(0)
        glow_gradient.setColorAt(1, glow_color_transparent)

        painter.setPen(QPen(QColor(0, 0, 0, 0)))
        painter.setBrush(glow_gradient)
        painter.drawEllipse(
            int(center_x - radius * 1.3),
            int(center_y - radius * 1.3),
            int(radius * 2.6),
            int(radius * 2.6)
        )

        # Gradiente principal del LED encendido
        gradient = QRadialGradient(
            center_x - radius * 0.3,
            center_y - radius * 0.3,
            radius * 1.2
        )

        # Color brillante en el centro (reflejo)
        highlight = QColor(255, 255, 255, 200)
        gradient.setColorAt(0, highlight)
        gradient.setColorAt(0.3, base_color)

        # Color más oscuro en el borde
        dark_color = QColor(base_color)
        dark_color.setRed(int(dark_color.red() * 0.6))
        dark_color.setGreen(int(dark_color.green() * 0.6))
        dark_color.setBlue(int(dark_color.blue() * 0.6))
        gradient.setColorAt(1, dark_color)

        # Dibujar el LED
        painter.setBrush(gradient)
        painter.setPen(QPen(dark_color, 1))
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )

    def _draw_led_off(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        radius: float
    ) -> None:
        """Dibuja el LED en estado apagado."""
        off_color = self._color_provider.get_color_off(self._color)

        # Gradiente para dar volumen al LED apagado
        gradient = QRadialGradient(
            center_x - radius * 0.3,
            center_y - radius * 0.3,
            radius * 1.2
        )

        # Ligeramente más claro en el centro
        light_off = QColor(off_color)
        light_off.setRed(min(255, int(light_off.red() * 1.3)))
        light_off.setGreen(min(255, int(light_off.green() * 1.3)))
        light_off.setBlue(min(255, int(light_off.blue() * 1.3)))
        gradient.setColorAt(0, light_off)
        gradient.setColorAt(0.5, off_color)

        # Más oscuro en el borde
        dark_off = QColor(off_color)
        dark_off.setRed(int(dark_off.red() * 0.7))
        dark_off.setGreen(int(dark_off.green() * 0.7))
        dark_off.setBlue(int(dark_off.blue() * 0.7))
        gradient.setColorAt(1, dark_off)

        # Dibujar el LED
        painter.setBrush(gradient)
        painter.setPen(QPen(dark_off, 1))
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2)
        )
