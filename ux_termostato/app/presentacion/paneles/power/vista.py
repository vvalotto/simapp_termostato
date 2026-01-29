"""
Vista del panel Power (Encendido/Apagado).

Este módulo define la vista MVC que renderiza el botón de encendido/apagado
del termostato con estilos condicionales según el estado.
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .modelo import PowerModelo


class PowerVista(QWidget):
    """
    Vista del botón de encendido/apagado del termostato.

    Renderiza:
    - Botón "ENCENDER" (verde) cuando está apagado
    - Botón "APAGAR" (gris) cuando está encendido
    - Icono de power ⚡
    - Feedback visual al presionar
    """

    def __init__(self):
        """Inicializa la vista del panel power."""
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Configura los widgets y layout de la vista."""
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Botón principal de power
        self.btn_power = QPushButton("⚡ ENCENDER")
        self.btn_power.setObjectName("btnPower")
        self.btn_power.setCursor(Qt.CursorShape.PointingHandCursor)

        # Configurar fuente
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.btn_power.setFont(font)

        # Configurar tamaño mínimo
        self.btn_power.setMinimumHeight(60)
        self.btn_power.setMinimumWidth(200)

        # Agregar al layout
        layout.addWidget(self.btn_power)
        self.setLayout(layout)

        # Aplicar estilos iniciales (apagado)
        self._aplicar_estilo_apagado()

    def _aplicar_estilo_apagado(self):
        """Aplica estilos para estado apagado (botón verde ENCENDER)."""
        self.btn_power.setStyleSheet("""
            QPushButton#btnPower {
                background-color: #16a34a;  /* green-600 */
                color: white;
                border: 2px solid #15803d;  /* green-700 */
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#btnPower:hover {
                background-color: #15803d;  /* green-700 */
                border-color: #166534;      /* green-800 */
            }

            QPushButton#btnPower:pressed {
                background-color: #166534;  /* green-800 */
            }
        """)

    def _aplicar_estilo_encendido(self):
        """Aplica estilos para estado encendido (botón gris APAGAR)."""
        self.btn_power.setStyleSheet("""
            QPushButton#btnPower {
                background-color: #475569;  /* slate-600 */
                color: white;
                border: 2px solid #334155;  /* slate-700 */
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#btnPower:hover {
                background-color: #334155;  /* slate-700 */
                border-color: #1e293b;      /* slate-800 */
            }

            QPushButton#btnPower:pressed {
                background-color: #1e293b;  /* slate-800 */
            }
        """)

    def actualizar(self, modelo: PowerModelo):
        """
        Actualiza la vista con los datos del modelo.

        Args:
            modelo: Instancia de PowerModelo con el estado actual
        """
        if modelo.encendido:
            self.btn_power.setText("⚡ APAGAR")
            self._aplicar_estilo_encendido()
        else:
            self.btn_power.setText("⚡ ENCENDER")
            self._aplicar_estilo_apagado()
