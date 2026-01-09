"""Vista para el Panel de Conexión.

Responsable de la presentación de los controles de conexión.
"""

from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from compartido.widgets.config_panel import ConfigPanel, ConfigPanelLabels
from ..base import ModeloBase
from .modelo import ConfiguracionConexion, EstadoConexion


@dataclass(frozen=True)
class ConfigPanelConexionVista:
    """Configuración visual del panel de conexión."""

    ip_label: str = "IP Servidor:"
    puerto_label: str = "Puerto:"
    texto_conectar: str = "Conectar"
    texto_desconectar: str = "Desconectar"
    ip_placeholder: str = "xxx.xxx.xxx.xxx"


class PanelConexionVista(QWidget):
    """Vista del panel de configuración de conexión.

    Wrapper alrededor de ConfigPanel del módulo compartido.
    Propaga las señales del ConfigPanel y provee interfaz unificada.

    Signals:
        conexion_solicitada: Emitido cuando se solicita conectar.
        desconexion_solicitada: Emitido cuando se solicita desconectar.
        ip_cambiada: Emitido cuando cambia la IP.
        puerto_cambiado: Emitido cuando cambia el puerto.
    """

    conexion_solicitada = pyqtSignal()
    desconexion_solicitada = pyqtSignal()
    ip_cambiada = pyqtSignal(str)
    puerto_cambiado = pyqtSignal(int)

    def __init__(
        self,
        config: Optional[ConfigPanelConexionVista] = None,
        ip_inicial: str = "127.0.0.1",
        puerto_inicial: int = 14001,
        parent: Optional[QWidget] = None
    ) -> None:
        """Inicializa la vista del panel de conexión.

        Args:
            config: Configuración visual del panel.
            ip_inicial: IP por defecto.
            puerto_inicial: Puerto por defecto.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._config = config or ConfigPanelConexionVista()
        self._ip_anterior = ip_inicial
        self._puerto_anterior = puerto_inicial
        self._setup_ui(ip_inicial, puerto_inicial)
        self._conectar_signals()

    def _setup_ui(self, ip_inicial: str, puerto_inicial: int) -> None:
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        labels = ConfigPanelLabels(
            ip_label=self._config.ip_label,
            port_label=self._config.puerto_label,
            connect_text=self._config.texto_conectar,
            disconnect_text=self._config.texto_desconectar,
            ip_placeholder=self._config.ip_placeholder,
        )

        self._config_panel = ConfigPanel(
            default_ip=ip_inicial,
            default_port=puerto_inicial,
            labels=labels,
        )
        layout.addWidget(self._config_panel)

    def _conectar_signals(self) -> None:
        """Conecta las señales internas."""
        self._config_panel.connect_requested.connect(
            self.conexion_solicitada.emit
        )
        self._config_panel.disconnect_requested.connect(
            self.desconexion_solicitada.emit
        )
        self._config_panel.config_changed.connect(self._on_config_changed)

    def _on_config_changed(self) -> None:
        """Maneja cambios en la configuración."""
        ip_actual = self._config_panel.get_ip()
        puerto_actual = self._config_panel.get_port()

        if ip_actual != self._ip_anterior:
            self._ip_anterior = ip_actual
            self.ip_cambiada.emit(ip_actual)

        if puerto_actual != self._puerto_anterior:
            self._puerto_anterior = puerto_actual
            self.puerto_cambiado.emit(puerto_actual)

    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo.

        Args:
            modelo: Instancia de ConfiguracionConexion.
        """
        if not isinstance(modelo, ConfiguracionConexion):
            return

        # Actualizar valores sin disparar señales
        if self._config_panel.get_ip() != modelo.ip:
            self._config_panel.set_ip(modelo.ip)
            self._ip_anterior = modelo.ip

        if self._config_panel.get_port() != modelo.puerto:
            self._config_panel.set_port(modelo.puerto)
            self._puerto_anterior = modelo.puerto

        # Actualizar estado de conexión
        self._config_panel.set_connected_state(modelo.esta_conectado)

    @property
    def ip(self) -> str:
        """Retorna la IP configurada."""
        return self._config_panel.get_ip()

    @property
    def puerto(self) -> int:
        """Retorna el puerto configurado."""
        return self._config_panel.get_port()

    @property
    def esta_conectado(self) -> bool:
        """Retorna el estado de conexión visual."""
        return self._config_panel.is_connected()

    @property
    def ip_valida(self) -> bool:
        """Indica si la IP actual es válida."""
        return self._config_panel.is_ip_valid()

    def set_ip(self, ip: str) -> None:
        """Establece la IP."""
        self._config_panel.set_ip(ip)
        self._ip_anterior = ip

    def set_puerto(self, puerto: int) -> None:
        """Establece el puerto."""
        self._config_panel.set_port(puerto)
        self._puerto_anterior = puerto

    def set_estado_conexion(self, conectado: bool) -> None:
        """Establece el estado visual de conexión."""
        self._config_panel.set_connected_state(conectado)

    @property
    def config_panel(self) -> ConfigPanel:
        """Retorna el ConfigPanel interno para acceso directo."""
        return self._config_panel
