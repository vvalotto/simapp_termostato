"""Capa de comunicación del simulador de batería.

Contiene los componentes de red:
- ClienteBateria: Cliente TCP para envío de voltaje
- ServicioEnvioBateria: Integración generador + cliente
"""
from .cliente_bateria import ClienteBateria
from .servicio_envio import ServicioEnvioBateria

__all__ = [
    "ClienteBateria",
    "ServicioEnvioBateria",
]
