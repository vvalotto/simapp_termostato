"""Tests para el módulo de estilos dark_theme."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from compartido.estilos import (
    ColorPalette,
    DarkThemeColors,
    DefaultPathResolver,
    FileThemeProvider,
    GeneratedThemeProvider,
    QSSGenerator,
    ThemeProvider,
    generate_dark_theme_qss,
    load_dark_theme,
)


# ============================================
# Tests para DarkThemeColors
# ============================================

class TestDarkThemeColors:
    """Tests para las constantes de colores."""

    def test_background_colors_are_hex(self):
        """Los colores de fondo son valores hexadecimales válidos."""
        assert DarkThemeColors.BACKGROUND_PRIMARY.startswith("#")
        assert len(DarkThemeColors.BACKGROUND_PRIMARY) == 7

    def test_background_primary_is_dark(self):
        """El fondo primario es un color oscuro."""
        assert DarkThemeColors.BACKGROUND_PRIMARY == "#1e1e1e"

    def test_text_primary_is_light(self):
        """El texto primario es un color claro."""
        assert DarkThemeColors.TEXT_PRIMARY == "#e0e0e0"

    def test_accent_primary_is_cyan(self):
        """El acento primario es cyan (estilo LCD)."""
        assert DarkThemeColors.ACCENT_PRIMARY == "#00aaff"

    def test_error_color_is_red(self):
        """El color de error es rojo."""
        assert DarkThemeColors.ERROR == "#ff6b6b"

    def test_warning_color_is_yellow(self):
        """El color de advertencia es amarillo."""
        assert DarkThemeColors.WARNING == "#ffcc00"

    def test_success_color_is_green(self):
        """El color de éxito es verde."""
        assert DarkThemeColors.SUCCESS == "#4caf50"

    def test_all_colors_are_strings(self):
        """Todos los atributos de color son strings."""
        color_attrs = [
            attr for attr in dir(DarkThemeColors)
            if not attr.startswith("_")
        ]
        for attr in color_attrs:
            value = getattr(DarkThemeColors, attr)
            assert isinstance(value, str), f"{attr} should be string"

    def test_all_colors_are_valid_hex(self):
        """Todos los colores son valores hex válidos."""
        color_attrs = [
            attr for attr in dir(DarkThemeColors)
            if not attr.startswith("_")
        ]
        for attr in color_attrs:
            value = getattr(DarkThemeColors, attr)
            assert value.startswith("#"), f"{attr} should start with #"
            assert len(value) == 7, f"{attr} should be 7 chars (#RRGGBB)"
            try:
                int(value[1:], 16)
            except ValueError:
                pytest.fail(f"{attr} is not valid hex: {value}")


# ============================================
# Tests para QSSGenerator
# ============================================

class TestQSSGenerator:
    """Tests para el generador de QSS."""

    def test_generate_returns_string(self):
        """generate() retorna string."""
        generator = QSSGenerator()
        result = generator.generate()
        assert isinstance(result, str)

    def test_generate_not_empty(self):
        """El QSS generado no está vacío."""
        generator = QSSGenerator()
        result = generator.generate()
        assert len(result) > 0

    def test_uses_default_palette(self):
        """Usa DarkThemeColors por defecto."""
        generator = QSSGenerator()
        result = generator.generate()
        assert DarkThemeColors.BACKGROUND_PRIMARY in result
        assert DarkThemeColors.ACCENT_PRIMARY in result

    def test_accepts_custom_palette(self):
        """Acepta una paleta personalizada."""
        class CustomPalette:
            BACKGROUND_PRIMARY = "#000000"
            BACKGROUND_SECONDARY = "#111111"
            BACKGROUND_TERTIARY = "#222222"
            BACKGROUND_ELEVATED = "#333333"
            TEXT_PRIMARY = "#ffffff"
            TEXT_SECONDARY = "#cccccc"
            TEXT_DISABLED = "#666666"
            ACCENT_PRIMARY = "#ff0000"
            ACCENT_HOVER = "#ff3333"
            ACCENT_PRESSED = "#cc0000"
            BORDER_DEFAULT = "#444444"
            BORDER_HOVER = "#555555"
            BORDER_FOCUS = "#ff0000"
            ERROR = "#ff0000"
            WARNING = "#ffff00"
            SUCCESS = "#00ff00"
            SELECTION_BACKGROUND = "#ff0000"
            SELECTION_TEXT = "#000000"

        generator = QSSGenerator(CustomPalette)
        result = generator.generate()
        assert "#000000" in result  # CustomPalette.BACKGROUND_PRIMARY
        assert "#ff0000" in result  # CustomPalette.ACCENT_PRIMARY

    def test_contains_all_widget_styles(self):
        """Contiene estilos para todos los widgets requeridos."""
        generator = QSSGenerator()
        result = generator.generate()

        required_widgets = [
            "QMainWindow", "QWidget", "QLabel", "QPushButton",
            "QLineEdit", "QSpinBox", "QComboBox", "QSlider",
            "QProgressBar", "QGroupBox", "QFrame"
        ]
        for widget in required_widgets:
            assert widget in result, f"Missing style for {widget}"

    def test_balanced_braces(self):
        """Las llaves están balanceadas."""
        generator = QSSGenerator()
        result = generator.generate()
        open_count = result.count("{")
        close_count = result.count("}")
        assert open_count == close_count


class TestGenerateDarkThemeQss:
    """Tests para la función generate_dark_theme_qss()."""

    def test_returns_string(self):
        """Retorna string."""
        result = generate_dark_theme_qss()
        assert isinstance(result, str)

    def test_same_as_generator(self):
        """Retorna lo mismo que QSSGenerator."""
        function_result = generate_dark_theme_qss()
        generator_result = QSSGenerator().generate()
        assert function_result == generator_result

    def test_accepts_custom_palette(self):
        """Acepta paleta personalizada."""
        result = generate_dark_theme_qss(DarkThemeColors)
        assert DarkThemeColors.ACCENT_PRIMARY in result


# ============================================
# Tests para GeneratedThemeProvider
# ============================================

class TestGeneratedThemeProvider:
    """Tests para GeneratedThemeProvider."""

    def test_implements_theme_provider_protocol(self):
        """Implementa el protocolo ThemeProvider."""
        provider = GeneratedThemeProvider()
        assert hasattr(provider, "get_stylesheet")
        assert callable(provider.get_stylesheet)

    def test_get_stylesheet_returns_string(self):
        """get_stylesheet() retorna string."""
        provider = GeneratedThemeProvider()
        result = provider.get_stylesheet()
        assert isinstance(result, str)

    def test_uses_default_palette(self):
        """Usa DarkThemeColors por defecto."""
        provider = GeneratedThemeProvider()
        result = provider.get_stylesheet()
        assert DarkThemeColors.ACCENT_PRIMARY in result

    def test_accepts_custom_palette(self):
        """Acepta paleta personalizada."""
        class CustomPalette:
            BACKGROUND_PRIMARY = "#123456"
            BACKGROUND_SECONDARY = "#234567"
            BACKGROUND_TERTIARY = "#345678"
            BACKGROUND_ELEVATED = "#456789"
            TEXT_PRIMARY = "#ffffff"
            TEXT_SECONDARY = "#eeeeee"
            TEXT_DISABLED = "#aaaaaa"
            ACCENT_PRIMARY = "#abcdef"
            ACCENT_HOVER = "#bcdef0"
            ACCENT_PRESSED = "#9abcde"
            BORDER_DEFAULT = "#567890"
            BORDER_HOVER = "#678901"
            BORDER_FOCUS = "#abcdef"
            ERROR = "#ff0000"
            WARNING = "#ffff00"
            SUCCESS = "#00ff00"
            SELECTION_BACKGROUND = "#abcdef"
            SELECTION_TEXT = "#123456"

        provider = GeneratedThemeProvider(CustomPalette)
        result = provider.get_stylesheet()
        assert "#123456" in result
        assert "#abcdef" in result


# ============================================
# Tests para DefaultPathResolver
# ============================================

class TestDefaultPathResolver:
    """Tests para DefaultPathResolver."""

    def test_resolve_returns_path(self):
        """resolve() retorna Path."""
        resolver = DefaultPathResolver()
        result = resolver.resolve("dark_theme")
        assert isinstance(result, Path)

    def test_resolve_finds_existing_theme(self):
        """Encuentra temas existentes."""
        resolver = DefaultPathResolver()
        result = resolver.resolve("dark_theme")
        assert result.exists()

    def test_resolve_raises_for_missing_theme(self):
        """Lanza error para temas inexistentes."""
        resolver = DefaultPathResolver()
        with pytest.raises(FileNotFoundError):
            resolver.resolve("nonexistent_theme")

    def test_accepts_custom_base_dir(self):
        """Acepta directorio base personalizado."""
        custom_dir = Path("/tmp")
        resolver = DefaultPathResolver(custom_dir)
        # Debería buscar en /tmp, no en el directorio de estilos
        with pytest.raises(FileNotFoundError):
            resolver.resolve("dark_theme")


# ============================================
# Tests para FileThemeProvider
# ============================================

class TestFileThemeProvider:
    """Tests para FileThemeProvider."""

    def test_implements_theme_provider_protocol(self):
        """Implementa el protocolo ThemeProvider."""
        provider = FileThemeProvider()
        assert hasattr(provider, "get_stylesheet")
        assert callable(provider.get_stylesheet)

    def test_get_stylesheet_returns_string(self):
        """get_stylesheet() retorna string."""
        provider = FileThemeProvider()
        result = provider.get_stylesheet()
        assert isinstance(result, str)

    def test_loads_dark_theme_by_default(self):
        """Carga dark_theme por defecto."""
        provider = FileThemeProvider()
        result = provider.get_stylesheet()
        assert len(result) > 0
        assert "QWidget" in result

    def test_accepts_custom_theme_name(self):
        """Acepta nombre de tema personalizado."""
        provider = FileThemeProvider("dark_theme")
        result = provider.get_stylesheet()
        assert len(result) > 0

    def test_raises_for_missing_theme(self):
        """Lanza error para temas inexistentes."""
        provider = FileThemeProvider("nonexistent")
        with pytest.raises(FileNotFoundError):
            provider.get_stylesheet()

    def test_accepts_custom_path_resolver(self):
        """Acepta PathResolver personalizado (DIP)."""
        mock_resolver = Mock()
        mock_path = Mock()
        mock_path.read_text.return_value = "QWidget { color: red; }"
        mock_resolver.resolve.return_value = mock_path

        provider = FileThemeProvider("custom", path_resolver=mock_resolver)
        result = provider.get_stylesheet()

        mock_resolver.resolve.assert_called_once_with("custom")
        assert result == "QWidget { color: red; }"


# ============================================
# Tests para load_dark_theme()
# ============================================

class TestLoadDarkTheme:
    """Tests para load_dark_theme()."""

    def test_returns_string(self):
        """Retorna string."""
        result = load_dark_theme()
        assert isinstance(result, str)

    def test_not_empty(self):
        """El resultado no está vacío."""
        result = load_dark_theme()
        assert len(result) > 0

    def test_uses_generated_provider_by_default(self):
        """Usa GeneratedThemeProvider por defecto."""
        result = load_dark_theme()
        # El generado contiene colores de DarkThemeColors
        assert DarkThemeColors.ACCENT_PRIMARY in result

    def test_accepts_custom_provider(self):
        """Acepta ThemeProvider personalizado (DIP)."""
        mock_provider = Mock()
        mock_provider.get_stylesheet.return_value = "custom stylesheet"

        result = load_dark_theme(mock_provider)

        mock_provider.get_stylesheet.assert_called_once()
        assert result == "custom stylesheet"

    def test_accepts_file_provider(self):
        """Acepta FileThemeProvider."""
        provider = FileThemeProvider("dark_theme")
        result = load_dark_theme(provider)
        assert len(result) > 0
        assert "QWidget" in result

    def test_accepts_generated_provider(self):
        """Acepta GeneratedThemeProvider."""
        provider = GeneratedThemeProvider()
        result = load_dark_theme(provider)
        assert DarkThemeColors.ACCENT_PRIMARY in result


# ============================================
# Tests para validez del QSS
# ============================================

class TestThemeQSSValidity:
    """Tests para validar la estructura del QSS."""

    def test_generated_has_balanced_braces(self):
        """El QSS generado tiene llaves balanceadas."""
        result = load_dark_theme()
        open_count = result.count("{")
        close_count = result.count("}")
        assert open_count == close_count

    def test_file_has_balanced_braces(self):
        """El QSS de archivo tiene llaves balanceadas."""
        provider = FileThemeProvider()
        result = provider.get_stylesheet()
        open_count = result.count("{")
        close_count = result.count("}")
        assert open_count == close_count

    def test_contains_hover_states(self):
        """Contiene estados :hover."""
        result = load_dark_theme()
        assert ":hover" in result

    def test_contains_disabled_states(self):
        """Contiene estados :disabled."""
        result = load_dark_theme()
        assert ":disabled" in result

    def test_contains_focus_states(self):
        """Contiene estados :focus."""
        result = load_dark_theme()
        assert ":focus" in result

    def test_contains_pressed_states(self):
        """Contiene estados :pressed."""
        result = load_dark_theme()
        assert ":pressed" in result


# ============================================
# Tests de integración con PyQt6
# ============================================

class TestThemeIntegration:
    """Tests de integración con PyQt6."""

    def test_can_import_qcolor(self):
        """Se puede usar QColor con los colores del tema."""
        from PyQt6.QtGui import QColor  # pylint: disable=import-outside-toplevel
        color = QColor(DarkThemeColors.ACCENT_PRIMARY)
        assert color.isValid()

    def test_accent_color_rgb_values(self):
        """El color de acento tiene los valores RGB correctos."""
        from PyQt6.QtGui import QColor  # pylint: disable=import-outside-toplevel
        color = QColor(DarkThemeColors.ACCENT_PRIMARY)
        # #00aaff = RGB(0, 170, 255)
        assert color.red() == 0
        assert color.green() == 170
        assert color.blue() == 255

    def test_background_color_rgb_values(self):
        """El fondo primario tiene los valores RGB correctos."""
        from PyQt6.QtGui import QColor  # pylint: disable=import-outside-toplevel
        color = QColor(DarkThemeColors.BACKGROUND_PRIMARY)
        # #1e1e1e = RGB(30, 30, 30)
        assert color.red() == 30
        assert color.green() == 30
        assert color.blue() == 30


# ============================================
# Tests de SOLID compliance
# ============================================

class TestSOLIDCompliance:
    """Tests que verifican cumplimiento de principios SOLID."""

    def test_dip_load_dark_theme_accepts_abstraction(self):
        """load_dark_theme acepta ThemeProvider (DIP)."""
        # Cualquier objeto con get_stylesheet() funciona
        class MinimalProvider:
            def get_stylesheet(self) -> str:
                return "minimal"

        result = load_dark_theme(MinimalProvider())
        assert result == "minimal"

    def test_dip_file_provider_accepts_path_resolver(self):
        """FileThemeProvider acepta PathResolver (DIP)."""
        class MockResolver:
            def resolve(self, theme_name: str) -> Path:
                # Retorna el archivo real para testing
                return Path(__file__).parent.parent / "estilos" / "dark_theme.qss"

        provider = FileThemeProvider("any", path_resolver=MockResolver())
        result = provider.get_stylesheet()
        assert len(result) > 0

    def test_ocp_new_palette_without_modification(self):
        """Se puede crear nueva paleta sin modificar código (OCP)."""
        class BluePalette:
            BACKGROUND_PRIMARY = "#000033"
            BACKGROUND_SECONDARY = "#000066"
            BACKGROUND_TERTIARY = "#000099"
            BACKGROUND_ELEVATED = "#0000cc"
            TEXT_PRIMARY = "#ffffff"
            TEXT_SECONDARY = "#cccccc"
            TEXT_DISABLED = "#666666"
            ACCENT_PRIMARY = "#0066ff"
            ACCENT_HOVER = "#3399ff"
            ACCENT_PRESSED = "#0044cc"
            BORDER_DEFAULT = "#003399"
            BORDER_HOVER = "#0055bb"
            BORDER_FOCUS = "#0066ff"
            ERROR = "#ff0000"
            WARNING = "#ffff00"
            SUCCESS = "#00ff00"
            SELECTION_BACKGROUND = "#0066ff"
            SELECTION_TEXT = "#ffffff"

        provider = GeneratedThemeProvider(BluePalette)
        result = provider.get_stylesheet()
        assert "#000033" in result
        assert "#0066ff" in result

    def test_lsp_providers_are_substitutable(self):
        """Ambos providers son sustituibles (LSP)."""
        providers = [
            GeneratedThemeProvider(),
            FileThemeProvider(),
        ]

        for provider in providers:
            result = provider.get_stylesheet()
            assert isinstance(result, str)
            assert len(result) > 0
            assert "QWidget" in result
