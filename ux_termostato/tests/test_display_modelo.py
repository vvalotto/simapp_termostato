"""
Tests unitarios para DisplayModelo.

Este módulo contiene los tests que validan el comportamiento del modelo
del panel Display LCD, incluyendo creación, inmutabilidad y validación.
"""

import pytest
from dataclasses import FrozenInstanceError

from app.presentacion.paneles.display.modelo import DisplayModelo


class TestCreacion:
    """Tests de creación del modelo DisplayModelo."""

    def test_crear_con_valores_default(self):
        """
        Test: Crear modelo con valores por defecto.

        Given: No se proporcionan parámetros
        When: Se crea una instancia de DisplayModelo
        Then: Se inicializa con valores por defecto correctos
        """
        modelo = DisplayModelo()

        assert modelo.temperatura == 0.0
        assert modelo.modo_vista == "ambiente"
        assert modelo.encendido is True
        assert modelo.error_sensor is False

    def test_crear_con_valores_custom(self):
        """
        Test: Crear modelo con valores personalizados.

        Given: Se proporcionan parámetros personalizados
        When: Se crea una instancia de DisplayModelo
        Then: Se inicializa con los valores proporcionados
        """
        modelo = DisplayModelo(
            temperatura=22.5,
            modo_vista="deseada",
            encendido=False,
            error_sensor=True
        )

        assert modelo.temperatura == 22.5
        assert modelo.modo_vista == "deseada"
        assert modelo.encendido is False
        assert modelo.error_sensor is True

    def test_crear_con_temperatura_negativa(self):
        """
        Test: Crear modelo con temperatura negativa.

        Given: Se proporciona temperatura negativa válida
        When: Se crea una instancia de DisplayModelo
        Then: Se acepta el valor negativo
        """
        modelo = DisplayModelo(temperatura=-5.0)

        assert modelo.temperatura == -5.0

    def test_crear_con_temperatura_alta(self):
        """
        Test: Crear modelo con temperatura alta.

        Given: Se proporciona temperatura alta válida
        When: Se crea una instancia de DisplayModelo
        Then: Se acepta el valor alto
        """
        modelo = DisplayModelo(temperatura=45.0)

        assert modelo.temperatura == 45.0


class TestInmutabilidad:
    """Tests de inmutabilidad del modelo DisplayModelo."""

    def test_es_inmutable(self):
        """
        Test: El modelo es inmutable (frozen=True).

        Given: Se crea una instancia de DisplayModelo
        When: Se intenta modificar un atributo
        Then: Se lanza FrozenInstanceError
        """
        modelo = DisplayModelo(temperatura=22.0)

        with pytest.raises(FrozenInstanceError):
            modelo.temperatura = 25.0

    def test_modo_vista_es_inmutable(self):
        """
        Test: El campo modo_vista es inmutable.

        Given: Se crea una instancia de DisplayModelo
        When: Se intenta modificar modo_vista
        Then: Se lanza FrozenInstanceError
        """
        modelo = DisplayModelo(modo_vista="ambiente")

        with pytest.raises(FrozenInstanceError):
            modelo.modo_vista = "deseada"

    def test_encendido_es_inmutable(self):
        """
        Test: El campo encendido es inmutable.

        Given: Se crea una instancia de DisplayModelo
        When: Se intenta modificar encendido
        Then: Se lanza FrozenInstanceError
        """
        modelo = DisplayModelo(encendido=True)

        with pytest.raises(FrozenInstanceError):
            modelo.encendido = False


class TestValidacion:
    """Tests de validación del modelo DisplayModelo."""

    def test_modo_vista_valido_ambiente(self):
        """
        Test: Modo vista "ambiente" es válido.

        Given: Se proporciona modo_vista="ambiente"
        When: Se crea una instancia de DisplayModelo
        Then: Se crea exitosamente sin errores
        """
        modelo = DisplayModelo(modo_vista="ambiente")

        assert modelo.modo_vista == "ambiente"

    def test_modo_vista_valido_deseada(self):
        """
        Test: Modo vista "deseada" es válido.

        Given: Se proporciona modo_vista="deseada"
        When: Se crea una instancia de DisplayModelo
        Then: Se crea exitosamente sin errores
        """
        modelo = DisplayModelo(modo_vista="deseada")

        assert modelo.modo_vista == "deseada"

    def test_modo_vista_invalido_lanza_error(self):
        """
        Test: Modo vista inválido lanza ValueError.

        Given: Se proporciona modo_vista con valor inválido
        When: Se crea una instancia de DisplayModelo
        Then: Se lanza ValueError con mensaje descriptivo
        """
        with pytest.raises(ValueError) as exc_info:
            DisplayModelo(modo_vista="invalido")

        assert "modo_vista debe ser 'ambiente' o 'deseada'" in str(exc_info.value)
        assert "invalido" in str(exc_info.value)

    def test_modo_vista_vacio_lanza_error(self):
        """
        Test: Modo vista vacío lanza ValueError.

        Given: Se proporciona modo_vista=""
        When: Se crea una instancia de DisplayModelo
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError):
            DisplayModelo(modo_vista="")


class TestMetodosUtilidad:
    """Tests de métodos de utilidad del modelo DisplayModelo."""

    def test_to_dict_con_valores_default(self):
        """
        Test: Convertir modelo a diccionario con valores por defecto.

        Given: Se crea modelo con valores por defecto
        When: Se llama al método to_dict()
        Then: Se retorna diccionario con todos los campos
        """
        modelo = DisplayModelo()
        resultado = modelo.to_dict()

        assert isinstance(resultado, dict)
        assert resultado["temperatura"] == 0.0
        assert resultado["modo_vista"] == "ambiente"
        assert resultado["encendido"] is True
        assert resultado["error_sensor"] is False

    def test_to_dict_con_valores_custom(self):
        """
        Test: Convertir modelo a diccionario con valores personalizados.

        Given: Se crea modelo con valores personalizados
        When: Se llama al método to_dict()
        Then: Se retorna diccionario con los valores correctos
        """
        modelo = DisplayModelo(
            temperatura=22.5,
            modo_vista="deseada",
            encendido=False,
            error_sensor=True
        )
        resultado = modelo.to_dict()

        assert resultado["temperatura"] == 22.5
        assert resultado["modo_vista"] == "deseada"
        assert resultado["encendido"] is False
        assert resultado["error_sensor"] is True

    def test_to_dict_contiene_todas_las_claves(self):
        """
        Test: El diccionario contiene todas las claves esperadas.

        Given: Se crea modelo
        When: Se llama al método to_dict()
        Then: El diccionario contiene exactamente las 4 claves esperadas
        """
        modelo = DisplayModelo()
        resultado = modelo.to_dict()

        claves_esperadas = {"temperatura", "modo_vista", "encendido", "error_sensor"}
        assert set(resultado.keys()) == claves_esperadas
