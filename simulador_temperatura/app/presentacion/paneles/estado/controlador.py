"""Controlador para el Panel de Estado.

Coordina la comunicación entre el modelo y la vista,
manejando las actualizaciones del estado de la simulación.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import EstadoSimulacion
from .vista import PanelEstadoVista


class PanelEstadoControlador(ControladorBase[EstadoSimulacion, PanelEstadoVista]):
    """Controlador del panel de estado.

    Gestiona las actualizaciones de temperatura, conexión y contadores.

    Signals:
        temperatura_actualizada: Emitido cuando cambia la temperatura.
        conexion_actualizada: Emitido cuando cambia el estado de conexión.
        contadores_actualizados: Emitido cuando cambian los contadores.
    """

    temperatura_actualizada = pyqtSignal(float)
    conexion_actualizada = pyqtSignal(bool)
    contadores_actualizados = pyqtSignal(int, int)  # exitosos, fallidos

    def __init__(
        self,
        modelo: Optional[EstadoSimulacion] = None,
        vista: Optional[PanelEstadoVista] = None,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador del panel de estado.

        Args:
            modelo: Modelo de estado, se crea uno nuevo si no se provee.
            vista: Vista del panel, se crea una nueva si no se provee.
            parent: Objeto padre Qt opcional.
        """
        modelo = modelo or EstadoSimulacion()
        vista = vista or PanelEstadoVista()
        super().__init__(modelo, vista, parent)

    def _conectar_signals(self) -> None:
        """Conecta las señales internas.

        En este panel, las actualizaciones vienen del exterior
        (generador, servicio) por lo que no hay signals internos
        de la vista que conectar.
        """
        # El panel de estado es principalmente de solo lectura
        # Las actualizaciones vienen de métodos públicos
        pass

    def actualizar_temperatura(self, temperatura: float) -> None:
        """Actualiza la temperatura en el modelo y la vista.

        Args:
            temperatura: Nueva temperatura a mostrar.
        """
        self._modelo.temperatura_actual = temperatura
        self._actualizar_vista()
        self.temperatura_actualizada.emit(temperatura)

    def actualizar_conexion(self, conectado: bool) -> None:
        """Actualiza el estado de conexión.

        Args:
            conectado: True si está conectado al servidor.
        """
        self._modelo.conectado = conectado
        self._actualizar_vista()
        self.conexion_actualizada.emit(conectado)

    def registrar_envio_exitoso(self) -> None:
        """Registra un envío exitoso."""
        self._modelo.incrementar_exitosos()
        self._actualizar_vista()
        self.contadores_actualizados.emit(
            self._modelo.envios_exitosos,
            self._modelo.envios_fallidos
        )

    def registrar_envio_fallido(self) -> None:
        """Registra un envío fallido."""
        self._modelo.incrementar_fallidos()
        self._actualizar_vista()
        self.contadores_actualizados.emit(
            self._modelo.envios_exitosos,
            self._modelo.envios_fallidos
        )

    def reiniciar_contadores(self) -> None:
        """Reinicia los contadores de envíos."""
        self._modelo.reiniciar_contadores()
        self._actualizar_vista()
        self.contadores_actualizados.emit(0, 0)

    @property
    def temperatura_actual(self) -> float:
        """Retorna la temperatura actual del modelo."""
        return self._modelo.temperatura_actual

    @property
    def conectado(self) -> bool:
        """Retorna el estado de conexión."""
        return self._modelo.conectado

    @property
    def envios_exitosos(self) -> int:
        """Retorna el número de envíos exitosos."""
        return self._modelo.envios_exitosos

    @property
    def envios_fallidos(self) -> int:
        """Retorna el número de envíos fallidos."""
        return self._modelo.envios_fallidos
