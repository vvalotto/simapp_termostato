"""
Widget ConfigPanel para configuración de conexión de red.

Proporciona un panel compacto horizontal con campos para IP y puerto,
botón de conexión/desconexión e indicador de estado.
"""
# pylint: disable=no-name-in-module
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal

from .ip_validator import IPValidator, DefaultIPValidator
from .status_indicator import StatusIndicator, LEDStatusIndicator
from .validation_feedback import ValidationFeedbackProvider, BorderValidationFeedback


@dataclass
class ConfigPanelLabels:
    """
    Etiquetas configurables para ConfigPanel.

    Permite personalizar los textos mostrados sin modificar
    la clase ConfigPanel.
    """
    ip_label: str = "IP:"
    port_label: str = "Puerto:"
    connect_text: str = "Conectar"
    disconnect_text: str = "Desconectar"
    ip_placeholder: str = "xxx.xxx.xxx.xxx"


class ConfigPanel(QWidget):  # pylint: disable=too-many-instance-attributes
    """
    Panel de configuración de conexión de red.

    Proporciona campos para IP y puerto, botón de conexión/desconexión
    y un indicador de estado de conexión. Layout compacto horizontal.

    Todas las dependencias son inyectables para cumplir con DIP:
    - StatusIndicator: indicador visual de estado
    - IPValidator: validación de direcciones IP
    - ValidationFeedbackProvider: feedback visual de validación
    - ConfigPanelLabels: textos de la interfaz

    Attributes:
        connect_requested: Señal emitida al solicitar conexión.
        disconnect_requested: Señal emitida al solicitar desconexión.
        config_changed: Señal emitida cuando IP o puerto cambian.

    Example:
        # Uso básico con valores por defecto
        panel = ConfigPanel()

        # Uso con dependencias personalizadas
        panel = ConfigPanel(
            status_indicator=LEDStatusIndicator(color=LEDColor.BLUE),
            ip_validator=CustomIPValidator(),
            validation_feedback=CustomFeedback(),
            labels=ConfigPanelLabels(connect_text="Connect")
        )
    """

    connect_requested = pyqtSignal()
    disconnect_requested = pyqtSignal()
    config_changed = pyqtSignal()

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        parent: QWidget | None = None,
        default_ip: str = "localhost",
        default_port: int = 14001,
        status_indicator: StatusIndicator | None = None,
        ip_validator: IPValidator | None = None,
        validation_feedback: ValidationFeedbackProvider | None = None,
        labels: ConfigPanelLabels | None = None
    ):
        """
        Inicializa el panel de configuración.

        Args:
            parent: Widget padre.
            default_ip: Dirección IP por defecto.
            default_port: Puerto por defecto.
            status_indicator: Indicador de estado (opcional).
                             Si no se especifica, usa LEDStatusIndicator.
            ip_validator: Validador de IP (opcional).
                         Si no se especifica, usa DefaultIPValidator.
            validation_feedback: Proveedor de feedback visual (opcional).
                                Si no se especifica, usa BorderValidationFeedback.
            labels: Etiquetas de texto (opcional).
                   Si no se especifica, usa valores por defecto en español.
        """
        super().__init__(parent)

        # Inyección de dependencias con defaults
        self._status_indicator = status_indicator or LEDStatusIndicator()
        self._ip_validator = ip_validator or DefaultIPValidator()
        self._validation_feedback = validation_feedback or BorderValidationFeedback()
        self._labels = labels or ConfigPanelLabels()

        self._is_connected = False

        self._setup_ui(default_ip, default_port)
        self._connect_signals()

    def _setup_ui(self, default_ip: str, default_port: int) -> None:
        """Configura la interfaz de usuario."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Indicador de estado (inyectado)
        layout.addWidget(self._status_indicator.get_widget())

        # Campo IP
        self._ip_input = self._create_ip_input(default_ip)
        layout.addWidget(QLabel(self._labels.ip_label))
        layout.addWidget(self._ip_input)

        # Campo puerto
        self._port_input = self._create_port_input(default_port)
        layout.addWidget(QLabel(self._labels.port_label))
        layout.addWidget(self._port_input)

        # Botón conectar/desconectar
        self._connect_button = QPushButton(self._labels.connect_text)
        self._connect_button.setMinimumWidth(100)
        layout.addWidget(self._connect_button)

        layout.addStretch()

    def _create_ip_input(self, default_ip: str) -> QLineEdit:
        """Crea y configura el campo de entrada de IP."""
        ip_input = QLineEdit()
        ip_input.setText(default_ip)
        ip_input.setPlaceholderText(self._labels.ip_placeholder)
        ip_input.setMaximumWidth(140)
        ip_input.setMinimumWidth(100)
        return ip_input

    def _create_port_input(self, default_port: int) -> QSpinBox:
        """Crea y configura el campo de entrada de puerto."""
        port_input = QSpinBox()
        port_input.setRange(1, 65535)
        port_input.setValue(default_port)
        port_input.setMinimumWidth(70)
        return port_input

    def _connect_signals(self) -> None:
        """Conecta las señales internas."""
        self._connect_button.clicked.connect(self._on_button_clicked)
        self._ip_input.textChanged.connect(self._on_config_changed)
        self._port_input.valueChanged.connect(self._on_config_changed)

    def _on_button_clicked(self) -> None:
        """Maneja el clic del botón conectar/desconectar."""
        if self._is_connected:
            self.disconnect_requested.emit()
        else:
            if self._validate_and_show_feedback():
                self.connect_requested.emit()

    def _on_config_changed(self) -> None:
        """Maneja cambios en la configuración."""
        self._validate_and_show_feedback()
        self.config_changed.emit()

    def _validate_and_show_feedback(self) -> bool:
        """
        Valida la IP y muestra feedback visual.

        Returns:
            True si la IP es válida, False en caso contrario.
        """
        ip = self._ip_input.text()
        is_valid = self._ip_validator.validate(ip)

        if is_valid:
            self._validation_feedback.show_valid(self._ip_input)
        else:
            self._validation_feedback.show_invalid(
                self._ip_input,
                self._ip_validator.get_error_message()
            )

        return is_valid

    def _update_ui_for_connection_state(self) -> None:
        """Actualiza la UI según el estado de conexión."""
        if self._is_connected:
            self._connect_button.setText(self._labels.disconnect_text)
            self._ip_input.setEnabled(False)
            self._port_input.setEnabled(False)
        else:
            self._connect_button.setText(self._labels.connect_text)
            self._ip_input.setEnabled(True)
            self._port_input.setEnabled(True)

    # === Propiedades y métodos públicos ===

    @property
    def status_indicator(self) -> StatusIndicator:
        """Retorna el indicador de estado actual."""
        return self._status_indicator

    @property
    def ip_validator(self) -> IPValidator:
        """Retorna el validador de IP actual."""
        return self._ip_validator

    @property
    def validation_feedback(self) -> ValidationFeedbackProvider:
        """Retorna el proveedor de feedback de validación."""
        return self._validation_feedback

    @property
    def labels(self) -> ConfigPanelLabels:
        """Retorna las etiquetas configuradas."""
        return self._labels

    def set_ip_validator(self, validator: IPValidator) -> None:
        """
        Cambia el validador de IP.

        Args:
            validator: Nuevo validador de IP.
        """
        self._ip_validator = validator
        self._validate_and_show_feedback()

    def set_validation_feedback(self, feedback: ValidationFeedbackProvider) -> None:
        """
        Cambia el proveedor de feedback de validación.

        Args:
            feedback: Nuevo proveedor de feedback.
        """
        self._validation_feedback = feedback
        self._validate_and_show_feedback()

    def get_ip(self) -> str:
        """
        Retorna la dirección IP configurada.

        Returns:
            Dirección IP actual sin espacios.
        """
        return self._ip_input.text().strip()

    def set_ip(self, ip: str) -> None:
        """
        Establece la dirección IP.

        Args:
            ip: Nueva dirección IP.
        """
        self._ip_input.setText(ip)

    def get_port(self) -> int:
        """
        Retorna el puerto configurado.

        Returns:
            Número de puerto actual.
        """
        return self._port_input.value()

    def set_port(self, port: int) -> None:
        """
        Establece el puerto.

        Args:
            port: Nuevo número de puerto (1-65535).
        """
        self._port_input.setValue(port)

    def set_connected_state(self, connected: bool) -> None:
        """
        Actualiza el estado de conexión del panel.

        Args:
            connected: True si está conectado, False si no.
        """
        self._is_connected = connected
        self._status_indicator.set_state(connected)
        self._update_ui_for_connection_state()

    def is_connected(self) -> bool:
        """
        Retorna el estado de conexión actual.

        Returns:
            True si está conectado, False si no.
        """
        return self._is_connected

    def is_ip_valid(self) -> bool:
        """
        Verifica si la IP actual es válida.

        Returns:
            True si la IP es válida, False si no.
        """
        return self._ip_validator.validate(self._ip_input.text())
