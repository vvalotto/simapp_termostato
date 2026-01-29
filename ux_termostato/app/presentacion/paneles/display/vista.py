"""
Vista del panel Display LCD.

Este módulo define la vista MVC que renderiza el display principal del termostato,
mostrando la temperatura en un formato tipo LCD verde oscuro.
"""

import logging
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .modelo import DisplayModelo

logger = logging.getLogger(__name__)


class DisplayVista(QWidget):
    """
    Vista del display LCD principal del termostato.

    Renderiza:
    - Label superior con modo (Temperatura Ambiente/Deseada)
    - Valor de temperatura en fuente grande (≥48px)
    - Unidad °C
    - Mensaje de error cuando corresponde
    - Fondo verde oscuro simulando LCD
    """

    def __init__(self):
        """Inicializa la vista del display."""
        super().__init__()
        self._setup_ui()
        self._aplicar_estilos()

    def _setup_ui(self):
        """Configura los widgets y layout de la vista."""
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(20, 20, 20, 20)

        # Label del modo (superior)
        self.label_modo = QLabel("Temperatura Ambiente")
        self.label_modo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_modo.setObjectName("labelModo")

        # Container para temperatura y unidad
        container_temp = QWidget()
        layout_temp = QVBoxLayout()
        layout_temp.setSpacing(0)
        layout_temp.setContentsMargins(0, 10, 0, 10)

        # Label del valor de temperatura (grande)
        self.label_temp = QLabel("--.-")  # Placeholder, el controlador actualiza con valor real
        self.label_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_temp.setObjectName("labelTemp")

        # Configurar fuente grande para temperatura
        font_temp = QFont()
        font_temp.setPointSize(56)  # >48px como requiere la US
        font_temp.setBold(True)
        self.label_temp.setFont(font_temp)

        # Label de la unidad
        self.label_unidad = QLabel("°C")
        self.label_unidad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_unidad.setObjectName("labelUnidad")
        font_unidad = QFont()
        font_unidad.setPointSize(24)
        self.label_unidad.setFont(font_unidad)

        # Label de error (oculto por defecto)
        self.label_error = QLabel("⚠️ ERROR")
        self.label_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_error.setObjectName("labelError")
        self.label_error.setVisible(False)
        font_error = QFont()
        font_error.setPointSize(32)
        font_error.setBold(True)
        self.label_error.setFont(font_error)

        # Agregar al layout de temperatura
        layout_temp.addWidget(self.label_temp)
        layout_temp.addWidget(self.label_unidad)
        layout_temp.addWidget(self.label_error)
        container_temp.setLayout(layout_temp)

        # Agregar todos los widgets al layout principal
        layout.addWidget(self.label_modo)
        layout.addWidget(container_temp)

        self.setLayout(layout)
        self.setObjectName("displayLCD")

    def _aplicar_estilos(self):
        """Aplica estilos CSS al display para simular LCD verde."""
        self.setStyleSheet("""
            QWidget#displayLCD {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #065f46,
                    stop:1 #064e3b
                );
                border: 3px solid #047857;
                border-radius: 15px;
                min-height: 180px;
            }

            QLabel#labelModo {
                color: #6ee7b7;
                font-size: 14px;
                font-weight: normal;
                letter-spacing: 1px;
                background: transparent;
            }

            QLabel#labelTemp {
                color: #10b981;
                background: transparent;
                font-family: 'Courier New', monospace;
            }

            QLabel#labelUnidad {
                color: #34d399;
                background: transparent;
                margin-top: -10px;
            }

            QLabel#labelError {
                color: #ef4444;
                background: transparent;
            }
        """)

    def actualizar(self, modelo: DisplayModelo):
        """
        Actualiza la vista con los datos del modelo.

        Args:
            modelo: Instancia de DisplayModelo con el estado actual
        """
        logger.debug("🎨 Vista renderizando: temp=%.1f°C, encendido=%s, error=%s",
                    modelo.temperatura, modelo.encendido, modelo.error_sensor)

        # Manejar estado apagado
        if not modelo.encendido:
            logger.info("🔴 Display: Sistema apagado, mostrando '---'")
            self.label_temp.setText("---")
            self.label_temp.setVisible(True)
            self.label_unidad.setVisible(True)
            self.label_error.setVisible(False)
            self.label_modo.setText("APAGADO")
            return

        # Manejar error de sensor
        if modelo.error_sensor:
            logger.warning("⚠️  Display: Error de sensor detectado")
            self.label_temp.setVisible(False)
            self.label_unidad.setVisible(False)
            self.label_error.setVisible(True)
            self.label_modo.setText("ERROR DE SENSOR")
            return

        # Estado normal: mostrar temperatura
        logger.info("🟢 Display: Mostrando temperatura %.1f°C", modelo.temperatura)
        self.label_temp.setVisible(True)
        self.label_unidad.setVisible(True)
        self.label_error.setVisible(False)

        # Actualizar valor de temperatura con un decimal
        self.label_temp.setText(f"{modelo.temperatura:.1f}")

        # Actualizar label de modo
        if modelo.modo_vista == "ambiente":
            self.label_modo.setText("Temperatura Ambiente")
        else:
            self.label_modo.setText("Temperatura Deseada")
