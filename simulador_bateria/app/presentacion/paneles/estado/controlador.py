"""Controlador para el Panel de Estado de Bateria.

Coordina la comunicacion entre el modelo y la vista,
manejando las actualizaciones del estado de la simulacion.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import EstadoBateriaPanelModelo
from .vista import PanelEstadoVista


class PanelEstadoControlador(
    ControladorBase[EstadoBateriaPanelModelo, PanelEstadoVista]
):
    """Controlador del panel de estado de bateria.

    Gestiona las actualizaciones de voltaje, conexion y contadores.

    Signals:
        voltaje_actualizado: Emitido cuando cambia el voltaje.
        conexion_actualizada: Emitido cuando cambia el estado de conexion.
        contadores_actualizados: Emitido cuando cambian los contadores.
    """

    voltaje_actualizado = pyqtSignal(float)
    conexion_actualizada = pyqtSignal(bool)
    contadores_actualizados = pyqtSignal(int, int)  # exitosos, fallidos

    def __init__(
        self,
        modelo: Optional[EstadoBateriaPanelModelo] = None,
        vista: Optional[PanelEstadoVista] = None,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador del panel de estado.

        Args:
            modelo: Modelo de estado, se crea uno nuevo si no se provee.
            vista: Vista del panel, se crea una nueva si no se provee.
            parent: Objeto padre Qt opcional.
        """
        modelo = modelo or EstadoBateriaPanelModelo()
        vista = vista or PanelEstadoVista()
        super().__init__(modelo, vista, parent)

    def _conectar_signals(self) -> None:
        """Conecta las senales internas.

        En este panel, las actualizaciones vienen del exterior
        (generador, servicio) por lo que no hay signals internos
        de la vista que conectar.
        """
        # El panel de estado es principalmente de solo lectura
        # Las actualizaciones vienen de metodos publicos

    def actualizar_voltaje(self, voltaje: float) -> None:
        """Actualiza el voltaje en el modelo y la vista.

        Args:
            voltaje: Nuevo voltaje a mostrar en Volts.
        """
        self._modelo.actualizar_voltaje(voltaje)
        self._actualizar_vista()
        self.voltaje_actualizado.emit(voltaje)

    def actualizar_conexion(self, conectado: bool) -> None:
        """Actualiza el estado de conexion.

        Args:
            conectado: True si esta conectado al servidor.
        """
        self._modelo.conectado = conectado
        self._actualizar_vista()
        self.conexion_actualizada.emit(conectado)

    def registrar_envio_exitoso(self) -> None:
        """Registra un envio exitoso."""
        self._modelo.incrementar_exitosos()
        self._actualizar_vista()
        self.contadores_actualizados.emit(
            self._modelo.envios_exitosos,
            self._modelo.envios_fallidos
        )

    def registrar_envio_fallido(self) -> None:
        """Registra un envio fallido."""
        self._modelo.incrementar_fallidos()
        self._actualizar_vista()
        self.contadores_actualizados.emit(
            self._modelo.envios_exitosos,
            self._modelo.envios_fallidos
        )

    def reiniciar_contadores(self) -> None:
        """Reinicia los contadores de envios."""
        self._modelo.reiniciar_contadores()
        self._actualizar_vista()
        self.contadores_actualizados.emit(0, 0)

    @property
    def voltaje_actual(self) -> float:
        """Retorna el voltaje actual del modelo."""
        return self._modelo.voltaje_actual

    @property
    def porcentaje(self) -> float:
        """Retorna el porcentaje de bateria."""
        return self._modelo.porcentaje

    @property
    def conectado(self) -> bool:
        """Retorna el estado de conexion."""
        return self._modelo.conectado

    @property
    def envios_exitosos(self) -> int:
        """Retorna el numero de envios exitosos."""
        return self._modelo.envios_exitosos

    @property
    def envios_fallidos(self) -> int:
        """Retorna el numero de envios fallidos."""
        return self._modelo.envios_fallidos
