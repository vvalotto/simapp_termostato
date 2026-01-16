"""
Tests unitarios para ClimatizadorModelo.

Este módulo contiene los tests que validan el comportamiento del modelo
del panel Climatizador, incluyendo creación, inmutabilidad y validación.
"""

import pytest
from dataclasses import FrozenInstanceError

from app.presentacion.paneles.climatizador.modelo import (
    ClimatizadorModelo,
    MODO_CALENTANDO,
    MODO_ENFRIANDO,
    MODO_REPOSO,
    MODO_APAGADO,
)


class TestCreacion:
    """Tests de creación del modelo ClimatizadorModelo."""

    def test_crear_con_valores_default(self):
        """
        Test: Crear modelo con valores por defecto.

        Given: No se proporcionan parámetros
        When: Se crea una instancia de ClimatizadorModelo
        Then: Se inicializa con valores por defecto correctos
        """
        modelo = ClimatizadorModelo()

        assert modelo.modo == MODO_REPOSO
        assert modelo.encendido is True

    def test_crear_con_valores_custom(self):
        """
        Test: Crear modelo con valores personalizados.

        Given: Se proporcionan parámetros personalizados
        When: Se crea una instancia de ClimatizadorModelo
        Then: Se inicializa con los valores proporcionados
        """
        modelo = ClimatizadorModelo(
            modo=MODO_CALENTANDO,
            encendido=False
        )

        assert modelo.modo == MODO_CALENTANDO
        assert modelo.encendido is False

    def test_validar_modo_calentando(self):
        """
        Test: Crear modelo con modo calentando.

        Given: Se proporciona modo=MODO_CALENTANDO
        When: Se crea una instancia de ClimatizadorModelo
        Then: El modelo acepta el modo válido
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO)

        assert modelo.modo == MODO_CALENTANDO

    def test_validar_modo_enfriando(self):
        """
        Test: Crear modelo con modo enfriando.

        Given: Se proporciona modo=MODO_ENFRIANDO
        When: Se crea una instancia de ClimatizadorModelo
        Then: El modelo acepta el modo válido
        """
        modelo = ClimatizadorModelo(modo=MODO_ENFRIANDO)

        assert modelo.modo == MODO_ENFRIANDO

    def test_validar_modo_reposo(self):
        """
        Test: Crear modelo con modo reposo.

        Given: Se proporciona modo=MODO_REPOSO
        When: Se crea una instancia de ClimatizadorModelo
        Then: El modelo acepta el modo válido
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)

        assert modelo.modo == MODO_REPOSO

    def test_validar_modo_apagado(self):
        """
        Test: Crear modelo con modo apagado.

        Given: Se proporciona modo=MODO_APAGADO
        When: Se crea una instancia de ClimatizadorModelo
        Then: El modelo acepta el modo válido
        """
        modelo = ClimatizadorModelo(modo=MODO_APAGADO)

        assert modelo.modo == MODO_APAGADO


class TestInmutabilidad:
    """Tests de inmutabilidad del modelo ClimatizadorModelo."""

    def test_es_inmutable(self):
        """
        Test: El modelo es inmutable (frozen=True).

        Given: Se crea una instancia de ClimatizadorModelo
        When: Se intenta modificar un atributo
        Then: Se lanza FrozenInstanceError
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO)

        with pytest.raises(FrozenInstanceError):
            modelo.modo = MODO_CALENTANDO

    def test_encendido_es_inmutable(self):
        """
        Test: El campo encendido es inmutable.

        Given: Se crea una instancia de ClimatizadorModelo
        When: Se intenta modificar encendido
        Then: Se lanza FrozenInstanceError
        """
        modelo = ClimatizadorModelo(encendido=True)

        with pytest.raises(FrozenInstanceError):
            modelo.encendido = False


class TestValidacion:
    """Tests de validación del modelo ClimatizadorModelo."""

    def test_modo_invalido_lanza_error(self):
        """
        Test: Modo inválido lanza ValueError.

        Given: Se proporciona modo con valor inválido
        When: Se crea una instancia de ClimatizadorModelo
        Then: Se lanza ValueError con mensaje descriptivo
        """
        with pytest.raises(ValueError) as exc_info:
            ClimatizadorModelo(modo="invalido")

        assert "modo debe ser uno de" in str(exc_info.value)
        assert "invalido" in str(exc_info.value)

    def test_modo_vacio_lanza_error(self):
        """
        Test: Modo vacío lanza ValueError.

        Given: Se proporciona modo=""
        When: Se crea una instancia de ClimatizadorModelo
        Then: Se lanza ValueError
        """
        with pytest.raises(ValueError):
            ClimatizadorModelo(modo="")


class TestMetodosUtilidad:
    """Tests de métodos de utilidad del modelo ClimatizadorModelo."""

    def test_to_dict_con_valores_default(self):
        """
        Test: Convertir modelo a diccionario con valores por defecto.

        Given: Se crea modelo con valores por defecto
        When: Se llama al método to_dict()
        Then: Se retorna diccionario con todos los campos
        """
        modelo = ClimatizadorModelo()
        resultado = modelo.to_dict()

        assert isinstance(resultado, dict)
        assert resultado["modo"] == MODO_REPOSO
        assert resultado["encendido"] is True

    def test_to_dict_con_valores_custom(self):
        """
        Test: Convertir modelo a diccionario con valores personalizados.

        Given: Se crea modelo con valores personalizados
        When: Se llama al método to_dict()
        Then: Se retorna diccionario con los valores correctos
        """
        modelo = ClimatizadorModelo(
            modo=MODO_CALENTANDO,
            encendido=False
        )
        resultado = modelo.to_dict()

        assert resultado["modo"] == MODO_CALENTANDO
        assert resultado["encendido"] is False

    def test_to_dict_contiene_todas_las_claves(self):
        """
        Test: El diccionario contiene todas las claves esperadas.

        Given: Se crea modelo
        When: Se llama al método to_dict()
        Then: El diccionario contiene exactamente las 2 claves esperadas
        """
        modelo = ClimatizadorModelo()
        resultado = modelo.to_dict()

        claves_esperadas = {"modo", "encendido"}
        assert set(resultado.keys()) == claves_esperadas


class TestPropiedadesEstado:
    """Tests de propiedades de estado del modelo."""

    def test_esta_calentando_true(self):
        """
        Test: Propiedad esta_calentando retorna True cuando corresponde.

        Given: Modelo con modo=MODO_CALENTANDO y encendido=True
        When: Se accede a la propiedad esta_calentando
        Then: Retorna True
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)

        assert modelo.esta_calentando is True

    def test_esta_calentando_false_por_modo(self):
        """
        Test: Propiedad esta_calentando retorna False cuando el modo es diferente.

        Given: Modelo con modo=MODO_REPOSO y encendido=True
        When: Se accede a la propiedad esta_calentando
        Then: Retorna False
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        assert modelo.esta_calentando is False

    def test_esta_calentando_false_por_apagado(self):
        """
        Test: Propiedad esta_calentando retorna False cuando está apagado.

        Given: Modelo con modo=MODO_CALENTANDO y encendido=False
        When: Se accede a la propiedad esta_calentando
        Then: Retorna False
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=False)

        assert modelo.esta_calentando is False

    def test_esta_enfriando_true(self):
        """
        Test: Propiedad esta_enfriando retorna True cuando corresponde.

        Given: Modelo con modo=MODO_ENFRIANDO y encendido=True
        When: Se accede a la propiedad esta_enfriando
        Then: Retorna True
        """
        modelo = ClimatizadorModelo(modo=MODO_ENFRIANDO, encendido=True)

        assert modelo.esta_enfriando is True

    def test_esta_enfriando_false_por_modo(self):
        """
        Test: Propiedad esta_enfriando retorna False cuando el modo es diferente.

        Given: Modelo con modo=MODO_REPOSO y encendido=True
        When: Se accede a la propiedad esta_enfriando
        Then: Retorna False
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        assert modelo.esta_enfriando is False

    def test_esta_en_reposo_true(self):
        """
        Test: Propiedad esta_en_reposo retorna True cuando corresponde.

        Given: Modelo con modo=MODO_REPOSO y encendido=True
        When: Se accede a la propiedad esta_en_reposo
        Then: Retorna True
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=True)

        assert modelo.esta_en_reposo is True

    def test_esta_apagado_true_por_encendido(self):
        """
        Test: Propiedad esta_apagado retorna True cuando encendido=False.

        Given: Modelo con encendido=False
        When: Se accede a la propiedad esta_apagado
        Then: Retorna True
        """
        modelo = ClimatizadorModelo(modo=MODO_REPOSO, encendido=False)

        assert modelo.esta_apagado is True

    def test_esta_apagado_true_por_modo(self):
        """
        Test: Propiedad esta_apagado retorna True cuando modo=MODO_APAGADO.

        Given: Modelo con modo=MODO_APAGADO y encendido=True
        When: Se accede a la propiedad esta_apagado
        Then: Retorna True
        """
        modelo = ClimatizadorModelo(modo=MODO_APAGADO, encendido=True)

        assert modelo.esta_apagado is True

    def test_esta_apagado_false(self):
        """
        Test: Propiedad esta_apagado retorna False cuando está operando.

        Given: Modelo con modo=MODO_CALENTANDO y encendido=True
        When: Se accede a la propiedad esta_apagado
        Then: Retorna False
        """
        modelo = ClimatizadorModelo(modo=MODO_CALENTANDO, encendido=True)

        assert modelo.esta_apagado is False
