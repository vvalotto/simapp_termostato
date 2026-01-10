"""Panel de Control de Temperatura - Patrón MVC.

Permite configurar los parámetros de simulación:
- Modo automático/manual
- Parámetros senoidales (T_base, amplitud, período)
- Temperatura manual fija
"""

from .modelo import (
    ModoOperacion,
    ParametrosSenoidal,
    RangosControl,
    ParametrosControl,
)
from .vista import SliderConValor, ControlTemperaturaVista
from .controlador import ControlTemperaturaControlador

__all__ = [
    "ModoOperacion",
    "ParametrosSenoidal",
    "RangosControl",
    "ParametrosControl",
    "SliderConValor",
    "ControlTemperaturaVista",
    "ControlTemperaturaControlador",
]
