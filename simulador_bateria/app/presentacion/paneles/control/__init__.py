"""Panel de Control - Patron MVC.

Slider para control manual del voltaje de bateria (0-5V).
Precision de 0.1V.
"""

from .modelo import ControlPanelModelo
from .vista import ControlPanelVista
from .controlador import ControlPanelControlador

__all__ = [
    "ControlPanelModelo",
    "ControlPanelVista",
    "ControlPanelControlador",
]
