"""Controlador para el Panel de Conexion.

Coordina la comunicacion entre el modelo y la vista,
manejando las solicitudes de conexion/desconexion.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import ConexionPanelModelo
from .vista import ConexionPanelVista


class ConexionPanelControlador(
    ControladorBase[ConexionPanelModelo, ConexionPanelVista]
):
    """Controlador del panel de conexion TCP.

    Gestiona las solicitudes de conexion/desconexion y emite
    las senales correspondientes.

    Signals:
        conectar_solicitado: Emitido con IP y puerto al conectar.
        desconectar_solicitado: Emitido al desconectar.
    """

    conectar_solicitado = pyqtSignal(str, int)
    desconectar_solicitado = pyqtSignal()

    def __init__(
        self,
        modelo: Optional[ConexionPanelModelo] = None,
        vista: Optional[ConexionPanelVista] = None,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador del panel de conexion.

        Args:
            modelo: Modelo de conexion, se crea uno nuevo si no se provee.
            vista: Vista del panel, se crea una nueva si no se provee.
            parent: Objeto padre Qt opcional.
        """
        modelo = modelo or ConexionPanelModelo()
        vista = vista or ConexionPanelVista()
        super().__init__(modelo, vista, parent)
        # Actualizar vista con valores iniciales
        self._actualizar_vista()

    def _conectar_signals(self) -> None:
        """Conecta las senales entre vista y modelo."""
        self._vista.conectar_clicked.connect(self._on_conectar)
        self._vista.desconectar_clicked.connect(self._on_desconectar)

    def _on_conectar(self) -> None:
        """Maneja la solicitud de conexion."""
        ip = self._vista.get_ip()
        puerto = self._vista.get_puerto()
        self._modelo.set_ip(ip)
        self._modelo.set_puerto(puerto)
        self.conectar_solicitado.emit(ip, puerto)

    def _on_desconectar(self) -> None:
        """Maneja la solicitud de desconexion."""
        self.desconectar_solicitado.emit()

    def actualizar_conexion(self, conectado: bool) -> None:
        """Actualiza el estado de conexion.

        Args:
            conectado: True si esta conectado.
        """
        self._modelo.set_conectado(conectado)
        self._actualizar_vista()

    def set_ip(self, ip: str) -> None:
        """Establece la IP desde codigo externo.

        Args:
            ip: Nueva direccion IP.
        """
        self._modelo.set_ip(ip)
        self._actualizar_vista()

    def set_puerto(self, puerto: int) -> None:
        """Establece el puerto desde codigo externo.

        Args:
            puerto: Nuevo numero de puerto.
        """
        self._modelo.set_puerto(puerto)
        self._actualizar_vista()

    @property
    def ip(self) -> str:
        """Retorna la IP actual."""
        return self._modelo.ip

    @property
    def puerto(self) -> int:
        """Retorna el puerto actual."""
        return self._modelo.puerto

    @property
    def conectado(self) -> bool:
        """Retorna el estado de conexion."""
        return self._modelo.conectado
