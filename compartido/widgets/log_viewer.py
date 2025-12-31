"""
Widget LogViewer para mostrar logs en tiempo real.

Proporciona un área de texto con scroll automático, colores por nivel
de log, timestamp automático y límite configurable de líneas.
"""
# pylint: disable=no-name-in-module
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QCheckBox,
)
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor
from PyQt6.QtCore import pyqtSignal

from .log_color_provider import LogLevel, LogColorProvider, DefaultLogColorProvider
from .log_formatter import LogFormatter, TimestampLogFormatter


@dataclass
class LogViewerLabels:
    """
    Etiquetas configurables para LogViewer.

    Permite personalizar los textos mostrados sin modificar
    la clase LogViewer.
    """
    clear_button: str = "Limpiar"
    auto_scroll_checkbox: str = "Auto-scroll"


class LogViewer(QWidget):  # pylint: disable=too-many-instance-attributes
    """
    Visor de logs en tiempo real.

    Muestra mensajes de log con colores según nivel, timestamp automático
    y funcionalidades de auto-scroll y límite de líneas.

    Todas las dependencias son inyectables para cumplir con DIP:
    - LogColorProvider: colores según nivel de log
    - LogFormatter: formato de los mensajes
    - LogViewerLabels: textos de la interfaz

    Attributes:
        log_added: Señal emitida cuando se agrega un log.
        logs_cleared: Señal emitida cuando se limpian los logs.

    Example:
        # Uso básico
        viewer = LogViewer()
        viewer.add_log("Conexión establecida", LogLevel.INFO)
        viewer.add_log("Timeout detectado", LogLevel.WARNING)
        viewer.add_log("Error de conexión", LogLevel.ERROR)

        # Con dependencias personalizadas
        viewer = LogViewer(
            color_provider=DarkThemeColors(),
            formatter=CompactFormatter(),
            max_lines=500
        )
    """

    log_added = pyqtSignal(str, LogLevel)
    logs_cleared = pyqtSignal()

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        parent: QWidget | None = None,
        color_provider: LogColorProvider | None = None,
        formatter: LogFormatter | None = None,
        labels: LogViewerLabels | None = None,
        max_lines: int = 1000,
        auto_scroll: bool = True
    ):
        """
        Inicializa el visor de logs.

        Args:
            parent: Widget padre.
            color_provider: Proveedor de colores (opcional).
                           Si no se especifica, usa DefaultLogColorProvider.
            formatter: Formateador de mensajes (opcional).
                      Si no se especifica, usa TimestampLogFormatter.
            labels: Etiquetas de texto (opcional).
            max_lines: Número máximo de líneas a mantener.
            auto_scroll: Si activar auto-scroll inicialmente.
        """
        super().__init__(parent)

        # Inyección de dependencias con defaults
        self._color_provider = color_provider or DefaultLogColorProvider()
        self._formatter = formatter or TimestampLogFormatter()
        self._labels = labels or LogViewerLabels()

        self._max_lines = max_lines
        self._auto_scroll = auto_scroll
        self._line_count = 0

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Área de texto para logs
        self._text_area = self._create_text_area()
        layout.addWidget(self._text_area)

        # Barra de controles
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        # Checkbox auto-scroll
        self._auto_scroll_checkbox = QCheckBox(self._labels.auto_scroll_checkbox)
        self._auto_scroll_checkbox.setChecked(self._auto_scroll)
        controls_layout.addWidget(self._auto_scroll_checkbox)

        controls_layout.addStretch()

        # Botón limpiar
        self._clear_button = QPushButton(self._labels.clear_button)
        self._clear_button.setMaximumWidth(100)
        controls_layout.addWidget(self._clear_button)

        layout.addLayout(controls_layout)

    def _create_text_area(self) -> QTextEdit:
        """Crea y configura el área de texto."""
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Estilo para fondo oscuro
        text_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #3c3c3c;
            }
        """)

        return text_area

    def _connect_signals(self) -> None:
        """Conecta las señales internas."""
        self._clear_button.clicked.connect(self.clear_logs)
        self._auto_scroll_checkbox.stateChanged.connect(self._on_auto_scroll_changed)

    def _on_auto_scroll_changed(self, state: int) -> None:
        """Maneja cambios en el checkbox de auto-scroll."""
        self._auto_scroll = state == 2  # Qt.CheckState.Checked = 2

    def _apply_line_limit(self) -> None:
        """Aplica el límite de líneas eliminando las más antiguas."""
        if self._line_count <= self._max_lines:
            return

        cursor = self._text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # Calcular líneas a eliminar
        lines_to_remove = self._line_count - self._max_lines

        for _ in range(lines_to_remove):
            cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)

        cursor.removeSelectedText()
        self._line_count = self._max_lines

    def _scroll_to_bottom(self) -> None:
        """Desplaza el área de texto al final."""
        scrollbar = self._text_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # === Propiedades ===

    @property
    def color_provider(self) -> LogColorProvider:
        """Retorna el proveedor de colores actual."""
        return self._color_provider

    @property
    def formatter(self) -> LogFormatter:
        """Retorna el formateador actual."""
        return self._formatter

    @property
    def labels(self) -> LogViewerLabels:
        """Retorna las etiquetas configuradas."""
        return self._labels

    @property
    def max_lines(self) -> int:
        """Retorna el límite máximo de líneas."""
        return self._max_lines

    @max_lines.setter
    def max_lines(self, value: int) -> None:
        """Establece el límite máximo de líneas."""
        self._max_lines = max(1, value)
        self._apply_line_limit()

    @property
    def auto_scroll(self) -> bool:
        """Retorna si auto-scroll está activo."""
        return self._auto_scroll

    @auto_scroll.setter
    def auto_scroll(self, value: bool) -> None:
        """Establece el estado de auto-scroll."""
        self._auto_scroll = value
        self._auto_scroll_checkbox.setChecked(value)

    @property
    def line_count(self) -> int:
        """Retorna el número actual de líneas."""
        return self._line_count

    # === Métodos públicos ===

    def set_color_provider(self, provider: LogColorProvider) -> None:
        """
        Cambia el proveedor de colores.

        Args:
            provider: Nuevo proveedor de colores.
        """
        self._color_provider = provider

    def set_formatter(self, formatter: LogFormatter) -> None:
        """
        Cambia el formateador de mensajes.

        Args:
            formatter: Nuevo formateador.
        """
        self._formatter = formatter

    def add_log(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        timestamp: datetime | None = None
    ) -> None:
        """
        Agrega un mensaje de log.

        Args:
            message: Mensaje a agregar.
            level: Nivel del log (INFO, WARNING, ERROR, DEBUG).
            timestamp: Momento del log (opcional, usa datetime.now() si no se especifica).
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Formatear mensaje
        formatted_message = self._formatter.format(message, level, timestamp)

        # Obtener color
        color = self._color_provider.get_color(level)

        # Insertar texto con color
        self._append_colored_text(formatted_message, color)

        self._line_count += 1
        self._apply_line_limit()

        if self._auto_scroll:
            self._scroll_to_bottom()

        self.log_added.emit(message, level)

    def _append_colored_text(self, text: str, color: QColor) -> None:
        """Agrega texto con color al área de texto."""
        cursor = self._text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Configurar formato
        char_format = QTextCharFormat()
        char_format.setForeground(color)

        # Insertar con formato
        cursor.insertText(text + "\n", char_format)

    def add_info(self, message: str) -> None:
        """Agrega un log de nivel INFO."""
        self.add_log(message, LogLevel.INFO)

    def add_warning(self, message: str) -> None:
        """Agrega un log de nivel WARNING."""
        self.add_log(message, LogLevel.WARNING)

    def add_error(self, message: str) -> None:
        """Agrega un log de nivel ERROR."""
        self.add_log(message, LogLevel.ERROR)

    def add_debug(self, message: str) -> None:
        """Agrega un log de nivel DEBUG."""
        self.add_log(message, LogLevel.DEBUG)

    def clear_logs(self) -> None:
        """Limpia todos los logs."""
        self._text_area.clear()
        self._line_count = 0
        self.logs_cleared.emit()

    def get_text(self) -> str:
        """
        Retorna todo el texto de los logs.

        Returns:
            Contenido completo del visor de logs.
        """
        return self._text_area.toPlainText()
