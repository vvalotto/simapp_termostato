"""Controlador del panel de configuración de conexión."""

from dataclasses import replace
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import ConexionModelo
from .vista import ConexionVista


logger = logging.getLogger(__name__)


class ConexionControlador(QObject):
    """Controlador del panel de conexión.

    Gestiona la validación en tiempo real de la IP y emite señales
    cuando el usuario aplica una nueva configuración.
    """

    # Señales
    ip_cambiada = pyqtSignal(str)  # Emite la nueva IP cuando se aplica

    def __init__(
        self,
        modelo: ConexionModelo,
        vista: ConexionVista,
        parent=None
    ):
        """Inicializa el controlador.

        Args:
            modelo: Modelo de la conexión
            vista: Vista de la conexión
            parent: Objeto padre (opcional)
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
        self._vista.input_ip.textChanged.connect(self._on_ip_changed)
        self._vista.boton_aplicar.clicked.connect(self._on_aplicar_clicked)

    def _on_ip_changed(self, texto: str):
        """Handler de cambio de texto en input IP.

        Valida la IP en tiempo real y actualiza el feedback visual.

        Args:
            texto: Nuevo texto del input
        """
        # Validar IP
        valida, mensaje = ConexionModelo.validar_ip(texto)

        # Actualizar modelo
        self._modelo = replace(
            self._modelo,
            ip=texto,
            ip_valida=valida,
            mensaje_error=mensaje
        )

        # Actualizar vista
        self._vista.actualizar(self._modelo)

    def _on_aplicar_clicked(self):
        """Handler de click en botón Aplicar.

        Solo aplica la configuración si la IP es válida.
        """
        if self._modelo.ip_valida:
            # Emitir señal con la nueva IP
            self.ip_cambiada.emit(self._modelo.ip)
            logger.info("Nueva IP aplicada: %s", self._modelo.ip)
        else:
            logger.warning(
                "Intento de aplicar IP inválida: %s (%s)",
                self._modelo.ip,
                self._modelo.mensaje_error
            )

    @property
    def modelo(self) -> ConexionModelo:
        """Retorna el modelo actual."""
        return self._modelo
