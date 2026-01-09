"""Controlador para el Panel de Conexión.

Coordina la comunicación entre el modelo y la vista,
gestionando las acciones de conexión.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import ConfiguracionConexion, EstadoConexion
from .vista import PanelConexionVista, ConfigPanelConexionVista


class PanelConexionControlador(
    ControladorBase[ConfiguracionConexion, PanelConexionVista]
):
    """Controlador del panel de conexión.

    Gestiona las solicitudes de conexión/desconexión y
    los cambios de configuración.

    Signals:
        conexion_solicitada: Emitido cuando se solicita conectar.
        desconexion_solicitada: Emitido cuando se solicita desconectar.
        configuracion_cambiada: Emitido cuando cambia IP o puerto.
        estado_cambiado: Emitido cuando cambia el estado de conexión.
    """

    conexion_solicitada = pyqtSignal()
    desconexion_solicitada = pyqtSignal()
    configuracion_cambiada = pyqtSignal()
    estado_cambiado = pyqtSignal(bool)  # True=conectado

    def __init__(
        self,
        modelo: Optional[ConfiguracionConexion] = None,
        vista: Optional[PanelConexionVista] = None,
        ip_inicial: str = "127.0.0.1",
        puerto_inicial: int = 14001,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador.

        Args:
            modelo: Modelo de configuración, se crea uno si no se provee.
            vista: Vista del panel, se crea una si no se provee.
            ip_inicial: IP por defecto.
            puerto_inicial: Puerto por defecto.
            parent: Objeto padre Qt opcional.
        """
        modelo = modelo or ConfiguracionConexion(
            ip=ip_inicial, puerto=puerto_inicial
        )
        vista = vista or PanelConexionVista(
            ip_inicial=ip_inicial, puerto_inicial=puerto_inicial
        )
        super().__init__(modelo, vista, parent)

        # Sincronizar vista con modelo inicial
        self._actualizar_vista()

    def _conectar_signals(self) -> None:
        """Conecta las señales de la vista con el controlador."""
        self._vista.conexion_solicitada.connect(self._on_conexion_solicitada)
        self._vista.desconexion_solicitada.connect(
            self._on_desconexion_solicitada
        )
        self._vista.ip_cambiada.connect(self._on_ip_cambiada)
        self._vista.puerto_cambiado.connect(self._on_puerto_cambiado)

    def _on_conexion_solicitada(self) -> None:
        """Callback cuando se solicita conectar."""
        self._modelo.conectar()
        self.conexion_solicitada.emit()
        self.modelo_cambiado.emit(self._modelo)

    def _on_desconexion_solicitada(self) -> None:
        """Callback cuando se solicita desconectar."""
        self._modelo.desconectar()
        self._actualizar_vista()
        self.desconexion_solicitada.emit()
        self.estado_cambiado.emit(False)
        self.modelo_cambiado.emit(self._modelo)

    def _on_ip_cambiada(self, ip: str) -> None:
        """Callback cuando cambia la IP."""
        self._modelo.ip = ip
        self.configuracion_cambiada.emit()
        self.modelo_cambiado.emit(self._modelo)

    def _on_puerto_cambiado(self, puerto: int) -> None:
        """Callback cuando cambia el puerto."""
        self._modelo.puerto = puerto
        self.configuracion_cambiada.emit()
        self.modelo_cambiado.emit(self._modelo)

    def confirmar_conexion(self) -> None:
        """Confirma que la conexión fue exitosa."""
        self._modelo.confirmar_conexion()
        self._actualizar_vista()
        self.estado_cambiado.emit(True)
        self.modelo_cambiado.emit(self._modelo)

    def registrar_error(self, mensaje: str) -> None:
        """Registra un error de conexión.

        Args:
            mensaje: Mensaje descriptivo del error.
        """
        self._modelo.registrar_error(mensaje)
        self._actualizar_vista()
        self.estado_cambiado.emit(False)
        self.modelo_cambiado.emit(self._modelo)

    def desconectar(self) -> None:
        """Desconecta (llamado externamente)."""
        self._modelo.desconectar()
        self._actualizar_vista()
        self.estado_cambiado.emit(False)
        self.modelo_cambiado.emit(self._modelo)

    def set_ip(self, ip: str) -> None:
        """Establece la IP sin emitir signal de cambio."""
        self._modelo.ip = ip
        self._actualizar_vista()

    def set_puerto(self, puerto: int) -> None:
        """Establece el puerto sin emitir signal de cambio."""
        self._modelo.puerto = puerto
        self._actualizar_vista()

    @property
    def ip(self) -> str:
        """Retorna la IP configurada."""
        return self._modelo.ip

    @property
    def puerto(self) -> int:
        """Retorna el puerto configurado."""
        return self._modelo.puerto

    @property
    def esta_conectado(self) -> bool:
        """Indica si está conectado."""
        return self._modelo.esta_conectado

    @property
    def estado(self) -> EstadoConexion:
        """Retorna el estado actual de conexión."""
        return self._modelo.estado

    @property
    def mensaje_error(self) -> str:
        """Retorna el mensaje de error si hay alguno."""
        return self._modelo.mensaje_error

    @property
    def direccion_completa(self) -> str:
        """Retorna la dirección completa (IP:puerto)."""
        return self._modelo.direccion_completa
