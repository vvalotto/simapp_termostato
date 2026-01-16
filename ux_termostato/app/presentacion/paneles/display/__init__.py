"""
Panel Display - Componente MVC completo.

Este paquete contiene el panel del display LCD principal del termostato,
implementado con el patrón MVC (Model-View-Controller).
"""

from .modelo import DisplayModelo
from .vista import DisplayVista
from .controlador import DisplayControlador

__all__ = [
    "DisplayModelo",
    "DisplayVista",
    "DisplayControlador",
]
