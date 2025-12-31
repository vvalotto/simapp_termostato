"""
Proveedor de temas generados dinámicamente.

Implementa ThemeProvider generando QSS desde constantes
de colores Python, eliminando duplicación.

Example:
    from compartido.estilos import GeneratedThemeProvider

    provider = GeneratedThemeProvider()
    app.setStyleSheet(provider.get_stylesheet())
"""

from .qss_generator import ColorPalette, QSSGenerator
from .theme_colors import DarkThemeColors


class GeneratedThemeProvider:  # pylint: disable=too-few-public-methods
    """
    Proveedor de temas que genera QSS dinámicamente.

    Usa QSSGenerator para crear el stylesheet desde
    una paleta de colores, cumpliendo con DIP al
    depender de la abstracción ColorPalette.

    Example:
        # Con paleta por defecto
        provider = GeneratedThemeProvider()

        # Con paleta personalizada
        provider = GeneratedThemeProvider(CustomPalette)

        qss = provider.get_stylesheet()
    """

    def __init__(self, palette: type[ColorPalette] | None = None):
        """
        Inicializa el proveedor.

        Args:
            palette: Clase con constantes de colores.
                    Por defecto usa DarkThemeColors.
        """
        self._generator = QSSGenerator(palette or DarkThemeColors)

    def get_stylesheet(self) -> str:
        """
        Genera y retorna el stylesheet QSS.

        Returns:
            Stylesheet QSS completo generado desde la paleta.
        """
        return self._generator.generate()
