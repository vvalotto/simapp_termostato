"""Script de validación visual para paneles del Sprint 2.

Crea una ventana con los 3 paneles nuevos y simula datos del RPi
para verificar que funcionan correctamente antes de implementar tests.

Paneles incluidos:
- US-011: SelectorVista (toggle ambiente/deseada)
- US-015: EstadoConexion (indicador LED de conexión)
- US-013: Conexion (configuración IP/puertos)
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QGroupBox
)
from PyQt6.QtCore import QTimer

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.configuracion.config import ConfigUX
from app.factory import ComponenteFactoryUX

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VentanaValidacion(QMainWindow):
    """Ventana de validación visual de los paneles del Sprint 2."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validación Visual - Sprint 2 UX Termostato")
        self.setGeometry(100, 100, 800, 700)

        # Crear factory con configuración mock
        config = self._crear_config_mock()
        self.factory = ComponenteFactoryUX(config)

        # Crear los 3 paneles del Sprint 2
        self.paneles = {
            "selector_vista": self.factory.crear_panel_selector_vista(),
            "estado_conexion": self.factory.crear_panel_estado_conexion(),
            "conexion": self.factory.crear_panel_conexion(),
        }

        # Crear interfaz
        self._crear_ui()

        # Conectar señales para logging
        self._conectar_signals()

        logger.info("Ventana de validación inicializada")

    def _crear_config_mock(self) -> ConfigUX:
        """Crea configuración mock para testing."""
        return ConfigUX(
            ip_raspberry="192.168.1.50",
            puerto_recv=14001,
            puerto_send=14000,
            intervalo_recepcion_ms=500,
            intervalo_actualizacion_ui_ms=100,
            temperatura_min_setpoint=15.0,
            temperatura_max_setpoint=30.0,
            temperatura_setpoint_inicial=22.0,
        )

    def _crear_ui(self):
        """Crea la interfaz de usuario."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título principal
        titulo = QLabel("Paneles del Sprint 2 - Validación Visual")
        titulo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 10px;
            background-color: #007bff;
            border-radius: 5px;
        """)
        layout.addWidget(titulo)

        # Panel 1: Selector Vista
        layout.addWidget(self._crear_seccion("US-011: Selector Vista"))
        layout.addWidget(self.paneles["selector_vista"][1])  # Vista

        # Panel 2: Estado Conexión
        layout.addWidget(self._crear_seccion("US-015: Estado Conexión"))
        layout.addWidget(self.paneles["estado_conexion"][1])  # Vista

        # Botones de simulación de estados de conexión
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_conectado = QPushButton("Simular: Conectado")
        btn_conectado.setStyleSheet(self._estilo_boton("#28a745"))
        btn_conectado.clicked.connect(lambda: self._simular_estado("conectado"))

        btn_desconectado = QPushButton("Simular: Desconectado")
        btn_desconectado.setStyleSheet(self._estilo_boton("#dc3545"))
        btn_desconectado.clicked.connect(lambda: self._simular_estado("desconectado"))

        btn_conectando = QPushButton("Simular: Conectando")
        btn_conectando.setStyleSheet(self._estilo_boton("#ffc107"))
        btn_conectando.clicked.connect(lambda: self._simular_estado("conectando"))

        btn_layout.addWidget(btn_conectado)
        btn_layout.addWidget(btn_desconectado)
        btn_layout.addWidget(btn_conectando)
        layout.addLayout(btn_layout)

        # Panel 3: Configuración IP
        layout.addWidget(self._crear_seccion("US-013: Configuración IP"))
        layout.addWidget(self.paneles["conexion"][1])  # Vista

        # Info de ayuda
        info = QLabel(
            "💡 Tip: Observa la consola para ver las señales PyQt emitidas\n"
            "   - Cambia entre Ambiente/Deseada para probar US-011\n"
            "   - Usa botones de simulación para probar US-015\n"
            "   - Modifica la IP y presiona Aplicar para probar US-013"
        )
        info.setStyleSheet("""
            color: #cccccc;
            background-color: #2d2d2d;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        """)
        layout.addWidget(info)

        layout.addStretch()

        # Aplicar tema oscuro global
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

    def _crear_seccion(self, titulo: str) -> QWidget:
        """Crea un separador de sección.

        Args:
            titulo: Título de la sección

        Returns:
            Widget QLabel con estilo de sección
        """
        label = QLabel(titulo)
        label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00aaff;
            padding: 8px;
            border-bottom: 2px solid #555555;
            margin-top: 10px;
        """)
        return label

    def _estilo_boton(self, color: str) -> str:
        """Genera stylesheet para botón con color personalizado.

        Args:
            color: Color hex del botón

        Returns:
            String con CSS del botón
        """
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                padding: 11px 14px 9px 16px;
            }}
        """

    def _conectar_signals(self):
        """Conecta señales de los paneles para logging."""
        # SelectorVista
        ctrl_selector = self.paneles["selector_vista"][2]
        ctrl_selector.modo_cambiado.connect(
            lambda modo: logger.info("✓ SEÑAL modo_cambiado: %s", modo)
        )

        # EstadoConexion
        ctrl_estado = self.paneles["estado_conexion"][2]
        ctrl_estado.estado_cambiado.connect(
            lambda estado: logger.info("✓ SEÑAL estado_cambiado: %s", estado)
        )

        # Conexion
        ctrl_conexion = self.paneles["conexion"][2]
        ctrl_conexion.ip_cambiada.connect(
            lambda ip: logger.info("✓ SEÑAL ip_cambiada: %s", ip)
        )

    def _simular_estado(self, estado: str):
        """Simula un cambio de estado de conexión.

        Args:
            estado: Estado a simular ("conectado", "desconectado", "conectando")
        """
        ctrl_estado = self.paneles["estado_conexion"][2]

        if estado == "conectado":
            ctrl_estado.conexion_establecida("192.168.1.50:14001")
        elif estado == "desconectado":
            ctrl_estado.conexion_perdida()
        elif estado == "conectando":
            ctrl_estado.conectando()

        logger.info("Simulación de estado: %s", estado)


def main():
    """Entry point de la aplicación de validación."""
    logger.info("Iniciando validación visual del Sprint 2...")

    app = QApplication(sys.argv)
    app.setApplicationName("Validación Sprint 2")
    app.setOrganizationName("ISSE")

    ventana = VentanaValidacion()
    ventana.show()

    logger.info("Ventana mostrada. Esperando interacción del usuario...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
