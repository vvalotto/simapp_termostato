"""
Generador de QSS desde constantes de colores.

Genera stylesheets QSS dinámicamente usando las constantes
definidas en theme_colors.py, eliminando duplicación.

Example:
    from compartido.estilos.qss_generator import generate_dark_theme_qss

    qss = generate_dark_theme_qss()
    app.setStyleSheet(qss)
"""

from typing import Protocol

from .theme_colors import DarkThemeColors


class ColorPalette(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para paletas de colores.

    Define los colores mínimos necesarios para generar un tema.
    Permite inyectar diferentes paletas al generador.
    """

    BACKGROUND_PRIMARY: str
    BACKGROUND_SECONDARY: str
    BACKGROUND_TERTIARY: str
    BACKGROUND_ELEVATED: str
    TEXT_PRIMARY: str
    TEXT_SECONDARY: str
    TEXT_DISABLED: str
    ACCENT_PRIMARY: str
    ACCENT_HOVER: str
    ACCENT_PRESSED: str
    BORDER_DEFAULT: str
    BORDER_HOVER: str
    BORDER_FOCUS: str
    ERROR: str
    WARNING: str
    SUCCESS: str
    SELECTION_BACKGROUND: str
    SELECTION_TEXT: str


class QSSGenerator:  # pylint: disable=too-few-public-methods
    """
    Generador de stylesheets QSS.

    Genera QSS dinámicamente desde una paleta de colores,
    eliminando la duplicación entre código Python y archivos QSS.

    Example:
        generator = QSSGenerator(DarkThemeColors)
        qss = generator.generate()
    """

    def __init__(self, palette: type[ColorPalette] | None = None):
        """
        Inicializa el generador.

        Args:
            palette: Clase con constantes de colores.
                    Por defecto usa DarkThemeColors.
        """
        self._palette = palette or DarkThemeColors

    def generate(self) -> str:
        """
        Genera el stylesheet QSS completo.

        Returns:
            String con todo el QSS listo para aplicar.
        """
        p = self._palette
        return f'''/*
 * Dark Theme - Generated from DarkThemeColors
 * Simulates embedded device display appearance
 */

/* ============================================
   BASE WIDGETS
   ============================================ */

QMainWindow {{
    background-color: {p.BACKGROUND_PRIMARY};
    color: {p.TEXT_PRIMARY};
}}

QWidget {{
    background-color: {p.BACKGROUND_PRIMARY};
    color: {p.TEXT_PRIMARY};
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 12px;
}}

QWidget:disabled {{
    color: {p.TEXT_DISABLED};
}}

/* ============================================
   LABELS
   ============================================ */

QLabel {{
    background-color: transparent;
    color: {p.TEXT_PRIMARY};
    padding: 2px;
}}

QLabel:disabled {{
    color: {p.TEXT_DISABLED};
}}

/* ============================================
   BUTTONS
   ============================================ */

QPushButton {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    padding: 6px 16px;
    min-height: 24px;
}}

QPushButton:hover {{
    background-color: {p.BACKGROUND_TERTIARY};
    border-color: {p.ACCENT_PRIMARY};
}}

QPushButton:pressed {{
    background-color: {p.ACCENT_PRESSED};
    border-color: {p.ACCENT_PRIMARY};
}}

QPushButton:disabled {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_DISABLED};
    border-color: {p.BACKGROUND_TERTIARY};
}}

QPushButton:focus {{
    border-color: {p.ACCENT_PRIMARY};
    outline: none;
}}

QPushButton[primary="true"] {{
    background-color: {p.ACCENT_PRIMARY};
    color: {p.BACKGROUND_PRIMARY};
    border-color: {p.ACCENT_PRIMARY};
    font-weight: bold;
}}

QPushButton[primary="true"]:hover {{
    background-color: {p.ACCENT_HOVER};
    border-color: {p.ACCENT_HOVER};
}}

QPushButton[primary="true"]:pressed {{
    background-color: {p.ACCENT_PRESSED};
    border-color: {p.ACCENT_PRESSED};
}}

QPushButton[danger="true"] {{
    background-color: {p.ERROR};
    color: {p.BACKGROUND_PRIMARY};
    border-color: {p.ERROR};
}}

/* ============================================
   TEXT INPUTS
   ============================================ */

QLineEdit {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    padding: 6px 8px;
    selection-background-color: {p.SELECTION_BACKGROUND};
    selection-color: {p.SELECTION_TEXT};
}}

QLineEdit:hover {{
    border-color: {p.BORDER_HOVER};
}}

QLineEdit:focus {{
    border-color: {p.BORDER_FOCUS};
    background-color: {p.BACKGROUND_TERTIARY};
}}

QLineEdit:disabled {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_DISABLED};
    border-color: {p.BACKGROUND_TERTIARY};
}}

QLineEdit:read-only {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_SECONDARY};
}}

QLineEdit[valid="false"] {{
    border-color: {p.ERROR};
}}

QLineEdit[valid="true"] {{
    border-color: {p.SUCCESS};
}}

/* ============================================
   SPIN BOXES
   ============================================ */

QSpinBox, QDoubleSpinBox {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    padding: 4px 8px;
    padding-right: 20px;
}}

QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: {p.BORDER_HOVER};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {p.BORDER_FOCUS};
    background-color: {p.BACKGROUND_TERTIARY};
}}

QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_DISABLED};
    border-color: {p.BACKGROUND_TERTIARY};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid {p.BORDER_DEFAULT};
    border-bottom: 1px solid {p.BORDER_DEFAULT};
    border-top-right-radius: 3px;
    background-color: {p.BACKGROUND_TERTIARY};
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {p.ACCENT_PRIMARY};
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    width: 8px;
    height: 8px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid {p.TEXT_PRIMARY};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid {p.BORDER_DEFAULT};
    border-bottom-right-radius: 3px;
    background-color: {p.BACKGROUND_TERTIARY};
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {p.ACCENT_PRIMARY};
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    width: 8px;
    height: 8px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid {p.TEXT_PRIMARY};
}}

/* ============================================
   COMBO BOXES
   ============================================ */

QComboBox {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    padding: 6px 8px;
    padding-right: 24px;
    min-width: 80px;
}}

QComboBox:hover {{
    border-color: {p.BORDER_HOVER};
}}

QComboBox:focus {{
    border-color: {p.BORDER_FOCUS};
}}

QComboBox:disabled {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_DISABLED};
    border-color: {p.BACKGROUND_TERTIARY};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {p.BORDER_DEFAULT};
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    background-color: {p.BACKGROUND_TERTIARY};
}}

QComboBox::drop-down:hover {{
    background-color: {p.ACCENT_PRIMARY};
}}

QComboBox::down-arrow {{
    width: 8px;
    height: 8px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid {p.TEXT_PRIMARY};
}}

QComboBox QAbstractItemView {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    selection-background-color: {p.SELECTION_BACKGROUND};
    selection-color: {p.SELECTION_TEXT};
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 6px 8px;
    min-height: 24px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {p.BACKGROUND_TERTIARY};
}}

/* ============================================
   SLIDERS
   ============================================ */

QSlider::groove:horizontal {{
    border: 1px solid {p.BORDER_DEFAULT};
    height: 6px;
    background-color: {p.BACKGROUND_SECONDARY};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background-color: {p.ACCENT_PRIMARY};
    border: 1px solid {p.ACCENT_PRESSED};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {p.ACCENT_HOVER};
    border-color: {p.ACCENT_PRIMARY};
}}

QSlider::handle:horizontal:pressed {{
    background-color: {p.ACCENT_PRESSED};
}}

QSlider::handle:horizontal:disabled {{
    background-color: {p.TEXT_DISABLED};
    border-color: {p.BORDER_HOVER};
}}

QSlider::sub-page:horizontal {{
    background-color: {p.ACCENT_PRIMARY};
    border-radius: 3px;
}}

QSlider::add-page:horizontal {{
    background-color: {p.BACKGROUND_SECONDARY};
    border-radius: 3px;
}}

QSlider::groove:vertical {{
    border: 1px solid {p.BORDER_DEFAULT};
    width: 6px;
    background-color: {p.BACKGROUND_SECONDARY};
    border-radius: 3px;
}}

QSlider::handle:vertical {{
    background-color: {p.ACCENT_PRIMARY};
    border: 1px solid {p.ACCENT_PRESSED};
    width: 16px;
    height: 16px;
    margin: 0 -6px;
    border-radius: 8px;
}}

QSlider::handle:vertical:hover {{
    background-color: {p.ACCENT_HOVER};
}}

/* ============================================
   PROGRESS BARS
   ============================================ */

QProgressBar {{
    background-color: {p.BACKGROUND_SECONDARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    text-align: center;
    color: {p.TEXT_PRIMARY};
    min-height: 20px;
}}

QProgressBar::chunk {{
    background-color: {p.ACCENT_PRIMARY};
    border-radius: 3px;
}}

QProgressBar[level="warning"]::chunk {{
    background-color: {p.WARNING};
}}

QProgressBar[level="critical"]::chunk {{
    background-color: {p.ERROR};
}}

/* ============================================
   GROUP BOXES
   ============================================ */

QGroupBox {{
    background-color: {p.BACKGROUND_ELEVATED};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 6px;
    margin-top: 12px;
    padding: 12px 8px 8px 8px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.ACCENT_PRIMARY};
}}

/* ============================================
   FRAMES
   ============================================ */

QFrame {{
    background-color: transparent;
    border: none;
}}

QFrame[frameShape="4"] {{
    background-color: {p.BORDER_DEFAULT};
    max-height: 1px;
    min-height: 1px;
}}

QFrame[frameShape="5"] {{
    background-color: {p.BORDER_DEFAULT};
    max-width: 1px;
    min-width: 1px;
}}

QFrame[frameShape="1"] {{
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
}}

QFrame[frameShape="6"] {{
    background-color: {p.BACKGROUND_ELEVATED};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 6px;
}}

/* ============================================
   SCROLL BARS
   ============================================ */

QScrollBar:vertical {{
    background-color: {p.BACKGROUND_PRIMARY};
    width: 12px;
    border: none;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {p.BORDER_DEFAULT};
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {p.BORDER_HOVER};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {p.ACCENT_PRIMARY};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {p.BACKGROUND_PRIMARY};
    height: 12px;
    border: none;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {p.BORDER_DEFAULT};
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {p.BORDER_HOVER};
}}

QScrollBar::handle:horizontal:pressed {{
    background-color: {p.ACCENT_PRIMARY};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

/* ============================================
   TEXT EDIT / PLAIN TEXT EDIT
   ============================================ */

QTextEdit, QPlainTextEdit {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    selection-background-color: {p.SELECTION_BACKGROUND};
    selection-color: {p.SELECTION_TEXT};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {p.BORDER_FOCUS};
}}

/* ============================================
   TAB WIDGET
   ============================================ */

QTabWidget::pane {{
    background-color: {p.BACKGROUND_ELEVATED};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_SECONDARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.ACCENT_PRIMARY};
    border-bottom: 2px solid {p.ACCENT_PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background-color: {p.BACKGROUND_TERTIARY};
    color: {p.TEXT_PRIMARY};
}}

/* ============================================
   TOOL TIP
   ============================================ */

QToolTip {{
    background-color: {p.BACKGROUND_TERTIARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_HOVER};
    border-radius: 4px;
    padding: 4px 8px;
}}

/* ============================================
   MENU BAR
   ============================================ */

QMenuBar {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_PRIMARY};
    border-bottom: 1px solid {p.BORDER_DEFAULT};
    padding: 2px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {p.BACKGROUND_TERTIARY};
}}

QMenuBar::item:pressed {{
    background-color: {p.ACCENT_PRIMARY};
    color: {p.BACKGROUND_PRIMARY};
}}

/* ============================================
   MENU
   ============================================ */

QMenu {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {p.ACCENT_PRIMARY};
    color: {p.BACKGROUND_PRIMARY};
}}

QMenu::item:disabled {{
    color: {p.TEXT_DISABLED};
}}

QMenu::separator {{
    height: 1px;
    background-color: {p.BORDER_DEFAULT};
    margin: 4px 8px;
}}

/* ============================================
   STATUS BAR
   ============================================ */

QStatusBar {{
    background-color: {p.BACKGROUND_ELEVATED};
    color: {p.TEXT_SECONDARY};
    border-top: 1px solid {p.BORDER_DEFAULT};
}}

QStatusBar::item {{
    border: none;
}}

/* ============================================
   CHECK BOX
   ============================================ */

QCheckBox {{
    color: {p.TEXT_PRIMARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 3px;
    background-color: {p.BACKGROUND_SECONDARY};
}}

QCheckBox::indicator:hover {{
    border-color: {p.ACCENT_PRIMARY};
}}

QCheckBox::indicator:checked {{
    background-color: {p.ACCENT_PRIMARY};
    border-color: {p.ACCENT_PRIMARY};
}}

QCheckBox::indicator:checked:hover {{
    background-color: {p.ACCENT_HOVER};
}}

QCheckBox::indicator:disabled {{
    background-color: {p.BACKGROUND_ELEVATED};
    border-color: {p.BACKGROUND_TERTIARY};
}}

/* ============================================
   RADIO BUTTON
   ============================================ */

QRadioButton {{
    color: {p.TEXT_PRIMARY};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 9px;
    background-color: {p.BACKGROUND_SECONDARY};
}}

QRadioButton::indicator:hover {{
    border-color: {p.ACCENT_PRIMARY};
}}

QRadioButton::indicator:checked {{
    background-color: {p.ACCENT_PRIMARY};
    border-color: {p.ACCENT_PRIMARY};
}}

QRadioButton::indicator:disabled {{
    background-color: {p.BACKGROUND_ELEVATED};
    border-color: {p.BACKGROUND_TERTIARY};
}}

/* ============================================
   LIST VIEW / LIST WIDGET
   ============================================ */

QListView, QListWidget {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    outline: none;
}}

QListView::item, QListWidget::item {{
    padding: 6px 8px;
    border-radius: 2px;
}}

QListView::item:hover, QListWidget::item:hover {{
    background-color: {p.BACKGROUND_TERTIARY};
}}

QListView::item:selected, QListWidget::item:selected {{
    background-color: {p.SELECTION_BACKGROUND};
    color: {p.SELECTION_TEXT};
}}

/* ============================================
   TABLE VIEW / TABLE WIDGET
   ============================================ */

QTableView, QTableWidget {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
    border: 1px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
    gridline-color: {p.BORDER_DEFAULT};
    selection-background-color: {p.SELECTION_BACKGROUND};
    selection-color: {p.SELECTION_TEXT};
}}

QTableView::item, QTableWidget::item {{
    padding: 4px 8px;
}}

QHeaderView::section {{
    background-color: {p.BACKGROUND_TERTIARY};
    color: {p.TEXT_PRIMARY};
    border: none;
    border-right: 1px solid {p.BORDER_DEFAULT};
    border-bottom: 1px solid {p.BORDER_DEFAULT};
    padding: 6px 8px;
    font-weight: bold;
}}

QHeaderView::section:hover {{
    background-color: {p.BORDER_DEFAULT};
}}

/* ============================================
   SPLITTER
   ============================================ */

QSplitter::handle {{
    background-color: {p.BORDER_DEFAULT};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {p.ACCENT_PRIMARY};
}}

/* ============================================
   DOCK WIDGET
   ============================================ */

QDockWidget {{
    color: {p.TEXT_PRIMARY};
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}

QDockWidget::title {{
    background-color: {p.BACKGROUND_TERTIARY};
    padding: 8px;
    border-bottom: 1px solid {p.BORDER_DEFAULT};
}}

QDockWidget::close-button,
QDockWidget::float-button {{
    background-color: transparent;
    border: none;
    padding: 2px;
}}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {{
    background-color: {p.BORDER_HOVER};
    border-radius: 2px;
}}

/* ============================================
   DIAL
   ============================================ */

QDial {{
    background-color: {p.BACKGROUND_SECONDARY};
}}

/* ============================================
   LCD NUMBER
   ============================================ */

QLCDNumber {{
    background-color: #1a1a1a;
    color: {p.ACCENT_PRIMARY};
    border: 2px solid {p.BORDER_DEFAULT};
    border-radius: 4px;
}}

/* ============================================
   CALENDAR WIDGET
   ============================================ */

QCalendarWidget {{
    background-color: {p.BACKGROUND_SECONDARY};
    color: {p.TEXT_PRIMARY};
}}

QCalendarWidget QToolButton {{
    background-color: {p.BACKGROUND_TERTIARY};
    color: {p.TEXT_PRIMARY};
    border: none;
    border-radius: 4px;
    padding: 4px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {p.ACCENT_PRIMARY};
    color: {p.BACKGROUND_PRIMARY};
}}
'''


def generate_dark_theme_qss(palette: type[ColorPalette] | None = None) -> str:
    """
    Genera el QSS del tema oscuro.

    Función conveniente que usa QSSGenerator internamente.

    Args:
        palette: Paleta de colores opcional. Por defecto DarkThemeColors.

    Returns:
        Stylesheet QSS completo.

    Example:
        qss = generate_dark_theme_qss()
        app.setStyleSheet(qss)
    """
    generator = QSSGenerator(palette)
    return generator.generate()
