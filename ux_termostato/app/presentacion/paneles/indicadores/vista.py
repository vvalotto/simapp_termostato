"""
Vista del panel de Indicadores de Alerta.

Este módulo define la vista MVC que renderiza los indicadores LED
de alerta del termostato (falla sensor y batería baja).
"""
# pylint: disable=no-name-in-module,import-error

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from compartido.widgets import LEDIndicator
from compartido.widgets.led_color_provider import LEDColor

from .modelo import IndicadoresModelo


class AlertLED(QWidget):
    """
    Widget que combina un LEDIndicator con un label y animación pulsante.

    Este widget encapsula la funcionalidad de un LED de alerta que puede
    parpadear cuando está activo.

    Attributes:
        led: El indicador LED
        label: Label descriptivo del LED
    """

    def __init__(self, label_text: str, color: LEDColor, size: int = 24):
        """
        Inicializa el AlertLED.

        Args:
            label_text: Texto del label (ej: "Sensor", "Batería")
            color: Color del LED cuando está activo
            size: Tamaño del LED en píxeles
        """
        super().__init__()
        self._color = color
        self._animacion_activa = False

        # Crear layout vertical (LED arriba, label abajo)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Crear LED indicator
        self.led = LEDIndicator(color=color, size=size, state=False)

        # Crear label
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)

        # Agregar widgets al layout
        layout.addWidget(self.led)
        layout.addWidget(self.label)

        self.setLayout(layout)

        # Timer para animación pulsante (toggle cada 500ms)
        self._timer_pulso = QTimer(self)
        self._timer_pulso.setInterval(500)
        self._timer_pulso.timeout.connect(self._pulsar)

    def set_estado(self, activo: bool, pulsar: bool = False):
        """
        Establece el estado del LED.

        Args:
            activo: True para encender el LED, False para apagar
            pulsar: True para activar animación pulsante
        """
        self.led.set_state(activo)

        if pulsar and activo:
            self._iniciar_pulso()
        else:
            self._detener_pulso()

    def _iniciar_pulso(self):
        """Inicia la animación pulsante del LED."""
        if not self._animacion_activa:
            self._animacion_activa = True
            self._timer_pulso.start()

    def _detener_pulso(self):
        """Detiene la animación pulsante del LED."""
        if self._animacion_activa:
            self._animacion_activa = False
            self._timer_pulso.stop()
            self.led.set_state(False)

    def _pulsar(self):
        """Toggle del estado del LED para crear efecto pulsante."""
        self.led.toggle()


class IndicadoresVista(QWidget):
    """
    Vista del panel de indicadores de alerta.

    Renderiza:
    - LED izquierdo: estado del sensor (gris apagado / rojo pulsante)
    - LED derecho: estado de batería (gris apagado / amarillo pulsante)
    - Labels descriptivos para cada LED
    """

    def __init__(self):
        """Inicializa la vista de indicadores."""
        super().__init__()
        self._setup_ui()
        self._aplicar_estilos()

    def _setup_ui(self):
        """Configura los widgets y layout de la vista."""
        # Layout principal horizontal
        layout = QHBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(15, 10, 15, 10)

        # AlertLED para sensor (rojo)
        self.alert_sensor = AlertLED("Sensor", LEDColor.RED, size=24)

        # AlertLED para batería (amarillo)
        self.alert_bateria = AlertLED("Batería", LEDColor.YELLOW, size=24)

        # Agregar widgets al layout
        layout.addWidget(self.alert_sensor)
        layout.addWidget(self.alert_bateria)
        layout.addStretch()  # Empuja los LEDs hacia la izquierda

        self.setLayout(layout)
        self.setObjectName("panelIndicadores")

    def _aplicar_estilos(self):
        """Aplica estilos CSS al panel de indicadores."""
        self.setStyleSheet("""
            QWidget#panelIndicadores {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 5px;
            }

            QLabel {
                color: #cbd5e1;
                background: transparent;
            }
        """)

    def actualizar(self, modelo: IndicadoresModelo):
        """
        Actualiza la vista basándose en el modelo.

        Args:
            modelo: Modelo con el estado de los indicadores
        """
        # Actualizar LED sensor
        if modelo.falla_sensor:
            self.alert_sensor.set_estado(activo=True, pulsar=True)
        else:
            self.alert_sensor.set_estado(activo=False, pulsar=False)

        # Actualizar LED batería
        if modelo.bateria_baja:
            self.alert_bateria.set_estado(activo=True, pulsar=True)
        else:
            self.alert_bateria.set_estado(activo=False, pulsar=False)
