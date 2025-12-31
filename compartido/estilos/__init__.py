"""
Módulo de estilos para ISSE_Simuladores.

Proporciona temas visuales para las aplicaciones PyQt6,
simulando la apariencia de dispositivos embebidos.

Arquitectura:
    - ThemeProvider: Protocolo abstracto para proveedores
    - GeneratedThemeProvider: Genera QSS desde DarkThemeColors
    - FileThemeProvider: Carga QSS desde archivo
    - QSSGenerator: Genera QSS desde cualquier paleta de colores

Uso básico:
    from compartido.estilos import load_dark_theme
    app.setStyleSheet(load_dark_theme())

Uso con proveedor específico:
    from compartido.estilos import FileThemeProvider, load_dark_theme
    provider = FileThemeProvider("dark_theme")
    app.setStyleSheet(load_dark_theme(provider))

Uso con colores en código:
    from compartido.estilos import DarkThemeColors
    color = DarkThemeColors.ACCENT_PRIMARY  # "#00aaff"
"""

from .theme_colors import DarkThemeColors
from .theme_provider import ThemeProvider
from .generated_theme_provider import GeneratedThemeProvider
from .file_theme_provider import FileThemeProvider, DefaultPathResolver, PathResolver
from .qss_generator import QSSGenerator, ColorPalette, generate_dark_theme_qss
from .theme_loader import load_dark_theme

__all__ = [
    # Función principal
    "load_dark_theme",
    # Protocolo abstracto
    "ThemeProvider",
    # Proveedores concretos
    "GeneratedThemeProvider",
    "FileThemeProvider",
    # Generador de QSS
    "QSSGenerator",
    "generate_dark_theme_qss",
    # Paletas de colores
    "DarkThemeColors",
    "ColorPalette",
    # Resolución de rutas
    "PathResolver",
    "DefaultPathResolver",
]
