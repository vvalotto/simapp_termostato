"""
Proveedores de feedback visual para validación de campos.

Define el protocolo para mostrar feedback de validación en widgets
y una implementación por defecto con estilos CSS.
"""
# pylint: disable=unnecessary-ellipsis,no-name-in-module
from typing import Protocol

from PyQt6.QtWidgets import QWidget


class ValidationFeedbackProvider(Protocol):
    """
    Protocolo para proveedores de feedback visual de validación.

    Permite inyectar diferentes estrategias de feedback visual
    sin modificar los widgets consumidores (OCP/DIP).

    Example:
        class IconFeedbackProvider:
            def show_valid(self, widget: QWidget) -> None:
                # Mostrar icono de check verde
                ...

            def show_invalid(self, widget: QWidget, message: str) -> None:
                # Mostrar icono de error con tooltip
                ...

        panel = ConfigPanel(validation_feedback=IconFeedbackProvider())
    """

    def show_valid(self, widget: QWidget) -> None:
        """
        Muestra el widget como válido.

        Args:
            widget: Widget a marcar como válido.
        """
        ...

    def show_invalid(self, widget: QWidget, message: str) -> None:
        """
        Muestra el widget como inválido.

        Args:
            widget: Widget a marcar como inválido.
            message: Mensaje de error a mostrar.
        """
        ...


class BorderValidationFeedback:
    """
    Proveedor de feedback visual usando bordes CSS.

    Muestra un borde rojo para campos inválidos y restaura
    el estilo por defecto para campos válidos.
    """

    def __init__(
        self,
        valid_style: str = "",
        invalid_style: str = "border: 1px solid red;"
    ):
        """
        Inicializa el proveedor de feedback.

        Args:
            valid_style: Estilo CSS para estado válido.
            invalid_style: Estilo CSS para estado inválido.
        """
        self._valid_style = valid_style
        self._invalid_style = invalid_style

    def show_valid(self, widget: QWidget) -> None:
        """Restaura el estilo por defecto del widget."""
        widget.setStyleSheet(self._valid_style)
        widget.setToolTip("")

    def show_invalid(self, widget: QWidget, message: str) -> None:
        """Aplica estilo de error y muestra tooltip."""
        widget.setStyleSheet(self._invalid_style)
        widget.setToolTip(message)

    @property
    def valid_style(self) -> str:
        """Retorna el estilo CSS para estado válido."""
        return self._valid_style

    @property
    def invalid_style(self) -> str:
        """Retorna el estilo CSS para estado inválido."""
        return self._invalid_style
