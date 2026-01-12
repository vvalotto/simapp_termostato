"""Coordinator para conexión de señales del simulador de batería.

Gestiona todas las conexiones de señales PyQt6 entre componentes,
desacoplando la lógica de conexión del ciclo de vida.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class SimuladorCoordinator(QObject):
    """Coordina las señales entre componentes del simulador.

    Conecta:
    - Generador → CtrlEstado (actualización de voltaje)
    - CtrlControl → Generador (cambios de voltaje desde slider)
    - CtrlConexion → Señales de conexión/desconexión
    - Servicio → CtrlEstado (estado de conexión)

    Signals:
        conexion_solicitada: Emitida cuando el usuario solicita conectar.
        desconexion_solicitada: Emitida cuando el usuario solicita desconectar.
    """

    conexion_solicitada = pyqtSignal()
    desconexion_solicitada = pyqtSignal()

    def __init__(
        self,
        generador,
        ctrl_estado,
        ctrl_control,
        ctrl_conexion,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el coordinator y conecta señales.

        Args:
            generador: GeneradorBateria.
            ctrl_estado: PanelEstadoControlador.
            ctrl_control: ControlBateriaControlador.
            ctrl_conexion: PanelConexionControlador.
            parent: QObject padre opcional.
        """
        super().__init__(parent)
        self._generador = generador
        self._ctrl_estado = ctrl_estado
        self._ctrl_control = ctrl_control
        self._ctrl_conexion = ctrl_conexion
        self._servicio = None

        self._conectar_generador()
        self._conectar_control()
        self._conectar_conexion()

    def _conectar_generador(self) -> None:
        """Conecta señales del generador a los controladores."""
        # Generador → CtrlEstado: actualizar voltaje mostrado
        self._generador.valor_generado.connect(
            self._ctrl_estado.actualizar_estado
        )

    def _conectar_control(self) -> None:
        """Conecta señales del control al generador."""
        # CtrlControl → Generador: cambiar voltaje desde slider
        self._ctrl_control.voltaje_cambiado.connect(
            self._generador.set_voltaje
        )

    def _conectar_conexion(self) -> None:
        """Conecta señales del panel de conexión."""
        # CtrlConexion → Coordinator: solicitudes de conexión
        self._ctrl_conexion.conectar_solicitado.connect(
            self.conexion_solicitada.emit
        )
        self._ctrl_conexion.desconectar_solicitado.connect(
            self.desconexion_solicitada.emit
        )

    def set_servicio(self, servicio) -> None:
        """Configura el servicio de envío y conecta sus señales.

        Args:
            servicio: ServicioEnvioBateria.
        """
        self._servicio = servicio

        # Servicio → CtrlEstado: actualizar estado de conexión
        self._servicio.servicio_iniciado.connect(
            lambda: self._ctrl_estado.set_conectado(True)
        )
        self._servicio.servicio_detenido.connect(
            lambda: self._ctrl_estado.set_conectado(False)
        )
        self._servicio.envio_exitoso.connect(
            self._ctrl_estado.registrar_envio
        )

    @property
    def ip_configurada(self) -> str:
        """Retorna la IP configurada en el panel de conexión."""
        return self._ctrl_conexion.modelo.ip

    @property
    def puerto_configurado(self) -> int:
        """Retorna el puerto configurado en el panel de conexión."""
        return self._ctrl_conexion.modelo.puerto
