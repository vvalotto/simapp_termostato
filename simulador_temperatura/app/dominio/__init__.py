"""
Modulo de logica de negocio del Simulador de Temperatura.

Contiene:
    - EstadoTemperatura: Modelo de datos para el estado de temperatura

Contendra:
    - GeneradorTemperatura: Genera valores simulados con variacion senoidal y ruido
"""
from .estado_temperatura import EstadoTemperatura

# Exports futuros (HU-3.3):
# from .generador_temperatura import GeneradorTemperatura

__all__ = [
    "EstadoTemperatura",
    # "GeneradorTemperatura",
]
