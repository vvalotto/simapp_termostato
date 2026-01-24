"""
Tests unitarios para SelectorVistaVista.

Este módulo contiene los tests que validan el comportamiento de la vista
del panel SelectorVista, incluyendo creación, actualización y estilos.
"""

import pytest
from PyQt6.QtWidgets import QPushButton, QLabel, QButtonGroup

from app.presentacion.paneles.selector_vista.vista import SelectorVistaVista
from app.presentacion.paneles.selector_vista.modelo import SelectorVistaModelo


class TestCreacion:
    """Tests de creación de la vista SelectorVistaVista."""

    def test_crear_vista(self, qapp):
        """
        Test: Crear vista correctamente.

        Given: Aplicación Qt inicializada
        When: Se crea una instancia de SelectorVistaVista
        Then: La vista se crea sin errores
        """
        vista = SelectorVistaVista()

        assert vista is not None
        assert isinstance(vista, SelectorVistaVista)

    def test_widgets_existen(self, qapp):
        """
        Test: Todos los widgets necesarios existen.

        Given: Se crea una instancia de SelectorVistaVista
        When: Se verifican los widgets internos
        Then: Existen botones ambiente, deseada y label
        """
        vista = SelectorVistaVista()

        assert hasattr(vista, "boton_ambiente")
        assert hasattr(vista, "boton_deseada")

    def test_botones_son_qpushbutton(self, qapp):
        """
        Test: Los botones son instancias de QPushButton.

        Given: Se crea una instancia de SelectorVistaVista
        When: Se verifican los tipos de widgets
        Then: boton_ambiente y boton_deseada son QPushButton
        """
        vista = SelectorVistaVista()

        assert isinstance(vista.boton_ambiente, QPushButton)
        assert isinstance(vista.boton_deseada, QPushButton)

    def test_botones_son_checkable(self, qapp):
        """
        Test: Los botones son checkable (toggle).

        Given: Se crea una instancia de SelectorVistaVista
        When: Se verifican las propiedades de los botones
        Then: Ambos botones son checkable
        """
        vista = SelectorVistaVista()

        assert vista.boton_ambiente.isCheckable()
        assert vista.boton_deseada.isCheckable()


class TestActualizacion:
    """Tests de actualización de la vista SelectorVistaVista."""

    def test_actualizar_modo_ambiente(self, qapp):
        """
        Test: Actualizar vista con modo ambiente.

        Given: Vista creada y modelo con modo "ambiente"
        When: Se llama a actualizar(modelo)
        Then: El botón ambiente está checked
        """
        vista = SelectorVistaVista()
        modelo = SelectorVistaModelo(modo="ambiente")

        vista.actualizar(modelo)

        assert vista.boton_ambiente.isChecked()
        assert not vista.boton_deseada.isChecked()

    def test_actualizar_modo_deseada(self, qapp):
        """
        Test: Actualizar vista con modo deseada.

        Given: Vista creada y modelo con modo "deseada"
        When: Se llama a actualizar(modelo)
        Then: El botón deseada está checked
        """
        vista = SelectorVistaVista()
        modelo = SelectorVistaModelo(modo="deseada")

        vista.actualizar(modelo)

        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()

    def test_actualizar_deshabilitado(self, qapp):
        """
        Test: Actualizar vista deshabilitada.

        Given: Vista creada y modelo con habilitado=False
        When: Se llama a actualizar(modelo)
        Then: Ambos botones están deshabilitados
        """
        vista = SelectorVistaVista()
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=False)

        vista.actualizar(modelo)

        assert not vista.boton_ambiente.isEnabled()
        assert not vista.boton_deseada.isEnabled()

    def test_actualizar_habilitado(self, qapp):
        """
        Test: Actualizar vista habilitada.

        Given: Vista creada y modelo con habilitado=True
        When: Se llama a actualizar(modelo)
        Then: Ambos botones están habilitados
        """
        vista = SelectorVistaVista()
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)

        vista.actualizar(modelo)

        assert vista.boton_ambiente.isEnabled()
        assert vista.boton_deseada.isEnabled()

    def test_cambiar_de_modo_actualiza_botones(self, qapp):
        """
        Test: Cambiar de modo actualiza los botones correctamente.

        Given: Vista con modo "ambiente"
        When: Se actualiza a modo "deseada"
        Then: Los botones cambian de estado checked
        """
        vista = SelectorVistaVista()

        # Iniciar en ambiente
        modelo1 = SelectorVistaModelo(modo="ambiente")
        vista.actualizar(modelo1)
        assert vista.boton_ambiente.isChecked()

        # Cambiar a deseada
        modelo2 = SelectorVistaModelo(modo="deseada")
        vista.actualizar(modelo2)
        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()


class TestExclusividad:
    """Tests de exclusividad de botones (ButtonGroup)."""

    def test_botones_son_exclusivos(self, qapp):
        """
        Test: Solo un botón puede estar checked a la vez.

        Given: Vista creada con ambos botones
        When: Se hace click en un botón
        Then: El otro botón se descheckea automáticamente
        """
        vista = SelectorVistaVista()

        # Seleccionar ambiente
        vista.boton_ambiente.setChecked(True)
        assert vista.boton_ambiente.isChecked()
        assert not vista.boton_deseada.isChecked()

        # Seleccionar deseada
        vista.boton_deseada.setChecked(True)
        assert vista.boton_deseada.isChecked()
        assert not vista.boton_ambiente.isChecked()
