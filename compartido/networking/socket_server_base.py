"""
Clase base abstracta para servidores TCP con integración PyQt6.

Proporciona configuración común y manejo de errores compartido
entre diferentes tipos de servidores de socket.
"""
import socket
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class SocketServerBase(QObject):
    """
    Clase base para servidores TCP con señales PyQt6.

    Proporciona configuración común, constantes y manejo de errores
    compartido. Diseñada para ser extendida por servidores concretos.

    Signals:
        error_occurred: Emitida cuando ocurre un error (str: mensaje).

    Attributes:
        host (str): Dirección IP donde escuchar.
        port (int): Puerto TCP donde escuchar.
    """

    # Señales comunes
    error_occurred = pyqtSignal(str)

    # Constantes de configuración
    BUFFER_SIZE = 4096
    ENCODING = "utf-8"
    BACKLOG = 5
    ACCEPT_TIMEOUT = 1.0
    RECV_TIMEOUT = 1.0

    def __init__(
        self,
        host: str,
        port: int,
        parent: Optional[QObject] = None
    ):
        """
        Inicializa la configuración base del servidor TCP.

        Args:
            host: Dirección IP donde escuchar (ej: "0.0.0.0" para todas).
            port: Puerto TCP donde escuchar.
            parent: Objeto padre de Qt (opcional).
        """
        super().__init__(parent)
        self._host = host
        self._port = port

    @property
    def host(self) -> str:
        """Retorna la dirección de escucha."""
        return self._host

    @property
    def port(self) -> int:
        """Retorna el puerto de escucha."""
        return self._port

    def _create_server_socket(self) -> socket.socket:
        """
        Crea y configura un socket de servidor.

        Este método puede ser sobrescrito para personalizar
        la creación del socket (DIP).

        Returns:
            Socket configurado para escuchar conexiones.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def _handle_bind_error(self, error: Exception) -> None:
        """
        Maneja errores de binding emitiendo la señal apropiada.

        Args:
            error: Excepción capturada durante el bind.
        """
        self.error_occurred.emit(
            f"Error al iniciar servidor en {self._host}:{self._port}: {error}"
        )

    def _handle_client_error(self, client_addr: str, error: Exception) -> None:
        """
        Maneja errores de comunicación con cliente.

        Args:
            client_addr: Dirección del cliente.
            error: Excepción capturada.
        """
        self.error_occurred.emit(f"Error con cliente {client_addr}: {error}")
