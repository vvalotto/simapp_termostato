"""
Configuración de fixtures para tests de ux_termostato.

Este módulo contiene fixtures compartidas para todos los tests,
incluyendo configuración de PyQt6 y componentes del panel Display.
"""

import pytest
from PyQt6.QtWidgets import QApplication

from app.presentacion.paneles.display.modelo import DisplayModelo
from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.controlador import DisplayControlador


@pytest.fixture(scope="session")
def qapp():
    """
    Fixture de sesión para QApplication.

    PyQt6 requiere una instancia de QApplication para crear widgets.
    Esta fixture asegura que exista una única instancia durante toda
    la sesión de tests.

    Yields:
        QApplication: Instancia de la aplicación Qt
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def display_modelo():
    """
    Fixture para crear un DisplayModelo con valores por defecto.

    Returns:
        DisplayModelo: Instancia con temperatura=22.0, modo_vista="ambiente"
    """
    return DisplayModelo(
        temperatura=22.0,
        modo_vista="ambiente",
        encendido=True,
        error_sensor=False
    )


@pytest.fixture
def display_modelo_custom():
    """
    Fixture factory para crear DisplayModelo con valores personalizados.

    Returns:
        callable: Función que crea DisplayModelo con parámetros custom
    """
    def _crear_modelo(**kwargs):
        """
        Crea DisplayModelo con valores personalizados.

        Args:
            **kwargs: Parámetros para DisplayModelo

        Returns:
            DisplayModelo: Instancia con valores custom
        """
        defaults = {
            "temperatura": 22.0,
            "modo_vista": "ambiente",
            "encendido": True,
            "error_sensor": False
        }
        defaults.update(kwargs)
        return DisplayModelo(**defaults)
    return _crear_modelo


@pytest.fixture
def display_vista(qapp):
    """
    Fixture para crear un DisplayVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        DisplayVista: Instancia de la vista del display
    """
    return DisplayVista()


@pytest.fixture
def display_controlador(qapp, display_modelo, display_vista):
    """
    Fixture para crear un DisplayControlador completo.

    Args:
        qapp: Fixture de QApplication
        display_modelo: Fixture de DisplayModelo
        display_vista: Fixture de DisplayVista

    Returns:
        DisplayControlador: Controlador completamente configurado
    """
    return DisplayControlador(display_modelo, display_vista)


@pytest.fixture
def display_controlador_custom(qapp):
    """
    Fixture factory para crear DisplayControlador con configuración custom.

    Args:
        qapp: Fixture de QApplication

    Returns:
        callable: Función que crea DisplayControlador con parámetros custom
    """
    def _crear_controlador(modelo=None, vista=None):
        """
        Crea DisplayControlador con componentes personalizados.

        Args:
            modelo: DisplayModelo opcional (crea uno por defecto si None)
            vista: DisplayVista opcional (crea una por defecto si None)

        Returns:
            DisplayControlador: Controlador configurado
        """
        if modelo is None:
            modelo = DisplayModelo()
        if vista is None:
            vista = DisplayVista()
        return DisplayControlador(modelo, vista)
    return _crear_controlador
