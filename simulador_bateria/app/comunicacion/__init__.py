"""Capa de comunicación del simulador de batería.

Contiene los componentes de red:
- ClienteBateria: Cliente TCP para envío de voltaje
- ServicioEnvioBateria: Integración generador + cliente
"""
from .cliente_bateria import ClienteBateria

__all__ = [
    "ClienteBateria",
]
