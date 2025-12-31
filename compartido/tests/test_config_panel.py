"""Tests para el widget ConfigPanel."""
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QWidget  # pylint: disable=no-name-in-module

from compartido.widgets import (
    ConfigPanel,
    ConfigPanelLabels,
    IPValidator,
    DefaultIPValidator,
    StatusIndicator,
    LEDStatusIndicator,
    ValidationFeedbackProvider,
    BorderValidationFeedback,
)


class TestConfigPanelInit:
    """Tests de inicialización del ConfigPanel."""

    def test_default_values(self, qtbot):
        """Verifica valores por defecto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert panel.get_ip() == "localhost"
        assert panel.get_port() == 14001
        assert panel.is_connected() is False

    def test_custom_ip(self, qtbot):
        """Verifica inicialización con IP personalizada."""
        panel = ConfigPanel(default_ip="192.168.1.100")
        qtbot.addWidget(panel)

        assert panel.get_ip() == "192.168.1.100"

    def test_custom_port(self, qtbot):
        """Verifica inicialización con puerto personalizado."""
        panel = ConfigPanel(default_port=14002)
        qtbot.addWidget(panel)

        assert panel.get_port() == 14002

    def test_custom_ip_and_port(self, qtbot):
        """Verifica inicialización con IP y puerto personalizados."""
        panel = ConfigPanel(default_ip="10.0.0.1", default_port=8080)
        qtbot.addWidget(panel)

        assert panel.get_ip() == "10.0.0.1"
        assert panel.get_port() == 8080

    def test_default_ip_validator(self, qtbot):
        """Verifica que usa DefaultIPValidator por defecto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert isinstance(panel.ip_validator, DefaultIPValidator)

    def test_default_status_indicator(self, qtbot):
        """Verifica que usa LEDStatusIndicator por defecto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert isinstance(panel.status_indicator, LEDStatusIndicator)

    def test_default_validation_feedback(self, qtbot):
        """Verifica que usa BorderValidationFeedback por defecto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert isinstance(panel.validation_feedback, BorderValidationFeedback)

    def test_default_labels(self, qtbot):
        """Verifica etiquetas por defecto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert panel.labels.ip_label == "IP:"
        assert panel.labels.port_label == "Puerto:"
        assert panel.labels.connect_text == "Conectar"
        assert panel.labels.disconnect_text == "Desconectar"


class TestConfigPanelIPValidation:
    """Tests de validación de IP."""

    def test_valid_ip_localhost(self, qtbot):
        """Verifica que localhost es válido."""
        panel = ConfigPanel(default_ip="localhost")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is True

    def test_valid_ip_standard(self, qtbot):
        """Verifica que una IP estándar es válida."""
        panel = ConfigPanel(default_ip="192.168.1.1")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is True

    def test_valid_ip_zeros(self, qtbot):
        """Verifica que 0.0.0.0 es válido."""
        panel = ConfigPanel(default_ip="0.0.0.0")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is True

    def test_valid_ip_broadcast(self, qtbot):
        """Verifica que 255.255.255.255 es válido."""
        panel = ConfigPanel(default_ip="255.255.255.255")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is True

    def test_invalid_ip_empty(self, qtbot):
        """Verifica que IP vacía es inválida."""
        panel = ConfigPanel(default_ip="")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is False

    def test_invalid_ip_letters(self, qtbot):
        """Verifica que IP con letras es inválida."""
        panel = ConfigPanel(default_ip="abc.def.ghi.jkl")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is False

    def test_invalid_ip_out_of_range(self, qtbot):
        """Verifica que IP fuera de rango es inválida."""
        panel = ConfigPanel(default_ip="256.256.256.256")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is False

    def test_invalid_ip_incomplete(self, qtbot):
        """Verifica que IP incompleta es inválida."""
        panel = ConfigPanel(default_ip="192.168.1")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is False


class TestConfigPanelPort:
    """Tests del campo de puerto."""

    def test_port_minimum(self, qtbot):
        """Verifica puerto mínimo permitido."""
        panel = ConfigPanel(default_port=1)
        qtbot.addWidget(panel)

        assert panel.get_port() == 1

    def test_port_maximum(self, qtbot):
        """Verifica puerto máximo permitido."""
        panel = ConfigPanel(default_port=65535)
        qtbot.addWidget(panel)

        assert panel.get_port() == 65535

    def test_set_port(self, qtbot):
        """Verifica cambio de puerto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_port(8080)

        assert panel.get_port() == 8080


class TestConfigPanelSetters:
    """Tests de los métodos setters."""

    def test_set_ip(self, qtbot):
        """Verifica cambio de IP."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_ip("10.0.0.1")

        assert panel.get_ip() == "10.0.0.1"

    def test_set_ip_with_spaces(self, qtbot):
        """Verifica que get_ip() retorna IP sin espacios."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_ip("  192.168.1.1  ")

        assert panel.get_ip() == "192.168.1.1"


class TestConfigPanelConnectionState:
    """Tests del estado de conexión."""

    def test_initial_disconnected_state(self, qtbot):
        """Verifica estado inicial desconectado."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert panel.is_connected() is False

    def test_set_connected_state_true(self, qtbot):
        """Verifica cambio a estado conectado."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_connected_state(True)

        assert panel.is_connected() is True

    def test_set_connected_state_false(self, qtbot):
        """Verifica cambio a estado desconectado."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_connected_state(True)
        panel.set_connected_state(False)

        assert panel.is_connected() is False

    def test_connected_state_disables_inputs(self, qtbot):
        """Verifica que estado conectado deshabilita inputs."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_connected_state(True)

        assert panel._ip_input.isEnabled() is False
        assert panel._port_input.isEnabled() is False

    def test_disconnected_state_enables_inputs(self, qtbot):
        """Verifica que estado desconectado habilita inputs."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_connected_state(True)
        panel.set_connected_state(False)

        assert panel._ip_input.isEnabled() is True
        assert panel._port_input.isEnabled() is True

    def test_connected_state_changes_button_text(self, qtbot):
        """Verifica que el botón cambia texto según estado."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        assert panel._connect_button.text() == "Conectar"

        panel.set_connected_state(True)
        assert panel._connect_button.text() == "Desconectar"

        panel.set_connected_state(False)
        assert panel._connect_button.text() == "Conectar"

    def test_connected_state_updates_status_indicator(self, qtbot):
        """Verifica que el indicador de estado se actualiza."""
        indicator = MagicMock(spec=StatusIndicator)
        indicator.get_widget.return_value = QWidget()

        panel = ConfigPanel(status_indicator=indicator)
        qtbot.addWidget(panel)

        panel.set_connected_state(True)

        indicator.set_state.assert_called_with(True)


class TestConfigPanelSignals:
    """Tests de señales."""

    def test_connect_requested_signal(self, qtbot):
        """Verifica emisión de señal connect_requested."""
        panel = ConfigPanel(default_ip="localhost")
        qtbot.addWidget(panel)

        signal_received = []
        panel.connect_requested.connect(lambda: signal_received.append(True))

        panel._connect_button.click()

        assert len(signal_received) == 1

    def test_connect_not_emitted_with_invalid_ip(self, qtbot):
        """Verifica que no se emite connect_requested con IP inválida."""
        panel = ConfigPanel(default_ip="invalid")
        qtbot.addWidget(panel)

        signal_received = []
        panel.connect_requested.connect(lambda: signal_received.append(True))

        panel._connect_button.click()

        assert len(signal_received) == 0

    def test_disconnect_requested_signal(self, qtbot):
        """Verifica emisión de señal disconnect_requested."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        panel.set_connected_state(True)

        signal_received = []
        panel.disconnect_requested.connect(lambda: signal_received.append(True))

        panel._connect_button.click()

        assert len(signal_received) == 1

    def test_config_changed_signal_on_ip_change(self, qtbot):
        """Verifica emisión de config_changed al cambiar IP."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        signal_received = []
        panel.config_changed.connect(lambda: signal_received.append(True))

        panel._ip_input.setText("192.168.1.1")

        assert len(signal_received) >= 1

    def test_config_changed_signal_on_port_change(self, qtbot):
        """Verifica emisión de config_changed al cambiar puerto."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)

        signal_received = []
        panel.config_changed.connect(lambda: signal_received.append(True))

        panel._port_input.setValue(8080)

        assert len(signal_received) == 1


class TestConfigPanelDependencyInjection:
    """Tests de inyección de dependencias."""

    def test_custom_ip_validator_injection(self, qtbot):
        """Verifica inyección de validador personalizado."""
        class AlwaysValidValidator:
            def validate(self, ip: str) -> bool:
                return True

            def get_error_message(self) -> str:
                return ""

        validator = AlwaysValidValidator()
        panel = ConfigPanel(ip_validator=validator)
        qtbot.addWidget(panel)

        assert panel.ip_validator is validator

    def test_custom_status_indicator_injection(self, qtbot):
        """Verifica inyección de indicador de estado personalizado."""
        class CustomIndicator:
            def __init__(self):
                self._widget = QWidget()

            def get_widget(self) -> QWidget:
                return self._widget

            def set_state(self, active: bool) -> None:
                pass

        indicator = CustomIndicator()
        panel = ConfigPanel(status_indicator=indicator)
        qtbot.addWidget(panel)

        assert panel.status_indicator is indicator

    def test_custom_validation_feedback_injection(self, qtbot):
        """Verifica inyección de feedback personalizado."""
        class CustomFeedback:
            def show_valid(self, widget: QWidget) -> None:
                pass

            def show_invalid(self, widget: QWidget, message: str) -> None:
                pass

        feedback = CustomFeedback()
        panel = ConfigPanel(validation_feedback=feedback)
        qtbot.addWidget(panel)

        assert panel.validation_feedback is feedback

    def test_custom_labels_injection(self, qtbot):
        """Verifica inyección de etiquetas personalizadas."""
        labels = ConfigPanelLabels(
            ip_label="Address:",
            port_label="Port:",
            connect_text="Connect",
            disconnect_text="Disconnect"
        )
        panel = ConfigPanel(labels=labels)
        qtbot.addWidget(panel)

        assert panel.labels is labels
        assert panel._connect_button.text() == "Connect"

    def test_validation_feedback_called_on_invalid_ip(self, qtbot):
        """Verifica que se llama al feedback en IP inválida."""
        feedback = MagicMock(spec=ValidationFeedbackProvider)

        panel = ConfigPanel(
            default_ip="localhost",
            validation_feedback=feedback
        )
        qtbot.addWidget(panel)

        # Cambiar a IP inválida dispara validación
        panel.set_ip("invalid-ip")

        feedback.show_invalid.assert_called()

    def test_validation_feedback_called_on_valid_ip(self, qtbot):
        """Verifica que se llama al feedback en IP válida."""
        feedback = MagicMock(spec=ValidationFeedbackProvider)

        panel = ConfigPanel(
            default_ip="invalid",
            validation_feedback=feedback
        )
        qtbot.addWidget(panel)

        # Cambiar a IP válida dispara validación
        panel.set_ip("192.168.1.1")

        feedback.show_valid.assert_called()

    def test_set_ip_validator(self, qtbot):
        """Verifica cambio de validador en runtime."""
        class AlwaysValidValidator:
            def validate(self, ip: str) -> bool:
                return True

            def get_error_message(self) -> str:
                return ""

        panel = ConfigPanel(default_ip="invalid-ip")
        qtbot.addWidget(panel)

        assert panel.is_ip_valid() is False

        panel.set_ip_validator(AlwaysValidValidator())

        assert panel.is_ip_valid() is True

    def test_set_validation_feedback(self, qtbot):
        """Verifica cambio de feedback en runtime."""
        panel = ConfigPanel(default_ip="invalid")
        qtbot.addWidget(panel)

        new_feedback = MagicMock(spec=ValidationFeedbackProvider)
        panel.set_validation_feedback(new_feedback)

        new_feedback.show_invalid.assert_called()


class TestDefaultIPValidator:
    """Tests del validador de IP por defecto."""

    def test_validate_localhost(self):
        """Verifica validación de localhost."""
        validator = DefaultIPValidator()

        assert validator.validate("localhost") is True
        assert validator.validate("LOCALHOST") is True
        assert validator.validate("LocalHost") is True

    def test_validate_standard_ips(self):
        """Verifica validación de IPs estándar."""
        validator = DefaultIPValidator()

        assert validator.validate("192.168.1.1") is True
        assert validator.validate("10.0.0.1") is True
        assert validator.validate("172.16.0.1") is True
        assert validator.validate("127.0.0.1") is True

    def test_validate_edge_case_ips(self):
        """Verifica validación de IPs en casos límite."""
        validator = DefaultIPValidator()

        assert validator.validate("0.0.0.0") is True
        assert validator.validate("255.255.255.255") is True
        assert validator.validate("1.1.1.1") is True

    def test_reject_empty(self):
        """Verifica rechazo de cadena vacía."""
        validator = DefaultIPValidator()

        assert validator.validate("") is False

    def test_reject_invalid_format(self):
        """Verifica rechazo de formato inválido."""
        validator = DefaultIPValidator()

        assert validator.validate("192.168.1") is False
        assert validator.validate("192.168.1.1.1") is False
        assert validator.validate("192.168.1.") is False
        assert validator.validate(".192.168.1.1") is False

    def test_reject_out_of_range(self):
        """Verifica rechazo de valores fuera de rango."""
        validator = DefaultIPValidator()

        assert validator.validate("256.0.0.1") is False
        assert validator.validate("192.168.1.256") is False
        assert validator.validate("300.300.300.300") is False

    def test_reject_non_numeric(self):
        """Verifica rechazo de valores no numéricos."""
        validator = DefaultIPValidator()

        assert validator.validate("abc.def.ghi.jkl") is False
        assert validator.validate("192.168.a.1") is False

    def test_strips_whitespace(self):
        """Verifica que acepta IPs con espacios alrededor."""
        validator = DefaultIPValidator()

        assert validator.validate("  192.168.1.1  ") is True
        assert validator.validate("  localhost  ") is True

    def test_error_message(self):
        """Verifica mensaje de error."""
        validator = DefaultIPValidator()

        message = validator.get_error_message()

        assert "IP" in message
        assert len(message) > 0


class TestConfigPanelRendering:
    """Tests de renderizado."""

    def test_renders_without_error(self, qtbot):
        """Verifica que el panel se renderiza sin errores."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)
        panel.show()

        assert True

    def test_all_widgets_visible(self, qtbot):
        """Verifica que todos los widgets son visibles."""
        panel = ConfigPanel()
        qtbot.addWidget(panel)
        panel.show()

        assert panel._ip_input.isVisible()
        assert panel._port_input.isVisible()
        assert panel._connect_button.isVisible()
