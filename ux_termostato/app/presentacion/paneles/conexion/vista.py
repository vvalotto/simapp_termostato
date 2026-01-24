"""Vista del panel de configuración de conexión."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QLabel, QPushButton, QGroupBox
)

from .modelo import ConexionModelo


class ConexionVista(QWidget):
    """Vista del panel de conexión.

    Permite configurar la dirección IP del Raspberry Pi y muestra
    los puertos de recepción y envío. Incluye validación visual de IP.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inicializar_ui()

    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # GroupBox
        group = QGroupBox("Configuración de Conexión")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        group_layout = QFormLayout()
        group_layout.setSpacing(15)

        # Campo IP
        self._input_ip = QLineEdit()
        self._input_ip.setPlaceholderText("192.168.1.50")
        self._input_ip.setMaxLength(15)

        # Label de validación
        self._label_validacion = QLabel("")
        self._label_validacion.setStyleSheet("color: #dc3545; font-size: 11px;")

        # Layout IP + validación
        ip_layout = QVBoxLayout()
        ip_layout.setSpacing(5)
        ip_layout.addWidget(self._input_ip)
        ip_layout.addWidget(self._label_validacion)

        # Puerto recv (read-only)
        self._input_puerto_recv = QLineEdit()
        self._input_puerto_recv.setReadOnly(True)
        self._input_puerto_recv.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #888888;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
            }
        """)

        # Puerto send (read-only)
        self._input_puerto_send = QLineEdit()
        self._input_puerto_send.setReadOnly(True)
        self._input_puerto_send.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: #888888;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
            }
        """)

        # Form layout
        label_ip = QLabel("IP Raspberry Pi:")
        label_ip.setStyleSheet("color: #cccccc; font-size: 13px;")

        label_recv = QLabel("Puerto Recepción:")
        label_recv.setStyleSheet("color: #cccccc; font-size: 13px;")

        label_send = QLabel("Puerto Envío:")
        label_send.setStyleSheet("color: #cccccc; font-size: 13px;")

        group_layout.addRow(label_ip, ip_layout)
        group_layout.addRow(label_recv, self._input_puerto_recv)
        group_layout.addRow(label_send, self._input_puerto_send)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Botón aplicar
        self._btn_aplicar = QPushButton("✓ Aplicar Configuración")
        self._btn_aplicar.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        layout.addWidget(self._btn_aplicar)

        # Stretch
        layout.addStretch()

        # Estilos del input IP (estado inicial)
        self._aplicar_estilos_ip_normal()

    def _aplicar_estilos_ip_normal(self):
        """Aplica estilos normales al input de IP."""
        self._input_ip.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)

    def _aplicar_estilos_ip_valida(self):
        """Aplica estilos de IP válida."""
        self._input_ip.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #28a745;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #28a745;
            }
        """)

    def _aplicar_estilos_ip_invalida(self):
        """Aplica estilos de IP inválida."""
        self._input_ip.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #dc3545;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #dc3545;
            }
        """)

    def actualizar(self, modelo: ConexionModelo):
        """Actualiza la vista desde el modelo.

        Args:
            modelo: Modelo con la configuración actual
        """
        # IP
        self._input_ip.setText(modelo.ip)

        # Puertos
        self._input_puerto_recv.setText(str(modelo.puerto_recv))
        self._input_puerto_send.setText(str(modelo.puerto_send))

        # Validación visual
        if modelo.ip_valida:
            # Borde verde
            self._aplicar_estilos_ip_valida()
            self._label_validacion.setText("")
            self._btn_aplicar.setEnabled(True)
        else:
            # Borde rojo
            self._aplicar_estilos_ip_invalida()
            self._label_validacion.setText(f"❌ {modelo.mensaje_error}")
            self._btn_aplicar.setEnabled(False)

    @property
    def input_ip(self) -> QLineEdit:
        """Retorna el input de IP."""
        return self._input_ip

    @property
    def boton_aplicar(self) -> QPushButton:
        """Retorna el botón de aplicar."""
        return self._btn_aplicar
