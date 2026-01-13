"""Controlador para el Panel de Control de Bateria.

Coordina la comunicacion entre el modelo y la vista,
manejando los cambios de voltaje del slider.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import ControlPanelModelo
from .vista import ControlPanelVista


class ControlPanelControlador(
    ControladorBase[ControlPanelModelo, ControlPanelVista]
):
    """Controlador del panel de control de voltaje.

    Gestiona los cambios de voltaje desde el slider y emite
    la senal correspondiente para actualizar el GeneradorBateria.

    Signals:
        voltaje_cambiado: Emitido cuando el usuario cambia el voltaje.
    """

    voltaje_cambiado = pyqtSignal(float)

    def __init__(
        self,
        modelo: Optional[ControlPanelModelo] = None,
        vista: Optional[ControlPanelVista] = None,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador del panel de control.

        Args:
            modelo: Modelo de control, se crea uno nuevo si no se provee.
            vista: Vista del panel, se crea una nueva si no se provee.
            parent: Objeto padre Qt opcional.
        """
        modelo = modelo or ControlPanelModelo()
        vista = vista or ControlPanelVista()
        super().__init__(modelo, vista, parent)
        # Actualizar vista con valores iniciales
        self._actualizar_vista()

    def _conectar_signals(self) -> None:
        """Conecta las senales entre vista y modelo."""
        self._vista.slider_cambiado.connect(self._on_slider_cambiado)

    def _on_slider_cambiado(self, paso: int) -> None:
        """Maneja el cambio del slider.

        Args:
            paso: Nueva posicion del slider.
        """
        voltaje = self._modelo.paso_a_voltaje(paso)
        self._modelo.set_voltaje(voltaje)
        self._actualizar_vista()
        self.voltaje_cambiado.emit(voltaje)

    def set_voltaje(self, voltaje: float) -> None:
        """Establece el voltaje desde codigo externo.

        Args:
            voltaje: Nuevo valor de voltaje en Volts.
        """
        self._modelo.set_voltaje(voltaje)
        self._actualizar_vista()

    @property
    def voltaje(self) -> float:
        """Retorna el voltaje actual."""
        return self._modelo.voltaje

    @property
    def voltaje_minimo(self) -> float:
        """Retorna el voltaje minimo."""
        return self._modelo.voltaje_minimo

    @property
    def voltaje_maximo(self) -> float:
        """Retorna el voltaje maximo."""
        return self._modelo.voltaje_maximo
