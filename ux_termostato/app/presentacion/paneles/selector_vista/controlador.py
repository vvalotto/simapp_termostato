"""Controlador del panel selector de vista."""

from dataclasses import replace
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import SelectorVistaModelo
from .vista import SelectorVistaVista


logger = logging.getLogger(__name__)


class SelectorVistaControlador(QObject):
    """Controlador del selector de vista.

    Gestiona la lógica de cambio entre vista "ambiente" y "deseada",
    emitiendo señales cuando el usuario cambia el modo.
    """

    # Señales
    modo_cambiado = pyqtSignal(str)  # Emite "ambiente" o "deseada"

    def __init__(
        self,
        modelo: SelectorVistaModelo,
        vista: SelectorVistaVista,
        parent=None
    ):
        """Inicializa el controlador.

        Args:
            modelo: Modelo del selector de vista
            vista: Vista del selector de vista
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self._modelo = modelo
        self._vista = vista

        # Conectar señales
        self._conectar_signals()

        # Inicializar vista
        self._vista.actualizar(self._modelo)

    def _conectar_signals(self):
        """Conecta señales de la vista."""
        self._vista.boton_ambiente.clicked.connect(self._on_ambiente_clicked)
        self._vista.boton_deseada.clicked.connect(self._on_deseada_clicked)

    def _on_ambiente_clicked(self):
        """Handler de click en botón ambiente."""
        if self._modelo.modo != "ambiente":
            self._cambiar_modo("ambiente")

    def _on_deseada_clicked(self):
        """Handler de click en botón deseada."""
        if self._modelo.modo != "deseada":
            self._cambiar_modo("deseada")

    def _cambiar_modo(self, nuevo_modo: str):
        """Cambia el modo y notifica.

        Args:
            nuevo_modo: Nuevo modo ("ambiente" o "deseada")
        """
        # Actualizar modelo
        self._modelo = replace(self._modelo, modo=nuevo_modo)

        # Actualizar vista
        self._vista.actualizar(self._modelo)

        # Emitir señal
        self.modo_cambiado.emit(nuevo_modo)
        logger.info("Modo de vista cambiado a: %s", nuevo_modo)

    def setEnabled(self, habilitado: bool):
        """Habilita/deshabilita el selector.

        Args:
            habilitado: True para habilitar, False para deshabilitar
        """
        self._modelo = replace(self._modelo, habilitado=habilitado)
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self) -> SelectorVistaModelo:
        """Retorna el modelo actual."""
        return self._modelo
