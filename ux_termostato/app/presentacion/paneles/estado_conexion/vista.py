"""Vista del panel de estado de conexión."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer

from compartido.widgets.led_indicator import LedIndicator
from .modelo import EstadoConexionModelo


class EstadoConexionVista(QWidget):
    """Vista del estado de conexión.

    Muestra un LED indicador y texto del estado actual de conexión con el RPi.
    Soporta animación pulsante para el estado "conectando".
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer_pulso = None
        self._pulso_activo = False
        self._inicializar_ui()

    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Label "Estado:"
        self._label = QLabel("Estado:")
        self._label.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 13px;")

        # LED indicator
        self._led = LedIndicator()
        self._led.setFixedSize(16, 16)

        # Label texto estado
        self._label_estado = QLabel("Desconectado")
        self._label_estado.setStyleSheet("color: #cccccc; font-size: 13px;")

        layout.addWidget(self._label)
        layout.addWidget(self._led)
        layout.addWidget(self._label_estado)
        layout.addStretch()

    def actualizar(self, modelo: EstadoConexionModelo):
        """Actualiza la vista desde el modelo.

        Args:
            modelo: Modelo con el estado actual de conexión
        """
        # Detener animación si existe
        self._detener_pulso()

        if modelo.estado == "conectado":
            self._led.set_color("green")
            self._led.set_active(True)
            self._label_estado.setText("Conectado")
            self._label_estado.setStyleSheet("color: #28a745; font-weight: bold; font-size: 13px;")

        elif modelo.estado == "desconectado":
            self._led.set_color("red")
            self._led.set_active(False)
            self._label_estado.setText("Desconectado")
            self._label_estado.setStyleSheet("color: #dc3545; font-size: 13px;")

        elif modelo.estado == "conectando":
            self._led.set_color("yellow")
            self._label_estado.setText("Conectando...")
            self._label_estado.setStyleSheet("color: #ffc107; font-size: 13px;")
            # Iniciar animación pulsante
            self._iniciar_pulso()

    def _iniciar_pulso(self):
        """Inicia animación pulsante del LED."""
        self._pulso_activo = True
        self._timer_pulso = QTimer(self)
        self._timer_pulso.timeout.connect(self._toggle_pulso)
        self._timer_pulso.start(500)  # 500ms

    def _detener_pulso(self):
        """Detiene animación pulsante del LED."""
        if self._timer_pulso:
            self._timer_pulso.stop()
            self._timer_pulso = None
        self._pulso_activo = False

    def _toggle_pulso(self):
        """Toggle del LED para efecto de animación."""
        if self._pulso_activo:
            self._led.set_active(not self._led.is_active)
