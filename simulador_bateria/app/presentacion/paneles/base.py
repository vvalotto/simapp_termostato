"""Clases base para el patrón MVC de paneles.

Define las interfaces abstractas que todos los paneles deben implementar,
estableciendo contratos claros para Modelo, Vista y Controlador.
"""

from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


M = TypeVar('M')  # Tipo del Modelo
V = TypeVar('V', bound=QWidget)  # Tipo de la Vista


class ModeloBase:
    """Clase base para modelos de panel.

    Los modelos contienen los datos y la lógica de negocio
    del panel, sin conocimiento de la presentación.
    Subclases deben ser dataclasses con los datos específicos.
    """


class VistaBaseMeta(ABCMeta, type(QWidget)):
    """Metaclase que combina ABCMeta con la metaclase de QWidget."""


class VistaBase(QWidget, metaclass=VistaBaseMeta):
    """Clase base abstracta para vistas de panel.

    Las vistas son responsables únicamente de la presentación
    visual, sin lógica de negocio.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Inicializa la vista base.

        Args:
            parent: Widget padre opcional.
        """
        super().__init__(parent)

    @abstractmethod
    def actualizar(self, modelo: ModeloBase) -> None:
        """Actualiza la vista con datos del modelo.

        Args:
            modelo: Instancia del modelo con los datos a mostrar.
        """
        pass


class ControladorBaseMeta(ABCMeta, type(QObject)):
    """Metaclase que combina ABCMeta con la metaclase de QObject."""


class ControladorBase(QObject, Generic[M, V], metaclass=ControladorBaseMeta):
    """Clase base abstracta para controladores de panel.

    Los controladores coordinan la comunicación entre el modelo
    y la vista, manejando eventos y actualizaciones.

    Attributes:
        modelo_cambiado: Signal emitido cuando el modelo cambia.
    """

    modelo_cambiado = pyqtSignal(object)

    def __init__(
        self,
        modelo: M,
        vista: V,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador.

        Args:
            modelo: Instancia del modelo de datos.
            vista: Instancia de la vista asociada.
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._modelo = modelo
        self._vista = vista
        self._conectar_signals()

    @property
    def modelo(self) -> M:
        """Retorna el modelo asociado."""
        return self._modelo

    @property
    def vista(self) -> V:
        """Retorna la vista asociada."""
        return self._vista

    @abstractmethod
    def _conectar_signals(self) -> None:
        """Conecta las señales entre vista y modelo.

        Las subclases deben implementar este método para
        establecer las conexiones específicas del panel.
        """
        pass

    def _actualizar_vista(self) -> None:
        """Actualiza la vista con el estado actual del modelo."""
        self._vista.actualizar(self._modelo)
        self.modelo_cambiado.emit(self._modelo)
