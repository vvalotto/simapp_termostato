"""
Panel de Indicadores de Alerta.

Este paquete implementa el panel MVC completo para mostrar indicadores LED
de alerta del sistema (falla sensor y batería baja).
"""

from .modelo import IndicadoresModelo
from .vista import IndicadoresVista, AlertLED
from .controlador import IndicadoresControlador

__all__ = [
    "IndicadoresModelo",
    "IndicadoresVista",
    "AlertLED",
    "IndicadoresControlador",
]
