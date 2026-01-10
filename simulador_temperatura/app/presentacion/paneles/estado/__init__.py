"""Panel de Estado - Patrón MVC.

Muestra el estado actual de la simulación:
- Temperatura actual
- Estado de conexión
- Contadores de envíos exitosos/fallidos
"""

from .modelo import EstadoSimulacion
from .vista import PanelEstadoVista
from .controlador import PanelEstadoControlador

__all__ = [
    "EstadoSimulacion",
    "PanelEstadoVista",
    "PanelEstadoControlador",
]
