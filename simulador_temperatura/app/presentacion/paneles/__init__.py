"""Paneles MVC para la capa de presentación.

Este paquete contiene los paneles de la interfaz organizados
siguiendo el patrón Modelo-Vista-Controlador (MVC).
"""

from .base import ModeloBase, VistaBase, ControladorBase

__all__ = [
    "ModeloBase",
    "VistaBase",
    "ControladorBase",
]
