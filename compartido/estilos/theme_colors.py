"""
Constantes de colores para el tema oscuro.

Proporciona acceso programático a los colores del tema
para uso en widgets personalizados o código Python.

Example:
    from compartido.estilos import DarkThemeColors

    # Usar en código
    background = DarkThemeColors.BACKGROUND_PRIMARY
    accent = DarkThemeColors.ACCENT_PRIMARY

    # Obtener QColor
    from PyQt6.QtGui import QColor
    q_color = QColor(DarkThemeColors.ACCENT_PRIMARY)
"""


class DarkThemeColors:  # pylint: disable=too-few-public-methods
    """
    Paleta de colores del tema oscuro.

    Diseñada para simular displays de dispositivos embebidos
    con un estilo LCD/OLED moderno.
    """

    # Backgrounds
    BACKGROUND_PRIMARY = "#1e1e1e"
    BACKGROUND_SECONDARY = "#2d2d2d"
    BACKGROUND_TERTIARY = "#383838"
    BACKGROUND_ELEVATED = "#252525"

    # Text
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_DISABLED = "#606060"

    # Accent (Cyan - LCD style)
    ACCENT_PRIMARY = "#00aaff"
    ACCENT_HOVER = "#33bbff"
    ACCENT_PRESSED = "#0088cc"

    # Borders
    BORDER_DEFAULT = "#404040"
    BORDER_HOVER = "#505050"
    BORDER_FOCUS = "#00aaff"

    # Semantic colors
    ERROR = "#ff6b6b"
    ERROR_LIGHT = "#ff8a8a"
    WARNING = "#ffcc00"
    SUCCESS = "#4caf50"

    # Special
    SELECTION_BACKGROUND = "#00aaff"
    SELECTION_TEXT = "#1e1e1e"
