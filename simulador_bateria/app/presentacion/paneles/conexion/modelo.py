"""Modelo de datos para el Panel de Conexion.

Contiene el estado de la conexion TCP sin conocimiento de la UI.
"""

from dataclasses import dataclass

from ..base import ModeloBase


@dataclass
class ConexionPanelModelo(ModeloBase):
    """Modelo que representa el estado de la conexion TCP.

    Attributes:
        ip: Direccion IP del servidor.
        puerto: Puerto del servidor.
        conectado: Estado de la conexion.
    """

    ip: str = "localhost"
    puerto: int = 11000
    conectado: bool = False

    def set_ip(self, ip: str) -> None:
        """Establece la direccion IP.

        Args:
            ip: Nueva direccion IP.
        """
        self.ip = ip.strip()

    def set_puerto(self, puerto: int) -> None:
        """Establece el puerto validando el rango.

        Args:
            puerto: Nuevo numero de puerto.
        """
        self.puerto = max(1, min(65535, puerto))

    def set_conectado(self, conectado: bool) -> None:
        """Establece el estado de conexion.

        Args:
            conectado: True si esta conectado.
        """
        self.conectado = conectado
