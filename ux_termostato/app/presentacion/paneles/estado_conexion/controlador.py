"""Controlador del panel de estado de conexión."""

from dataclasses import replace
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import EstadoConexionModelo
from .vista import EstadoConexionVista


logger = logging.getLogger(__name__)


class EstadoConexionControlador(QObject):
    """Controlador del estado de conexión.

    Gestiona los cambios de estado de la conexión con el Raspberry Pi
    y actualiza la vista correspondiente.
    """

    # Señales
    estado_cambiado = pyqtSignal(str)  # Emite el nuevo estado

    def __init__(
        self,
        modelo: EstadoConexionModelo,
        vista: EstadoConexionVista,
        parent=None
    ):
        """Inicializa el controlador.

        Args:
            modelo: Modelo del estado de conexión
            vista: Vista del estado de conexión
            parent: Objeto padre (opcional)
        """
        super().__init__(parent)
        self._modelo = modelo
        self._vista = vista

        # Inicializar vista
        self._vista.actualizar(self._modelo)

    def actualizar_estado(self, nuevo_estado: str, ip: str = ""):
        """Actualiza el estado de conexión.

        Args:
            nuevo_estado: Nuevo estado ("conectado", "desconectado", "conectando")
            ip: Dirección IP (opcional, para estado "conectado")
        """
        # Actualizar modelo
        self._modelo = replace(
            self._modelo,
            estado=nuevo_estado,
            direccion_ip=ip
        )

        # Actualizar vista
        self._vista.actualizar(self._modelo)

        # Emitir señal
        self.estado_cambiado.emit(nuevo_estado)
        logger.info("Estado de conexión: %s (IP: %s)", nuevo_estado, ip)

    def conexion_establecida(self, direccion: str):
        """Notifica que la conexión fue establecida.

        Args:
            direccion: Dirección del servidor conectado (formato "ip:puerto")
        """
        # Extraer solo la IP si viene en formato "ip:puerto"
        ip = direccion.split(":")[0] if ":" in direccion else direccion
        self.actualizar_estado("conectado", ip)

    def conexion_perdida(self, direccion: str = ""):
        """Notifica que la conexión se perdió.

        Args:
            direccion: Dirección del servidor desconectado (opcional)
        """
        self.actualizar_estado("desconectado", "")

    def conectando(self):
        """Notifica que se está intentando conectar."""
        self.actualizar_estado("conectando", "")

    @property
    def modelo(self) -> EstadoConexionModelo:
        """Retorna el modelo actual."""
        return self._modelo
