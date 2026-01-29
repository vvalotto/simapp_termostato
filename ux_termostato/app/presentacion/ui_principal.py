"""Ventana Principal de la aplicación UX Termostato.

Este módulo implementa la ventana principal (QMainWindow) que orquesta
todo el ciclo de vida de la aplicación: creación de componentes,
inicialización de servicios, ensamblado de UI y cleanup.
"""

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# pylint: disable=wrong-import-position
# Agregar path para imports de compartido (debe estar antes de otros imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QScrollArea
from PyQt6.QtCore import QEvent, Qt

from compartido.estilos import load_dark_theme

if TYPE_CHECKING:
    from ..factory import ComponenteFactoryUX
    from ..coordinator import UXCoordinator

from .ui_compositor import UICompositor
# pylint: enable=wrong-import-position

logger = logging.getLogger(__name__)


class VentanaPrincipalUX(QMainWindow):
    """Ventana Principal de UX Termostato Desktop.

    Responsabilidades:
    - Orquestar creación de componentes via Factory
    - Coordinar señales via Coordinator
    - Ensamblar UI via Compositor
    - Manejar ciclo de vida (iniciar/cerrar)
    - Aplicar tema oscuro
    """

    def __init__(self, factory: "ComponenteFactoryUX") -> None:
        """Inicializa la ventana principal.

        Args:
            factory: Factory para crear componentes de la aplicación
        """
        super().__init__()

        self._factory = factory
        self._componentes = {}          # Dict de paneles MVC
        self._servidor_estado = None    # ServidorEstado
        self._cliente_comandos = None   # ClienteComandos
        self._coordinator = None        # UXCoordinator
        self._compositor = None         # UICompositor

        logger.debug("VentanaPrincipalUX creada, iniciando configuración...")
        self._inicializar()

    def _inicializar(self) -> None:
        """Orquesta todo el proceso de inicialización.

        Llama a los métodos de configuración en orden:
        1. Configurar ventana (título, tamaño, tema)
        2. Crear componentes (paneles, servicios)
        3. Crear coordinator (conectar señales)
        4. Crear UI (ensamblar layout)
        """
        logger.info("Iniciando configuración de ventana principal...")

        self._configurar_ventana()
        self._crear_componentes()
        self._crear_coordinator()
        self._crear_ui()

        logger.info("Ventana principal configurada exitosamente")

    def _configurar_ventana(self) -> None:
        """Configura propiedades básicas de la ventana.

        - Título
        - Tamaño inicial y mínimo
        - Posición centrada en pantalla
        - Tema oscuro
        """
        # Título
        self.setWindowTitle("UX Termostato Desktop")

        # Tamaño
        self.resize(600, 800)
        self.setMinimumSize(500, 700)

        # Centrar en pantalla
        self._centrar_ventana()

        # Aplicar tema oscuro
        stylesheet = load_dark_theme()
        self.setStyleSheet(stylesheet)

        logger.debug(
            "Ventana configurada: título='%s', tamaño=%dx%d",
            self.windowTitle(),
            self.width(),
            self.height()
        )

    def _centrar_ventana(self) -> None:
        """Centra la ventana en la pantalla principal."""
        try:
            qr = self.frameGeometry()
            cp = QApplication.primaryScreen().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
            logger.debug("Ventana centrada en pantalla")
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("No se pudo centrar ventana: %s", e)

    def _crear_componentes(self) -> None:
        """Crea todos los componentes de la aplicación.

        - Paneles MVC via Factory
        - ServidorEstado
        - ClienteComandos

        Raises:
            RuntimeError: Si falla la creación de componentes críticos
        """
        try:
            logger.info("Creando componentes de la aplicación...")

            # Crear todos los paneles MVC
            self._componentes = self._factory.crear_todos_paneles()
            logger.info("Paneles MVC creados: %d paneles", len(self._componentes))

            # Crear servidor de estado (recibe JSON del RPi)
            self._servidor_estado = self._factory.crear_servidor_estado(parent=self)
            logger.info(
                "ServidorEstado creado (puerto %d)",
                self._factory.config.puerto_recv
            )

            # Crear cliente de comandos (envía comandos al RPi)
            self._cliente_comandos = self._factory.crear_cliente_comandos(parent=self)
            logger.info(
                "ClienteComandos creado (IP: %s, puerto %d)",
                self._factory.config.ip_raspberry,
                self._factory.config.puerto_send
            )

        except Exception as e:
            error_msg = f"Error crítico al crear componentes: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    def _crear_coordinator(self) -> None:
        """Crea el coordinator y conecta todas las señales PyQt.

        El coordinator es responsable de conectar las señales entre:
        - Servidor → Paneles (actualización de estado)
        - Paneles → Cliente (envío de comandos)
        - Panel Power → Otros paneles (habilitación/deshabilitación)

        Raises:
            RuntimeError: Si falla la creación o conexión del coordinator
        """
        try:
            # Import dinámico para evitar import circular
            from ..coordinator import UXCoordinator  # pylint: disable=import-outside-toplevel

            logger.info("Creando coordinator...")

            # Crear coordinator con todos los paneles
            # NOTA: El coordinator conecta las señales internamente en __init__
            self._coordinator = UXCoordinator(
                paneles=self._componentes,
                servidor_estado=self._servidor_estado,
                cliente_comandos=self._cliente_comandos,
                parent=self
            )

            logger.info(
                "Coordinator creado y señales conectadas (%d paneles)",
                len(self._componentes)
            )

        except Exception as e:
            error_msg = f"Error al crear coordinator: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    def _crear_ui(self) -> None:
        """Ensambla la interfaz de usuario completa.

        Usa UICompositor para ensamblar todos los paneles en un layout
        coherente y establece el widget central de la ventana con scroll.

        Raises:
            RuntimeError: Si falla el ensamblado de la UI
        """
        try:
            logger.info("Ensamblando interfaz de usuario...")

            # Crear compositor con todos los paneles
            self._compositor = UICompositor(self._componentes)

            # Crear layout completo
            widget_central = self._compositor.crear_layout()

            # Envolver en QScrollArea para que todos los paneles sean accesibles
            scroll_area = QScrollArea()
            scroll_area.setWidget(widget_central)
            scroll_area.setWidgetResizable(True)  # El widget se ajusta al ancho del scroll
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

            # Aplicar estilo para que el scroll sea visible
            scroll_area.setStyleSheet("""
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background: #1e293b;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background: #475569;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #64748b;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)

            # Establecer scroll area como widget central
            self.setCentralWidget(scroll_area)

            logger.info("Interfaz de usuario ensamblada exitosamente (con scroll)")

        except Exception as e:
            error_msg = f"Error al ensamblar UI: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    def iniciar(self) -> "VentanaPrincipalUX":
        """Inicia la aplicación.

        - Inicia el ServidorEstado (comienza a escuchar puerto)
        - Muestra la ventana

        Returns:
            self: Para permitir chaining

        Raises:
            RuntimeError: Si falla el inicio del servidor
        """
        try:
            logger.info("Iniciando aplicación...")

            # Iniciar servidor de estado
            if self._servidor_estado:
                self._servidor_estado.start()
                logger.info(
                    "ServidorEstado iniciado (escuchando en puerto %d)",
                    self._factory.config.puerto_recv
                )

            # Mostrar ventana
            self.show()
            logger.info("Ventana principal mostrada")

            logger.info("✓ Aplicación iniciada correctamente")
            return self

        except Exception as e:
            error_msg = f"Error al iniciar aplicación: {e}"
            logger.error(error_msg, exc_info=True)

            # Mostrar diálogo de error al usuario
            QMessageBox.critical(
                self,
                "Error de Inicio",
                f"No se pudo iniciar la aplicación:\n\n{e}\n\n"
                "Revise los logs para más detalles."
            )

            raise RuntimeError(error_msg) from e

    def cerrar(self) -> None:
        """Cierra la aplicación y limpia recursos.

        - Detiene el ServidorEstado
        - Cierra conexiones activas
        - Logging de cierre
        """
        logger.info("Cerrando aplicación...")

        try:
            # Detener servidor de estado
            if self._servidor_estado:
                self._servidor_estado.stop()
                logger.info("ServidorEstado detenido")

            # Aquí se podrían cerrar más recursos si es necesario
            # (por ahora no hay conexiones persistentes que cerrar)

            logger.info("✓ Aplicación cerrada correctamente")

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error al cerrar aplicación: %s", e, exc_info=True)

        finally:
            # Cerrar la ventana
            super().close()

    def closeEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        """Maneja el evento de cierre de la ventana.

        Override de QMainWindow.closeEvent() para asegurar cleanup
        apropiado cuando el usuario cierra la ventana.

        Args:
            event: Evento de cierre de Qt
        """
        logger.debug("Evento de cierre recibido")

        # Llamar a cleanup
        self.cerrar()

        # Aceptar el evento
        event.accept()
