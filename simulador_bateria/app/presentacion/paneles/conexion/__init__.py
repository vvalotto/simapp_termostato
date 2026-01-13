"""Panel de Conexion - Patron MVC.

Configuracion de IP, puerto y control de conexion/desconexion TCP.
Usa ConfigPanel de compartido/widgets para la UI.
"""

from .modelo import ConexionPanelModelo
from .vista import ConexionPanelVista
from .controlador import ConexionPanelControlador

__all__ = [
    "ConexionPanelModelo",
    "ConexionPanelVista",
    "ConexionPanelControlador",
]
