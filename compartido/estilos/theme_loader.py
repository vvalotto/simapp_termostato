"""
Funciones de conveniencia para cargar temas.

Proporciona una API simple para cargar temas,
usando GeneratedThemeProvider por defecto.

Example:
    from compartido.estilos import load_dark_theme

    app.setStyleSheet(load_dark_theme())
"""

from .generated_theme_provider import GeneratedThemeProvider
from .theme_provider import ThemeProvider


def load_dark_theme(provider: ThemeProvider | None = None) -> str:
    """
    Carga el tema oscuro para aplicaciones PyQt6.

    El tema simula la apariencia de un dispositivo embebido
    con colores oscuros y acentos cyan estilo LCD.

    Cumple con DIP: acepta un ThemeProvider opcional,
    permitiendo inyectar diferentes estrategias de carga.

    Args:
        provider: Proveedor de temas opcional.
                 Por defecto usa GeneratedThemeProvider.

    Returns:
        Contenido QSS como string, listo para aplicar
        con QApplication.setStyleSheet().

    Example:
        # Uso simple (genera desde DarkThemeColors)
        app.setStyleSheet(load_dark_theme())

        # Con proveedor desde archivo
        from compartido.estilos import FileThemeProvider
        provider = FileThemeProvider("dark_theme")
        app.setStyleSheet(load_dark_theme(provider))

        # Con proveedor personalizado
        class CustomProvider:
            def get_stylesheet(self) -> str:
                return "QWidget { background: black; }"

        app.setStyleSheet(load_dark_theme(CustomProvider()))
    """
    theme_provider = provider or GeneratedThemeProvider()
    return theme_provider.get_stylesheet()
