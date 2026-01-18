"""
Panel Power - Componente de encendido/apagado del termostato.

Este paquete implementa el patrón MVC para el botón de encendido/apagado
del termostato, permitiendo al usuario controlar el estado general del sistema.
"""

from .modelo import PowerModelo
from .vista import PowerVista
from .controlador import PowerControlador

__all__ = [
    "PowerModelo",
    "PowerVista",
    "PowerControlador",
]
