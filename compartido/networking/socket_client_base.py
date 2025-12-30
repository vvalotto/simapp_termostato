"""
Clase base abstracta para clientes TCP con integración PyQt6.

Proporciona la funcionalidad común compartida entre clientes
de conexión persistente y efímera.
"""
import socket
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class SocketClientBase(QObject):
    """
    Clase base para clientes TCP con señales PyQt6.

    Proporciona configuración común, constantes y manejo de errores
    compartido entre diferentes tipos de clientes de socket.

    Signals:
        error_occurred: Emitida cuando ocurre un error (str: mensaje).

    Attributes:
        host (str): Dirección IP o hostname del servidor.
        port (int): Puerto TCP del servidor.
    """

    # Señales comunes
    error_occurred = pyqtSignal(str)

    # Constantes de configuración
    BUFFER_SIZE = 4096
    DEFAULT_TIMEOUT = 5.0
    ENCODING = "utf-8"

    def __init__(self, host: str, port: int, parent: Optional[QObject] = None):
        """
        Inicializa la configuración base del cliente TCP.

        Args:
            host: Dirección IP o hostname del servidor.
            port: Puerto TCP del servidor.
            parent: Objeto padre de Qt (opcional).
        """
        super().__init__(parent)
        self._host = host
        self._port = port

    @property
    def host(self) -> str:
        """Retorna la dirección del servidor."""
        return self._host

    @property
    def port(self) -> int:
        """Retorna el puerto del servidor."""
        return self._port

    def _create_socket(self) -> socket.socket:
        """
        Crea y configura un nuevo socket TCP.

        Returns:
            Socket configurado con timeout por defecto.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.DEFAULT_TIMEOUT)
        return sock

    def _handle_connection_error(self, error: Exception) -> None:
        """
        Maneja errores de conexión emitiendo la señal apropiada.

        Args:
            error: Excepción capturada durante la operación de red.
        """
        if isinstance(error, socket.timeout):
            self.error_occurred.emit(
                f"Timeout al conectar a {self._host}:{self._port}"
            )
        elif isinstance(error, ConnectionRefusedError):
            self.error_occurred.emit(
                f"Conexión rechazada por {self._host}:{self._port}"
            )
        else:
            self.error_occurred.emit(f"Error de conexión: {error}")
