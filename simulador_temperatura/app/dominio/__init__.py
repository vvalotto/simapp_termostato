"""
Modulo de logica de negocio del Simulador de Temperatura.

Contiene:
    - EstadoTemperatura: Modelo de datos para el estado de temperatura
    - VariacionSenoidal: Logica de variacion senoidal de temperatura
    - GeneradorTemperatura: Genera valores simulados con variacion senoidal
"""
from .estado_temperatura import EstadoTemperatura
from .variacion_senoidal import VariacionSenoidal
from .generador_temperatura import GeneradorTemperatura

__all__ = [
    "EstadoTemperatura",
    "VariacionSenoidal",
    "GeneradorTemperatura",
]
