"""
Panel Climatizador - Componente MVC completo.

Este paquete contiene el panel del estado del climatizador del termostato,
implementado con el patrón MVC (Model-View-Controller).
"""

from .modelo import (
    ClimatizadorModelo,
    MODO_CALENTANDO,
    MODO_ENFRIANDO,
    MODO_REPOSO,
    MODO_APAGADO,
)
from .vista import ClimatizadorVista
from .controlador import ClimatizadorControlador

__all__ = [
    "ClimatizadorModelo",
    "ClimatizadorVista",
    "ClimatizadorControlador",
    "MODO_CALENTANDO",
    "MODO_ENFRIANDO",
    "MODO_REPOSO",
    "MODO_APAGADO",
]
