"""Tests para el widget LEDIndicator."""
from unittest.mock import MagicMock
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor

from compartido.widgets import (
    LEDIndicator,
    LEDColor,
    LEDColorProvider,
    DefaultLEDColorProvider,
)


class TestLEDIndicatorInit:
    """Tests de inicialización del LEDIndicator."""

    def test_default_values(self, qtbot):
        """Verifica valores por defecto."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        assert led.state is False
        assert led.color == LEDColor.GREEN
        assert led.led_size == 20

    def test_custom_color(self, qtbot):
        """Verifica inicialización con color personalizado."""
        led = LEDIndicator(color=LEDColor.RED)
        qtbot.addWidget(led)

        assert led.color == LEDColor.RED

    def test_custom_size(self, qtbot):
        """Verifica inicialización con tamaño personalizado."""
        led = LEDIndicator(size=30)
        qtbot.addWidget(led)

        assert led.led_size == 30
        assert led.size() == QSize(30, 30)

    def test_custom_state(self, qtbot):
        """Verifica inicialización con estado encendido."""
        led = LEDIndicator(state=True)
        qtbot.addWidget(led)

        assert led.state is True

    def test_all_custom_parameters(self, qtbot):
        """Verifica inicialización con todos los parámetros personalizados."""
        led = LEDIndicator(color=LEDColor.BLUE, size=40, state=True)
        qtbot.addWidget(led)

        assert led.color == LEDColor.BLUE
        assert led.led_size == 40
        assert led.state is True

    def test_default_color_provider(self, qtbot):
        """Verifica que usa DefaultLEDColorProvider por defecto."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        assert isinstance(led.color_provider, DefaultLEDColorProvider)


class TestLEDIndicatorState:
    """Tests de cambio de estado."""

    def test_set_state_true(self, qtbot):
        """Verifica encender el LED."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.set_state(True)

        assert led.state is True

    def test_set_state_false(self, qtbot):
        """Verifica apagar el LED."""
        led = LEDIndicator(state=True)
        qtbot.addWidget(led)

        led.set_state(False)

        assert led.state is False

    def test_state_property_setter(self, qtbot):
        """Verifica cambio de estado mediante property."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.state = True

        assert led.state is True

    def test_toggle(self, qtbot):
        """Verifica toggle del estado."""
        led = LEDIndicator(state=False)
        qtbot.addWidget(led)

        led.toggle()
        assert led.state is True

        led.toggle()
        assert led.state is False

    def test_state_changed_signal_emitted(self, qtbot):
        """Verifica que se emite señal al cambiar estado."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        signal_received = []
        led.state_changed.connect(lambda s: signal_received.append(s))

        led.set_state(True)

        assert len(signal_received) == 1
        assert signal_received[0] is True

    def test_state_changed_signal_not_emitted_same_state(self, qtbot):
        """Verifica que no se emite señal si el estado es el mismo."""
        led = LEDIndicator(state=True)
        qtbot.addWidget(led)

        signal_received = []
        led.state_changed.connect(lambda s: signal_received.append(s))

        led.set_state(True)

        assert len(signal_received) == 0


class TestLEDIndicatorColor:
    """Tests de cambio de color."""

    def test_set_color(self, qtbot):
        """Verifica cambio de color."""
        led = LEDIndicator(color=LEDColor.GREEN)
        qtbot.addWidget(led)

        led.set_color(LEDColor.RED)

        assert led.color == LEDColor.RED

    def test_color_property_setter(self, qtbot):
        """Verifica cambio de color mediante property."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.color = LEDColor.YELLOW

        assert led.color == LEDColor.YELLOW

    def test_all_colors_available(self, qtbot):
        """Verifica que todos los colores funcionan."""
        for color in LEDColor:
            led = LEDIndicator(color=color)
            qtbot.addWidget(led)
            assert led.color == color


class TestLEDIndicatorSize:
    """Tests de cambio de tamaño."""

    def test_set_size(self, qtbot):
        """Verifica cambio de tamaño."""
        led = LEDIndicator(size=20)
        qtbot.addWidget(led)

        led.set_size(50)

        assert led.led_size == 50
        assert led.size() == QSize(50, 50)

    def test_led_size_property_setter(self, qtbot):
        """Verifica cambio de tamaño mediante property."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.led_size = 35

        assert led.led_size == 35

    def test_size_hint(self, qtbot):
        """Verifica sizeHint."""
        led = LEDIndicator(size=25)
        qtbot.addWidget(led)

        assert led.sizeHint() == QSize(25, 25)

    def test_minimum_size_hint(self, qtbot):
        """Verifica minimumSizeHint."""
        led = LEDIndicator(size=25)
        qtbot.addWidget(led)

        assert led.minimumSizeHint() == QSize(25, 25)


class TestLEDIndicatorRendering:
    """Tests de renderizado."""

    def test_paint_event_off(self, qtbot):
        """Verifica que el LED apagado se renderiza sin errores."""
        led = LEDIndicator(state=False)
        qtbot.addWidget(led)
        led.show()

        # Forzar repintado
        led.repaint()

        # Si llegamos aquí sin excepción, el test pasa
        assert True

    def test_paint_event_on(self, qtbot):
        """Verifica que el LED encendido se renderiza sin errores."""
        led = LEDIndicator(state=True)
        qtbot.addWidget(led)
        led.show()

        # Forzar repintado
        led.repaint()

        assert True

    def test_paint_all_colors_on(self, qtbot):
        """Verifica renderizado de todos los colores encendidos."""
        for color in LEDColor:
            led = LEDIndicator(color=color, state=True)
            qtbot.addWidget(led)
            led.show()
            led.repaint()

        assert True

    def test_paint_all_colors_off(self, qtbot):
        """Verifica renderizado de todos los colores apagados."""
        for color in LEDColor:
            led = LEDIndicator(color=color, state=False)
            qtbot.addWidget(led)
            led.show()
            led.repaint()

        assert True

    def test_update_called_on_state_change(self, qtbot):
        """Verifica que se llama update() al cambiar estado."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.update = MagicMock()
        led.set_state(True)

        led.update.assert_called_once()

    def test_update_called_on_color_change(self, qtbot):
        """Verifica que se llama update() al cambiar color."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.update = MagicMock()
        led.set_color(LEDColor.RED)

        led.update.assert_called_once()

    def test_update_called_on_size_change(self, qtbot):
        """Verifica que se llama update() al cambiar tamaño."""
        led = LEDIndicator()
        qtbot.addWidget(led)

        led.update = MagicMock()
        led.set_size(30)

        led.update.assert_called_once()


class TestLEDColorProvider:
    """Tests del proveedor de colores."""

    def test_custom_color_provider_injection(self, qtbot):
        """Verifica inyección de proveedor de colores personalizado."""
        class CustomProvider:
            def get_color_on(self, color: LEDColor) -> QColor:
                return QColor(255, 0, 255)  # Magenta

            def get_color_off(self, color: LEDColor) -> QColor:
                return QColor(50, 0, 50)

        provider = CustomProvider()
        led = LEDIndicator(color_provider=provider)
        qtbot.addWidget(led)

        assert led.color_provider is provider

    def test_set_color_provider(self, qtbot):
        """Verifica cambio de proveedor de colores."""
        class CustomProvider:
            def get_color_on(self, color: LEDColor) -> QColor:
                return QColor(255, 0, 255)

            def get_color_off(self, color: LEDColor) -> QColor:
                return QColor(50, 0, 50)

        led = LEDIndicator()
        qtbot.addWidget(led)

        assert isinstance(led.color_provider, DefaultLEDColorProvider)

        custom = CustomProvider()
        led.set_color_provider(custom)

        assert led.color_provider is custom

    def test_set_color_provider_triggers_update(self, qtbot):
        """Verifica que cambiar proveedor dispara update()."""
        class CustomProvider:
            def get_color_on(self, color: LEDColor) -> QColor:
                return QColor(255, 0, 255)

            def get_color_off(self, color: LEDColor) -> QColor:
                return QColor(50, 0, 50)

        led = LEDIndicator()
        qtbot.addWidget(led)

        led.update = MagicMock()
        led.set_color_provider(CustomProvider())

        led.update.assert_called_once()

    def test_render_with_custom_provider_on(self, qtbot):
        """Verifica que renderiza sin errores con proveedor personalizado encendido."""
        class MagentaProvider:
            def get_color_on(self, color: LEDColor) -> QColor:
                return QColor(255, 0, 255)

            def get_color_off(self, color: LEDColor) -> QColor:
                return QColor(50, 0, 50)

        led = LEDIndicator(color_provider=MagentaProvider(), state=True)
        qtbot.addWidget(led)
        led.show()
        led.repaint()

        # Si no hay excepción, el proveedor funciona
        assert True

    def test_render_with_custom_provider_off(self, qtbot):
        """Verifica que renderiza sin errores con proveedor personalizado apagado."""
        class MagentaProvider:
            def get_color_on(self, color: LEDColor) -> QColor:
                return QColor(255, 0, 255)

            def get_color_off(self, color: LEDColor) -> QColor:
                return QColor(50, 0, 50)

        led = LEDIndicator(color_provider=MagentaProvider(), state=False)
        qtbot.addWidget(led)
        led.show()
        led.repaint()

        # Si no hay excepción, el proveedor funciona
        assert True


class TestDefaultLEDColorProvider:
    """Tests del proveedor de colores por defecto."""

    def test_get_color_on_red(self):
        """Verifica color encendido rojo."""
        provider = DefaultLEDColorProvider()
        color = provider.get_color_on(LEDColor.RED)

        assert color.red() == 255
        assert color.green() == 0
        assert color.blue() == 0

    def test_get_color_on_green(self):
        """Verifica color encendido verde."""
        provider = DefaultLEDColorProvider()
        color = provider.get_color_on(LEDColor.GREEN)

        assert color.red() == 0
        assert color.green() == 255
        assert color.blue() == 0

    def test_get_color_on_yellow(self):
        """Verifica color encendido amarillo."""
        provider = DefaultLEDColorProvider()
        color = provider.get_color_on(LEDColor.YELLOW)

        assert color.red() == 255
        assert color.green() == 255
        assert color.blue() == 0

    def test_get_color_on_blue(self):
        """Verifica color encendido azul."""
        provider = DefaultLEDColorProvider()
        color = provider.get_color_on(LEDColor.BLUE)

        assert color.red() == 0
        assert color.green() == 120
        assert color.blue() == 255

    def test_get_color_off_darker(self):
        """Verifica que los colores apagados son más oscuros."""
        provider = DefaultLEDColorProvider()

        for led_color in LEDColor:
            on_color = provider.get_color_on(led_color)
            off_color = provider.get_color_off(led_color)

            # El color apagado debe ser más oscuro (valores RGB menores)
            assert off_color.red() <= on_color.red()
            assert off_color.green() <= on_color.green()
            assert off_color.blue() <= on_color.blue()

    def test_returns_new_qcolor_instances(self):
        """Verifica que retorna nuevas instancias de QColor."""
        provider = DefaultLEDColorProvider()

        color1 = provider.get_color_on(LEDColor.RED)
        color2 = provider.get_color_on(LEDColor.RED)

        # Deben ser objetos diferentes (no el mismo QColor)
        assert color1 is not color2
        # Pero con los mismos valores
        assert color1.red() == color2.red()
