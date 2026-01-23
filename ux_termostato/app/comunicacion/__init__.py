"""
Módulo de comunicación del termostato.

Este módulo contiene los componentes de comunicación TCP bidireccional
con el Raspberry Pi:
- ServidorEstado: Recibe estado del termostato (puerto 14001)
- ClienteComandos: Envía comandos al termostato (puerto 14000)
"""

from .servidor_estado import ServidorEstado
from .cliente_comandos import ClienteComandos

__all__ = [
    "ServidorEstado",
    "ClienteComandos",
]
