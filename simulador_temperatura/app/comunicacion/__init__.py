"""
Modulo de comunicacion TCP del Simulador de Temperatura.

Contiene:
    - ClienteTemperatura: Cliente TCP para enviar valores al puerto 12000
    - ServicioEnvioTemperatura: Integración generador + cliente
"""
from .cliente_temperatura import ClienteTemperatura
from .servicio_envio import ServicioEnvioTemperatura

__all__ = [
    "ClienteTemperatura",
    "ServicioEnvioTemperatura",
]
