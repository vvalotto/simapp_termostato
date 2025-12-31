"""Tests para StatusIndicator y LEDStatusIndicator."""
from compartido.widgets import (
    LEDStatusIndicator,
    LEDIndicator,
    LEDColor,
)


class TestLEDStatusIndicatorInit:
    """Tests de inicialización del LEDStatusIndicator."""

    def test_default_values(self, qtbot):
        """Verifica valores por defecto."""
        indicator = LEDStatusIndicator()
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert isinstance(indicator.led, LEDIndicator)
        assert indicator.led.color == LEDColor.GREEN
        assert indicator.led.led_size == 16

    def test_custom_color(self, qtbot):
        """Verifica inicialización con color personalizado."""
        indicator = LEDStatusIndicator(color=LEDColor.RED)
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert indicator.led.color == LEDColor.RED

    def test_custom_size(self, qtbot):
        """Verifica inicialización con tamaño personalizado."""
        indicator = LEDStatusIndicator(size=24)
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert indicator.led.led_size == 24


class TestLEDStatusIndicatorWidget:
    """Tests del widget retornado."""

    def test_get_widget_returns_led_indicator(self, qtbot):
        """Verifica que get_widget retorna el LEDIndicator."""
        indicator = LEDStatusIndicator()
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert widget is indicator.led

    def test_get_widget_is_qwidget(self, qtbot):
        """Verifica que el widget es un QWidget válido."""
        indicator = LEDStatusIndicator()
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert hasattr(widget, 'show')
        assert hasattr(widget, 'hide')


class TestLEDStatusIndicatorState:
    """Tests del estado del indicador."""

    def test_set_state_true(self, qtbot):
        """Verifica activar el indicador."""
        indicator = LEDStatusIndicator()
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        indicator.set_state(True)

        assert indicator.led.state is True

    def test_set_state_false(self, qtbot):
        """Verifica desactivar el indicador."""
        indicator = LEDStatusIndicator()
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        indicator.set_state(True)
        indicator.set_state(False)

        assert indicator.led.state is False

    def test_initial_state_off(self, qtbot):
        """Verifica estado inicial apagado."""
        indicator = LEDStatusIndicator()
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert indicator.led.state is False


class TestLEDStatusIndicatorColorProvider:
    """Tests del proveedor de colores."""

    def test_custom_color_provider(self, qtbot):
        """Verifica inyección de proveedor de colores."""
        from PyQt6.QtGui import QColor  # pylint: disable=no-name-in-module

        class CustomProvider:
            def get_color_on(self, color):
                return QColor(255, 0, 255)

            def get_color_off(self, color):
                return QColor(50, 0, 50)

        provider = CustomProvider()
        indicator = LEDStatusIndicator(color_provider=provider)
        widget = indicator.get_widget()
        qtbot.addWidget(widget)

        assert indicator.led.color_provider is provider
