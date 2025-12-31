"""
Widgets reutilizables para las aplicaciones del proyecto.

Este módulo contiene componentes visuales PyQt6 compartidos
entre los simuladores y la interfaz UX.
"""
from .led_color_provider import LEDColor, LEDColorProvider, DefaultLEDColorProvider
from .led_indicator import LEDIndicator
from .ip_validator import IPValidator, DefaultIPValidator
from .status_indicator import StatusIndicator, LEDStatusIndicator
from .validation_feedback import ValidationFeedbackProvider, BorderValidationFeedback
from .config_panel import ConfigPanel, ConfigPanelLabels

__all__ = [
    # LED Indicator
    "LEDIndicator",
    "LEDColor",
    "LEDColorProvider",
    "DefaultLEDColorProvider",
    # Status Indicator
    "StatusIndicator",
    "LEDStatusIndicator",
    # IP Validation
    "IPValidator",
    "DefaultIPValidator",
    # Validation Feedback
    "ValidationFeedbackProvider",
    "BorderValidationFeedback",
    # Config Panel
    "ConfigPanel",
    "ConfigPanelLabels",
]
