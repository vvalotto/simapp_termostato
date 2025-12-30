"""
Cliente TCP para conexiones efímeras con integración PyQt6.

Implementa el patrón: conectar → enviar → cerrar (operación atómica).
Ideal para simuladores que envían valores periódicamente sin mantener conexión.
"""
import socket
import threading
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .socket_client_base import SocketClientBase


class EphemeralSocketClient(SocketClientBase):
    """
    Cliente TCP para conexiones efímeras (fire-and-forget).

    Cada envío crea una nueva conexión, envía los datos y cierra
    inmediatamente. No mantiene estado de conexión.

    Este patrón es el usado por los simuladores de temperatura y
    batería según el protocolo de ISSE_Termostato.

    Signals:
        data_sent: Emitida cuando los datos se enviaron exitosamente.
        error_occurred: Emitida cuando ocurre un error (str: mensaje).

    Example:
        >>> client = EphemeralSocketClient("127.0.0.1", 12000)
        >>> client.data_sent.connect(on_success)
        >>> client.error_occurred.connect(on_error)
        >>> client.send("23.5")  # Conecta, envía, cierra
    """

    # Señal específica para envío efímero
    data_sent = pyqtSignal()

    def __init__(self, host: str, port: int, parent: Optional[QObject] = None):
        """
        Inicializa el cliente TCP efímero.

        Args:
            host: Dirección IP o hostname del servidor.
            port: Puerto TCP del servidor.
            parent: Objeto padre de Qt (opcional).
        """
        super().__init__(host, port, parent)

    def send(self, data: str) -> bool:
        """
        Conecta, envía datos y cierra la conexión de forma síncrona.

        Args:
            data: Cadena de texto a enviar.

        Returns:
            True si el envío fue exitoso, False en caso contrario.

        Note:
            Este método es bloqueante. Para envío no bloqueante,
            usar `send_async()`.
        """
        try:
            with self._create_socket() as sock:
                sock.connect((self._host, self._port))
                sock.sendall(data.encode(self.ENCODING))
                self.data_sent.emit()
                return True

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            self._handle_connection_error(e)
            return False

    def send_async(self, data: str) -> None:
        """
        Conecta, envía datos y cierra la conexión en un hilo separado.

        Args:
            data: Cadena de texto a enviar.

        Note:
            El resultado se comunica mediante las señales
            `data_sent` o `error_occurred`.
        """
        thread = threading.Thread(
            target=self._send_thread,
            args=(data,),
            daemon=True
        )
        thread.start()

    def _send_thread(self, data: str) -> None:
        """Hilo interno para envío asíncrono."""
        self.send(data)
