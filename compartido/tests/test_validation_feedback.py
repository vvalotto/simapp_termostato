"""Tests para ValidationFeedbackProvider y BorderValidationFeedback."""
from PyQt6.QtWidgets import QLineEdit  # pylint: disable=no-name-in-module

from compartido.widgets import BorderValidationFeedback


class TestBorderValidationFeedbackInit:
    """Tests de inicialización del BorderValidationFeedback."""

    def test_default_styles(self):
        """Verifica estilos por defecto."""
        feedback = BorderValidationFeedback()

        assert feedback.valid_style == ""
        assert feedback.invalid_style == "border: 1px solid red;"

    def test_custom_valid_style(self):
        """Verifica estilo válido personalizado."""
        feedback = BorderValidationFeedback(valid_style="border: 1px solid green;")

        assert feedback.valid_style == "border: 1px solid green;"

    def test_custom_invalid_style(self):
        """Verifica estilo inválido personalizado."""
        feedback = BorderValidationFeedback(invalid_style="background: #ffcccc;")

        assert feedback.invalid_style == "background: #ffcccc;"

    def test_custom_both_styles(self):
        """Verifica ambos estilos personalizados."""
        feedback = BorderValidationFeedback(
            valid_style="border: 2px solid green;",
            invalid_style="border: 2px solid red;"
        )

        assert feedback.valid_style == "border: 2px solid green;"
        assert feedback.invalid_style == "border: 2px solid red;"


class TestBorderValidationFeedbackShowValid:
    """Tests del método show_valid."""

    def test_show_valid_clears_stylesheet(self, qtbot):
        """Verifica que show_valid limpia el stylesheet."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        widget.setStyleSheet("border: 1px solid red;")
        feedback.show_valid(widget)

        assert widget.styleSheet() == ""

    def test_show_valid_clears_tooltip(self, qtbot):
        """Verifica que show_valid limpia el tooltip."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        widget.setToolTip("Error message")
        feedback.show_valid(widget)

        assert widget.toolTip() == ""

    def test_show_valid_applies_custom_style(self, qtbot):
        """Verifica que show_valid aplica estilo personalizado."""
        feedback = BorderValidationFeedback(valid_style="border: 1px solid green;")
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_valid(widget)

        assert widget.styleSheet() == "border: 1px solid green;"


class TestBorderValidationFeedbackShowInvalid:
    """Tests del método show_invalid."""

    def test_show_invalid_applies_error_style(self, qtbot):
        """Verifica que show_invalid aplica estilo de error."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_invalid(widget, "Error message")

        assert widget.styleSheet() == "border: 1px solid red;"

    def test_show_invalid_sets_tooltip(self, qtbot):
        """Verifica que show_invalid establece tooltip."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_invalid(widget, "IP inválida")

        assert widget.toolTip() == "IP inválida"

    def test_show_invalid_applies_custom_style(self, qtbot):
        """Verifica que show_invalid aplica estilo personalizado."""
        feedback = BorderValidationFeedback(invalid_style="background: pink;")
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_invalid(widget, "Error")

        assert widget.styleSheet() == "background: pink;"

    def test_show_invalid_empty_message(self, qtbot):
        """Verifica que show_invalid maneja mensaje vacío."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_invalid(widget, "")

        assert widget.toolTip() == ""
        assert widget.styleSheet() == "border: 1px solid red;"


class TestBorderValidationFeedbackTransitions:
    """Tests de transiciones entre estados."""

    def test_valid_to_invalid_transition(self, qtbot):
        """Verifica transición de válido a inválido."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_valid(widget)
        assert widget.styleSheet() == ""

        feedback.show_invalid(widget, "Error")
        assert widget.styleSheet() == "border: 1px solid red;"
        assert widget.toolTip() == "Error"

    def test_invalid_to_valid_transition(self, qtbot):
        """Verifica transición de inválido a válido."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_invalid(widget, "Error")
        assert widget.styleSheet() == "border: 1px solid red;"

        feedback.show_valid(widget)
        assert widget.styleSheet() == ""
        assert widget.toolTip() == ""

    def test_multiple_invalid_calls(self, qtbot):
        """Verifica múltiples llamadas a show_invalid."""
        feedback = BorderValidationFeedback()
        widget = QLineEdit()
        qtbot.addWidget(widget)

        feedback.show_invalid(widget, "Error 1")
        assert widget.toolTip() == "Error 1"

        feedback.show_invalid(widget, "Error 2")
        assert widget.toolTip() == "Error 2"
