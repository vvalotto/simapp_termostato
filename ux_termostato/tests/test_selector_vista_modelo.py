"""
Tests unitarios para SelectorVistaModelo.

Este módulo contiene los tests que validan el comportamiento del modelo
del panel SelectorVista, incluyendo creación, inmutabilidad y validación.
"""

import pytest
from dataclasses import FrozenInstanceError

from app.presentacion.paneles.selector_vista.modelo import SelectorVistaModelo


class TestCreacion:
    """Tests de creación del modelo SelectorVistaModelo."""

    def test_crear_con_modo_ambiente(self):
        """
        Test: Crear modelo con modo ambiente.

        Given: Se proporciona modo "ambiente"
        When: Se crea una instancia de SelectorVistaModelo
        Then: Se inicializa correctamente con modo ambiente
        """
        modelo = SelectorVistaModelo(modo="ambiente")

        assert modelo.modo == "ambiente"
        assert modelo.habilitado is True

    def test_crear_con_modo_deseada(self):
        """
        Test: Crear modelo con modo deseada.

        Given: Se proporciona modo "deseada"
        When: Se crea una instancia de SelectorVistaModelo
        Then: Se inicializa correctamente con modo deseada
        """
        modelo = SelectorVistaModelo(modo="deseada")

        assert modelo.modo == "deseada"
        assert modelo.habilitado is True

    def test_crear_deshabilitado(self):
        """
        Test: Crear modelo deshabilitado.

        Given: Se proporciona habilitado=False
        When: Se crea una instancia de SelectorVistaModelo
        Then: Se inicializa deshabilitado
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=False)

        assert modelo.modo == "ambiente"
        assert modelo.habilitado is False


class TestValidaciones:
    """Tests de validaciones del modelo SelectorVistaModelo."""

    def test_modo_invalido_lanza_excepcion(self):
        """
        Test: Crear modelo con modo inválido lanza excepción.

        Given: Se proporciona un modo inválido
        When: Se intenta crear una instancia de SelectorVistaModelo
        Then: Se lanza ValueError con mensaje apropiado
        """
        with pytest.raises(ValueError) as exc_info:
            SelectorVistaModelo(modo="invalido")

        assert "Modo inválido" in str(exc_info.value)
        assert "invalido" in str(exc_info.value)

    def test_modo_vacio_lanza_excepcion(self):
        """
        Test: Crear modelo con modo vacío lanza excepción.

        Given: Se proporciona modo vacío
        When: Se intenta crear una instancia de SelectorVistaModelo
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            SelectorVistaModelo(modo="")

        assert "Modo inválido" in str(exc_info.value)

    def test_modo_mayusculas_lanza_excepcion(self):
        """
        Test: Modo con mayúsculas no es válido.

        Given: Se proporciona modo "AMBIENTE" en mayúsculas
        When: Se intenta crear una instancia de SelectorVistaModelo
        Then: Se lanza ValueError (case-sensitive)
        """
        with pytest.raises(ValueError):
            SelectorVistaModelo(modo="AMBIENTE")


class TestInmutabilidad:
    """Tests de inmutabilidad del modelo SelectorVistaModelo."""

    def test_es_inmutable(self):
        """
        Test: El modelo es inmutable.

        Given: Una instancia de SelectorVistaModelo
        When: Se intenta modificar el atributo modo
        Then: Se lanza FrozenInstanceError
        """
        modelo = SelectorVistaModelo(modo="ambiente")

        with pytest.raises(FrozenInstanceError):
            modelo.modo = "deseada"

    def test_habilitado_es_inmutable(self):
        """
        Test: El atributo habilitado es inmutable.

        Given: Una instancia de SelectorVistaModelo
        When: Se intenta modificar el atributo habilitado
        Then: Se lanza FrozenInstanceError
        """
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)

        with pytest.raises(FrozenInstanceError):
            modelo.habilitado = False
