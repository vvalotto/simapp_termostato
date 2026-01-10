"""Modelo de datos para el Panel de Conexión.

Contiene la configuración de conexión TCP.
"""

from dataclasses import dataclass
from enum import Enum

from ..base import ModeloBase


class EstadoConexion(Enum):
    """Estado de la conexión TCP."""

    DESCONECTADO = "desconectado"
    CONECTANDO = "conectando"
    CONECTADO = "conectado"
    ERROR = "error"


@dataclass
class ConfiguracionConexion(ModeloBase):
    """Modelo con la configuración de conexión.

    Attributes:
        ip: Dirección IP del servidor.
        puerto: Puerto del servidor.
        estado: Estado actual de la conexión.
        mensaje_error: Mensaje de error si hay alguno.
    """

    ip: str = "127.0.0.1"
    puerto: int = 14001
    estado: EstadoConexion = EstadoConexion.DESCONECTADO
    mensaje_error: str = ""

    @property
    def esta_conectado(self) -> bool:
        """Indica si está conectado."""
        return self.estado == EstadoConexion.CONECTADO

    @property
    def esta_conectando(self) -> bool:
        """Indica si está en proceso de conexión."""
        return self.estado == EstadoConexion.CONECTANDO

    @property
    def tiene_error(self) -> bool:
        """Indica si hay un error."""
        return self.estado == EstadoConexion.ERROR

    def conectar(self) -> None:
        """Cambia el estado a conectando."""
        self.estado = EstadoConexion.CONECTANDO
        self.mensaje_error = ""

    def confirmar_conexion(self) -> None:
        """Confirma que la conexión fue exitosa."""
        self.estado = EstadoConexion.CONECTADO
        self.mensaje_error = ""

    def desconectar(self) -> None:
        """Cambia el estado a desconectado."""
        self.estado = EstadoConexion.DESCONECTADO
        self.mensaje_error = ""

    def registrar_error(self, mensaje: str) -> None:
        """Registra un error de conexión.

        Args:
            mensaje: Mensaje descriptivo del error.
        """
        self.estado = EstadoConexion.ERROR
        self.mensaje_error = mensaje

    @property
    def direccion_completa(self) -> str:
        """Retorna la dirección completa (IP:puerto)."""
        return f"{self.ip}:{self.puerto}"
