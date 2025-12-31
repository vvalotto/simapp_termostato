"""
Proveedor de temas desde archivo.

Implementa ThemeProvider cargando QSS desde archivos
en el sistema de archivos.

Example:
    from compartido.estilos import FileThemeProvider

    provider = FileThemeProvider("dark_theme")
    app.setStyleSheet(provider.get_stylesheet())
"""

from pathlib import Path
from typing import Protocol


class PathResolver(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para resolver rutas de temas.

    Permite inyectar diferentes estrategias de resolución
    de rutas (relativa, absoluta, desde recursos Qt, etc.).
    """

    def resolve(self, theme_name: str) -> Path:
        """
        Resuelve la ruta al archivo de tema.

        Args:
            theme_name: Nombre del tema sin extensión.

        Returns:
            Path al archivo QSS.
        """
        ...  # pylint: disable=unnecessary-ellipsis


class DefaultPathResolver:  # pylint: disable=too-few-public-methods
    """
    Resolvedor de rutas por defecto.

    Busca archivos QSS en el directorio de estilos.
    """

    def __init__(self, base_dir: Path | None = None):
        """
        Inicializa el resolvedor.

        Args:
            base_dir: Directorio base para buscar temas.
                     Por defecto usa el directorio del módulo.
        """
        self._base_dir = base_dir or Path(__file__).parent

    def resolve(self, theme_name: str) -> Path:
        """Resuelve la ruta al archivo de tema."""
        theme_file = self._base_dir / f"{theme_name}.qss"

        if not theme_file.exists():
            raise FileNotFoundError(f"Theme file not found: {theme_file}")

        return theme_file


class FileThemeProvider:  # pylint: disable=too-few-public-methods
    """
    Proveedor de temas desde archivo QSS.

    Carga stylesheets desde archivos en el sistema de
    archivos, útil para temas estáticos o personalizados.

    Cumple con DIP al aceptar un PathResolver inyectable.

    Example:
        # Con resolvedor por defecto
        provider = FileThemeProvider("dark_theme")

        # Con resolvedor personalizado
        resolver = CustomPathResolver("/themes")
        provider = FileThemeProvider("custom", path_resolver=resolver)

        qss = provider.get_stylesheet()
    """

    def __init__(
        self,
        theme_name: str = "dark_theme",
        path_resolver: PathResolver | None = None
    ):
        """
        Inicializa el proveedor.

        Args:
            theme_name: Nombre del tema sin extensión.
            path_resolver: Resolvedor de rutas opcional.
                          Por defecto usa DefaultPathResolver.
        """
        self._theme_name = theme_name
        self._path_resolver = path_resolver or DefaultPathResolver()

    def get_stylesheet(self) -> str:
        """
        Carga y retorna el stylesheet desde archivo.

        Returns:
            Contenido del archivo QSS.

        Raises:
            FileNotFoundError: Si el archivo no existe.
        """
        theme_path = self._path_resolver.resolve(self._theme_name)
        return theme_path.read_text(encoding="utf-8")
