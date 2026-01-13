"""Panel de Estado - Patron MVC.

Muestra el estado actual de la simulacion de bateria:
- Voltaje actual en formato X.XV
- Porcentaje equivalente (0-100%)
- Estado de conexion
- Contadores de envios exitosos/fallidos
"""

from .modelo import EstadoBateriaPanelModelo
from .vista import PanelEstadoVista
from .controlador import PanelEstadoControlador

__all__ = [
    "EstadoBateriaPanelModelo",
    "PanelEstadoVista",
    "PanelEstadoControlador",
]
