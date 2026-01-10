"""Panel de Gráfico - Patrón MVC.

Visualiza la temperatura en tiempo real usando pyqtgraph.
Mantiene un buffer circular de datos históricos.
"""

from .modelo import ConfigGrafico, PuntoTemperatura, DatosGrafico
from .vista import GraficoTemperaturaVista
from .controlador import GraficoControlador

__all__ = [
    "ConfigGrafico",
    "PuntoTemperatura",
    "DatosGrafico",
    "GraficoTemperaturaVista",
    "GraficoControlador",
]
