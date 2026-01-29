"""
Módulo de dominio del termostato.

Este módulo contiene la lógica de negocio pura del termostato:
- EstadoTermostato: Modelo de datos del estado del sistema
- Comandos: Jerarquía de comandos para acciones del usuario
"""

from .estado_termostato import EstadoTermostato
from .comandos import (
    ComandoTermostato,
    ComandoPower,
    ComandoSetTemp,
    ComandoAumentar,
    ComandoDisminuir,
    ComandoSetModoDisplay,
)

__all__ = [
    "EstadoTermostato",
    "ComandoTermostato",
    "ComandoPower",
    "ComandoSetTemp",
    "ComandoAumentar",
    "ComandoDisminuir",
    "ComandoSetModoDisplay",
]
