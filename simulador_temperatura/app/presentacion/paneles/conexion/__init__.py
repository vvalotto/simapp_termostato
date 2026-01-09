"""Panel de Conexión - Patrón MVC.

Gestiona la configuración de conexión TCP:
- IP del servidor
- Puerto
- Estado de conexión
"""

from .modelo import EstadoConexion, ConfiguracionConexion
from .vista import ConfigPanelConexionVista, PanelConexionVista
from .controlador import PanelConexionControlador

__all__ = [
    "EstadoConexion",
    "ConfiguracionConexion",
    "ConfigPanelConexionVista",
    "PanelConexionVista",
    "PanelConexionControlador",
]
