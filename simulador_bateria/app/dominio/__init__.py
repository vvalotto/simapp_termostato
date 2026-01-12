"""Capa de dominio del simulador de batería.

Contiene la lógica de negocio:
- EstadoBateria: Modelo de datos inmutable
- GeneradorBateria: Generador de valores de voltaje
"""
from .estado_bateria import EstadoBateria
from .generador_bateria import GeneradorBateria

__all__ = [
    "EstadoBateria",
    "GeneradorBateria",
]
