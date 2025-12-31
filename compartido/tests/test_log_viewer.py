"""Tests para el widget LogViewer y componentes relacionados."""
from datetime import datetime
from unittest.mock import MagicMock

from PyQt6.QtGui import QColor  # pylint: disable=no-name-in-module

from compartido.widgets import (
    LogViewer,
    LogViewerLabels,
    LogLevel,
    LogColorProvider,
    DefaultLogColorProvider,
    LogFormatter,
    TimestampLogFormatter,
)


class TestLogViewerInit:
    """Tests de inicialización del LogViewer."""

    def test_default_values(self, qtbot):
        """Verifica valores por defecto."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        assert viewer.max_lines == 1000
        assert viewer.auto_scroll is True
        assert viewer.line_count == 0

    def test_custom_max_lines(self, qtbot):
        """Verifica inicialización con max_lines personalizado."""
        viewer = LogViewer(max_lines=500)
        qtbot.addWidget(viewer)

        assert viewer.max_lines == 500

    def test_custom_auto_scroll(self, qtbot):
        """Verifica inicialización con auto_scroll desactivado."""
        viewer = LogViewer(auto_scroll=False)
        qtbot.addWidget(viewer)

        assert viewer.auto_scroll is False

    def test_default_color_provider(self, qtbot):
        """Verifica que usa DefaultLogColorProvider por defecto."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        assert isinstance(viewer.color_provider, DefaultLogColorProvider)

    def test_default_formatter(self, qtbot):
        """Verifica que usa TimestampLogFormatter por defecto."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        assert isinstance(viewer.formatter, TimestampLogFormatter)

    def test_default_labels(self, qtbot):
        """Verifica etiquetas por defecto."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        assert viewer.labels.clear_button == "Limpiar"
        assert viewer.labels.auto_scroll_checkbox == "Auto-scroll"


class TestLogViewerAddLog:
    """Tests del método add_log."""

    def test_add_log_increments_line_count(self, qtbot):
        """Verifica que agregar log incrementa contador."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.add_log("Test message", LogLevel.INFO)

        assert viewer.line_count == 1

    def test_add_multiple_logs(self, qtbot):
        """Verifica agregar múltiples logs."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.add_log("Message 1", LogLevel.INFO)
        viewer.add_log("Message 2", LogLevel.WARNING)
        viewer.add_log("Message 3", LogLevel.ERROR)

        assert viewer.line_count == 3

    def test_add_log_emits_signal(self, qtbot):
        """Verifica que add_log emite señal."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        signals_received = []
        viewer.log_added.connect(lambda msg, lvl: signals_received.append((msg, lvl)))

        viewer.add_log("Test", LogLevel.WARNING)

        assert len(signals_received) == 1
        assert signals_received[0] == ("Test", LogLevel.WARNING)

    def test_add_log_contains_message(self, qtbot):
        """Verifica que el mensaje aparece en el texto."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.add_log("Conexión establecida", LogLevel.INFO)

        assert "Conexión establecida" in viewer.get_text()

    def test_add_log_with_custom_timestamp(self, qtbot):
        """Verifica log con timestamp personalizado."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        custom_time = datetime(2024, 1, 15, 10, 30, 45)
        viewer.add_log("Test", LogLevel.INFO, timestamp=custom_time)

        assert "10:30:45" in viewer.get_text()


class TestLogViewerConvenienceMethods:
    """Tests de los métodos de conveniencia."""

    def test_add_info(self, qtbot):
        """Verifica método add_info."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        signals = []
        viewer.log_added.connect(lambda msg, lvl: signals.append(lvl))

        viewer.add_info("Info message")

        assert signals[0] == LogLevel.INFO

    def test_add_warning(self, qtbot):
        """Verifica método add_warning."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        signals = []
        viewer.log_added.connect(lambda msg, lvl: signals.append(lvl))

        viewer.add_warning("Warning message")

        assert signals[0] == LogLevel.WARNING

    def test_add_error(self, qtbot):
        """Verifica método add_error."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        signals = []
        viewer.log_added.connect(lambda msg, lvl: signals.append(lvl))

        viewer.add_error("Error message")

        assert signals[0] == LogLevel.ERROR

    def test_add_debug(self, qtbot):
        """Verifica método add_debug."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        signals = []
        viewer.log_added.connect(lambda msg, lvl: signals.append(lvl))

        viewer.add_debug("Debug message")

        assert signals[0] == LogLevel.DEBUG


class TestLogViewerLineLimit:
    """Tests del límite de líneas."""

    def test_respects_max_lines(self, qtbot):
        """Verifica que se respeta el límite de líneas."""
        viewer = LogViewer(max_lines=5)
        qtbot.addWidget(viewer)

        for i in range(10):
            viewer.add_log(f"Message {i}", LogLevel.INFO)

        assert viewer.line_count == 5

    def test_removes_oldest_lines(self, qtbot):
        """Verifica que se eliminan las líneas más antiguas."""
        viewer = LogViewer(max_lines=3)
        qtbot.addWidget(viewer)

        viewer.add_log("First", LogLevel.INFO)
        viewer.add_log("Second", LogLevel.INFO)
        viewer.add_log("Third", LogLevel.INFO)
        viewer.add_log("Fourth", LogLevel.INFO)

        text = viewer.get_text()
        assert "First" not in text
        assert "Fourth" in text

    def test_change_max_lines_applies_limit(self, qtbot):
        """Verifica que cambiar max_lines aplica el límite."""
        viewer = LogViewer(max_lines=100)
        qtbot.addWidget(viewer)

        for i in range(10):
            viewer.add_log(f"Message {i}", LogLevel.INFO)

        assert viewer.line_count == 10

        viewer.max_lines = 5

        assert viewer.line_count == 5

    def test_max_lines_minimum_is_one(self, qtbot):
        """Verifica que max_lines mínimo es 1."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.max_lines = 0

        assert viewer.max_lines == 1

        viewer.max_lines = -5

        assert viewer.max_lines == 1


class TestLogViewerClear:
    """Tests de limpieza de logs."""

    def test_clear_logs_empties_text(self, qtbot):
        """Verifica que clear_logs vacía el texto."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.add_log("Test", LogLevel.INFO)
        viewer.clear_logs()

        assert viewer.get_text() == ""

    def test_clear_logs_resets_line_count(self, qtbot):
        """Verifica que clear_logs resetea contador."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.add_log("Test 1", LogLevel.INFO)
        viewer.add_log("Test 2", LogLevel.INFO)
        viewer.clear_logs()

        assert viewer.line_count == 0

    def test_clear_logs_emits_signal(self, qtbot):
        """Verifica que clear_logs emite señal."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        signals = []
        viewer.logs_cleared.connect(lambda: signals.append(True))

        viewer.clear_logs()

        assert len(signals) == 1

    def test_clear_button_clears_logs(self, qtbot):
        """Verifica que el botón limpia los logs."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        viewer.add_log("Test", LogLevel.INFO)
        viewer._clear_button.click()

        assert viewer.line_count == 0


class TestLogViewerAutoScroll:
    """Tests de auto-scroll."""

    def test_auto_scroll_property_setter(self, qtbot):
        """Verifica setter de auto_scroll."""
        viewer = LogViewer(auto_scroll=True)
        qtbot.addWidget(viewer)

        viewer.auto_scroll = False

        assert viewer.auto_scroll is False
        assert viewer._auto_scroll_checkbox.isChecked() is False

    def test_checkbox_updates_auto_scroll(self, qtbot):
        """Verifica que checkbox actualiza auto_scroll."""
        viewer = LogViewer(auto_scroll=True)
        qtbot.addWidget(viewer)

        viewer._auto_scroll_checkbox.setChecked(False)

        assert viewer.auto_scroll is False


class TestLogViewerDependencyInjection:
    """Tests de inyección de dependencias."""

    def test_custom_color_provider(self, qtbot):
        """Verifica inyección de color provider personalizado."""
        class CustomColorProvider:
            def get_color(self, level: LogLevel) -> QColor:
                return QColor(128, 128, 128)

        provider = CustomColorProvider()
        viewer = LogViewer(color_provider=provider)
        qtbot.addWidget(viewer)

        assert viewer.color_provider is provider

    def test_custom_formatter(self, qtbot):
        """Verifica inyección de formatter personalizado."""
        class CustomFormatter:
            def format(self, message: str, level: LogLevel, timestamp: datetime) -> str:
                return f"CUSTOM: {message}"

        formatter = CustomFormatter()
        viewer = LogViewer(formatter=formatter)
        qtbot.addWidget(viewer)

        assert viewer.formatter is formatter

    def test_custom_labels(self, qtbot):
        """Verifica inyección de labels personalizadas."""
        labels = LogViewerLabels(
            clear_button="Clear",
            auto_scroll_checkbox="Auto-scroll enabled"
        )
        viewer = LogViewer(labels=labels)
        qtbot.addWidget(viewer)

        assert viewer.labels is labels
        assert viewer._clear_button.text() == "Clear"

    def test_custom_formatter_used_in_output(self, qtbot):
        """Verifica que se usa el formatter personalizado."""
        class PrefixFormatter:
            def format(self, message: str, level: LogLevel, timestamp: datetime) -> str:
                return f">>>{message}<<<"

        viewer = LogViewer(formatter=PrefixFormatter())
        qtbot.addWidget(viewer)

        viewer.add_log("Test", LogLevel.INFO)

        assert ">>>Test<<<" in viewer.get_text()

    def test_set_color_provider(self, qtbot):
        """Verifica cambio de color provider en runtime."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        new_provider = MagicMock(spec=LogColorProvider)
        new_provider.get_color.return_value = QColor(255, 0, 0)

        viewer.set_color_provider(new_provider)
        viewer.add_log("Test", LogLevel.INFO)

        new_provider.get_color.assert_called_with(LogLevel.INFO)

    def test_set_formatter(self, qtbot):
        """Verifica cambio de formatter en runtime."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        new_formatter = MagicMock(spec=LogFormatter)
        new_formatter.format.return_value = "FORMATTED"

        viewer.set_formatter(new_formatter)
        viewer.add_log("Test", LogLevel.INFO)

        new_formatter.format.assert_called()


class TestDefaultLogColorProvider:
    """Tests del proveedor de colores por defecto."""

    def test_info_color_is_white(self):
        """Verifica color INFO es blanco."""
        provider = DefaultLogColorProvider()
        color = provider.get_color(LogLevel.INFO)

        assert color.red() == 255
        assert color.green() == 255
        assert color.blue() == 255

    def test_warning_color_is_yellow(self):
        """Verifica color WARNING es amarillo."""
        provider = DefaultLogColorProvider()
        color = provider.get_color(LogLevel.WARNING)

        assert color.red() == 255
        assert color.green() == 255
        assert color.blue() == 0

    def test_error_color_is_red(self):
        """Verifica color ERROR es rojo claro."""
        provider = DefaultLogColorProvider()
        color = provider.get_color(LogLevel.ERROR)

        assert color.red() == 255
        assert color.green() == 100
        assert color.blue() == 100

    def test_debug_color_is_gray(self):
        """Verifica color DEBUG es gris."""
        provider = DefaultLogColorProvider()
        color = provider.get_color(LogLevel.DEBUG)

        assert color.red() == 180
        assert color.green() == 180
        assert color.blue() == 180

    def test_returns_new_qcolor_instances(self):
        """Verifica que retorna nuevas instancias."""
        provider = DefaultLogColorProvider()

        color1 = provider.get_color(LogLevel.INFO)
        color2 = provider.get_color(LogLevel.INFO)

        assert color1 is not color2


class TestTimestampLogFormatter:
    """Tests del formateador con timestamp."""

    def test_default_format(self):
        """Verifica formato por defecto."""
        formatter = TimestampLogFormatter()
        timestamp = datetime(2024, 1, 15, 14, 30, 45)

        result = formatter.format("Test message", LogLevel.INFO, timestamp)

        assert "[14:30:45]" in result
        assert "[INFO]" in result
        assert "Test message" in result

    def test_custom_time_format(self):
        """Verifica formato de tiempo personalizado."""
        formatter = TimestampLogFormatter(time_format="%Y-%m-%d %H:%M")
        timestamp = datetime(2024, 1, 15, 14, 30, 45)

        result = formatter.format("Test", LogLevel.INFO, timestamp)

        assert "2024-01-15 14:30" in result

    def test_without_level(self):
        """Verifica formato sin nivel."""
        formatter = TimestampLogFormatter(show_level=False)
        timestamp = datetime(2024, 1, 15, 14, 30, 45)

        result = formatter.format("Test", LogLevel.WARNING, timestamp)

        assert "[WARNING]" not in result
        assert "Test" in result

    def test_all_levels_formatted(self):
        """Verifica que todos los niveles se formatean."""
        formatter = TimestampLogFormatter()
        timestamp = datetime.now()

        for level in LogLevel:
            result = formatter.format("Test", level, timestamp)
            assert level.value.upper() in result

    def test_properties(self):
        """Verifica propiedades del formatter."""
        formatter = TimestampLogFormatter(
            time_format="%H:%M",
            show_level=False
        )

        assert formatter.time_format == "%H:%M"
        assert formatter.show_level is False


class TestLogViewerRendering:
    """Tests de renderizado."""

    def test_renders_without_error(self, qtbot):
        """Verifica que el viewer se renderiza sin errores."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)
        viewer.show()

        assert True

    def test_text_area_is_readonly(self, qtbot):
        """Verifica que el área de texto es solo lectura."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)

        assert viewer._text_area.isReadOnly() is True

    def test_all_controls_visible(self, qtbot):
        """Verifica que todos los controles son visibles."""
        viewer = LogViewer()
        qtbot.addWidget(viewer)
        viewer.show()

        assert viewer._text_area.isVisible()
        assert viewer._clear_button.isVisible()
        assert viewer._auto_scroll_checkbox.isVisible()
