"""Vista del panel selector de vista."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QButtonGroup
from PyQt6.QtCore import Qt

from .modelo import SelectorVistaModelo


class SelectorVistaVista(QWidget):
    """Vista del selector de vista.

    Presenta dos botones tipo toggle para seleccionar entre vista
    "ambiente" y "deseada". Solo un botón puede estar activo a la vez.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inicializar_ui()

    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Label
        self._label = QLabel("Vista:")
        self._label.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 14px;")

        # Botones tipo toggle (ButtonGroup para exclusividad)
        self._btn_ambiente = QPushButton("🌡️ Ambiente")
        self._btn_deseada = QPushButton("🎯 Deseada")

        # Configurar como checkable
        self._btn_ambiente.setCheckable(True)
        self._btn_deseada.setCheckable(True)

        # ButtonGroup para exclusividad
        self._grupo = QButtonGroup(self)
        self._grupo.addButton(self._btn_ambiente)
        self._grupo.addButton(self._btn_deseada)

        # Layout
        layout.addWidget(self._label)
        layout.addWidget(self._btn_ambiente)
        layout.addWidget(self._btn_deseada)
        layout.addStretch()

        # Estilos
        self._aplicar_estilos()

    def _aplicar_estilos(self):
        """Aplica estilos a los botones."""
        # Botón ambiente (checked = verde)
        self._btn_ambiente.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:checked {
                background-color: #28a745;
                border-color: #28a745;
                font-weight: bold;
            }
            QPushButton:hover:!checked {
                background-color: #3d3d3d;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
                border-color: #333333;
            }
        """)

        # Botón deseada (checked = azul)
        self._btn_deseada.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:checked {
                background-color: #007bff;
                border-color: #007bff;
                font-weight: bold;
            }
            QPushButton:hover:!checked {
                background-color: #3d3d3d;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
                border-color: #333333;
            }
        """)

    def actualizar(self, modelo: SelectorVistaModelo):
        """Actualiza la vista desde el modelo.

        Args:
            modelo: Modelo con el estado actual del selector
        """
        # Seleccionar botón según modo
        if modelo.modo == "ambiente":
            self._btn_ambiente.setChecked(True)
        else:
            self._btn_deseada.setChecked(True)

        # Habilitar/deshabilitar
        self._btn_ambiente.setEnabled(modelo.habilitado)
        self._btn_deseada.setEnabled(modelo.habilitado)

    @property
    def boton_ambiente(self) -> QPushButton:
        """Retorna el botón de vista ambiente."""
        return self._btn_ambiente

    @property
    def boton_deseada(self) -> QPushButton:
        """Retorna el botón de vista deseada."""
        return self._btn_deseada
