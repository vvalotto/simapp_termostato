"""
Protocolo para proveedores de temas.

Define la interfaz abstracta que deben implementar
todos los proveedores de temas QSS.

Example:
    class CustomThemeProvider:
        def get_stylesheet(self) -> str:
            return "QWidget { background: black; }"

    provider: ThemeProvider = CustomThemeProvider()
    app.setStyleSheet(provider.get_stylesheet())
"""

from typing import Protocol


class ThemeProvider(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para proveedores de temas QSS.

    Permite implementar diferentes estrategias de provisión
    de temas: desde archivo, generado dinámicamente,
    desde recursos Qt, base de datos, etc.

    Cumple con DIP: los consumidores dependen de esta
    abstracción, no de implementaciones concretas.
    """

    def get_stylesheet(self) -> str:
        """
        Obtiene el stylesheet QSS completo.

        Returns:
            Contenido QSS como string, listo para aplicar
            con QApplication.setStyleSheet() o widget.setStyleSheet().
        """
        ...  # pylint: disable=unnecessary-ellipsis
