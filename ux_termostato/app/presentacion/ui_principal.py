"""Ventana Principal de la aplicación UX Termostato.

Facade de lifecycle: configura la ventana, delega creación de componentes
y coordinator a la factory, y gestiona el ciclo de vida (iniciar/cerrar).
"""

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# pylint: disable=wrong-import-position
# Agregar path para imports de compartido (debe estar antes de otros imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.QtCore import QEvent

from compartido.estilos import load_dark_theme

if TYPE_CHECKING:
    from ..factory import ComponenteFactoryUX

from .ui_compositor import UICompositor
# pylint: enable=wrong-import-position

logger = logging.getLogger(__name__)


class VentanaPrincipalUX(QMainWindow):
    """Facade de lifecycle para UX Termostato Desktop.

    Responsabilidades:
    - Configurar la ventana (título, tamaño, tema)
    - Delegar creación de componentes al ComponenteFactoryUX
    - Delegar conexión de señales al UXCoordinator (vía factory)
    - Ensamblar UI vía UICompositor
    - Manejar ciclo de vida (iniciar/cerrar)
    """

    def __init__(self, factory: "ComponenteFactoryUX") -> None:
        super().__init__()
        self._factory = factory
        self._servidor_estado = None
        self._cliente_comandos = None
        self._coordinator = None
        self._compositor = None
        self._componentes = {}

        self._configurar_ventana()

        try:
            self._componentes = self._factory.crear_todos_paneles()
            self._servidor_estado = self._factory.crear_servidor_estado(parent=self)
            self._cliente_comandos = self._factory.crear_cliente_comandos(parent=self)
        except Exception as e:
            raise RuntimeError(f"Error crítico al crear componentes: {e}") from e

        try:
            self._coordinator = self._factory.crear_coordinator(
                paneles=self._componentes,
                servidor_estado=self._servidor_estado,
                cliente_comandos=self._cliente_comandos,
                parent=self,
            )
        except Exception as e:
            raise RuntimeError(f"Error al crear coordinator: {e}") from e

        self._compositor = UICompositor(self._componentes)
        self.setCentralWidget(self._compositor.crear_scroll_layout())

        logger.info("VentanaPrincipalUX inicializada")

    def _configurar_ventana(self) -> None:
        """Configura título, tamaño, posición y tema de la ventana."""
        self.setWindowTitle("UX Termostato Desktop")
        self.resize(600, 800)
        self.setMinimumSize(500, 700)
        self._centrar_ventana()
        self.setStyleSheet(load_dark_theme())

    def _centrar_ventana(self) -> None:
        """Centra la ventana en la pantalla principal."""
        try:
            qr = self.frameGeometry()
            cp = QApplication.primaryScreen().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("No se pudo centrar ventana: %s", e)

    def iniciar(self) -> "VentanaPrincipalUX":
        """Inicia el servidor de estado y muestra la ventana.

        Returns:
            self: Para permitir chaining.

        Raises:
            RuntimeError: Si falla el inicio del servidor.
        """
        try:
            if self._servidor_estado:
                self._servidor_estado.start()
            self.show()
            logger.info("Aplicación iniciada (puerto %d)", self._factory.config.puerto_recv)
            return self
        except Exception as e:
            error_msg = f"Error al iniciar aplicación: {e}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(
                self, "Error de Inicio",
                f"No se pudo iniciar la aplicación:\n\n{e}\n\nRevise los logs."
            )
            raise RuntimeError(error_msg) from e

    def cerrar(self) -> None:
        """Detiene el servidor de estado y cierra la ventana."""
        try:
            if self._servidor_estado:
                self._servidor_estado.stop()
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error al cerrar aplicación: %s", e, exc_info=True)
        finally:
            super().close()

    def closeEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        """Maneja el evento de cierre de ventana de Qt."""
        self.cerrar()
        event.accept()
