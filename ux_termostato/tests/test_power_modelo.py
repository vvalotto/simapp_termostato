"""
Tests unitarios para PowerModelo.

Valida la creación, inmutabilidad y serialización del modelo de datos
del panel Power.
"""

import pytest

from app.presentacion.paneles.power.modelo import PowerModelo


class TestCreacion:
    """Tests de creación e inicialización de PowerModelo."""

    def test_crear_modelo_con_valores_default(self):
        """Test que PowerModelo se crea con valores por defecto."""
        modelo = PowerModelo()

        assert modelo.encendido is False

    def test_crear_modelo_apagado(self):
        """Test que PowerModelo se puede crear explícitamente apagado."""
        modelo = PowerModelo(encendido=False)

        assert modelo.encendido is False

    def test_crear_modelo_encendido(self):
        """Test que PowerModelo se puede crear encendido."""
        modelo = PowerModelo(encendido=True)

        assert modelo.encendido is True


class TestInmutabilidad:
    """Tests de inmutabilidad del dataclass."""

    def test_modelo_es_frozen(self):
        """Test que el modelo es inmutable (frozen=True)."""
        modelo = PowerModelo(encendido=False)

        # Intentar modificar un atributo debe lanzar FrozenInstanceError
        with pytest.raises(AttributeError):
            modelo.encendido = True

    def test_crear_nuevo_modelo_con_replace(self):
        """Test que se puede crear un nuevo modelo con dataclasses.replace."""
        from dataclasses import replace

        modelo_inicial = PowerModelo(encendido=False)
        modelo_nuevo = replace(modelo_inicial, encendido=True)

        # El modelo inicial no cambió
        assert modelo_inicial.encendido is False

        # El nuevo modelo tiene el valor actualizado
        assert modelo_nuevo.encendido is True


class TestSerializacion:
    """Tests de serialización a diccionario."""

    def test_to_dict_con_modelo_apagado(self):
        """Test que to_dict() serializa correctamente un modelo apagado."""
        modelo = PowerModelo(encendido=False)
        resultado = modelo.to_dict()

        assert isinstance(resultado, dict)
        assert resultado == {"encendido": False}

    def test_to_dict_con_modelo_encendido(self):
        """Test que to_dict() serializa correctamente un modelo encendido."""
        modelo = PowerModelo(encendido=True)
        resultado = modelo.to_dict()

        assert isinstance(resultado, dict)
        assert resultado == {"encendido": True}

    def test_to_dict_contiene_todas_las_claves(self):
        """Test que to_dict() contiene todas las claves esperadas."""
        modelo = PowerModelo()
        resultado = modelo.to_dict()

        assert "encendido" in resultado
        assert len(resultado) == 1  # Solo debe tener una clave


class TestRepresentacion:
    """Tests de representación del modelo."""

    def test_repr_modelo_apagado(self):
        """Test que el repr del modelo es legible."""
        modelo = PowerModelo(encendido=False)
        repr_str = repr(modelo)

        assert "PowerModelo" in repr_str
        assert "encendido=False" in repr_str

    def test_repr_modelo_encendido(self):
        """Test que el repr del modelo encendido es legible."""
        modelo = PowerModelo(encendido=True)
        repr_str = repr(modelo)

        assert "PowerModelo" in repr_str
        assert "encendido=True" in repr_str


class TestIgualdad:
    """Tests de comparación de modelos."""

    def test_modelos_iguales(self):
        """Test que dos modelos con mismo estado son iguales."""
        modelo_1 = PowerModelo(encendido=True)
        modelo_2 = PowerModelo(encendido=True)

        assert modelo_1 == modelo_2

    def test_modelos_diferentes(self):
        """Test que dos modelos con distinto estado no son iguales."""
        modelo_1 = PowerModelo(encendido=True)
        modelo_2 = PowerModelo(encendido=False)

        assert modelo_1 != modelo_2

    def test_modelos_default_iguales(self):
        """Test que dos modelos creados con defaults son iguales."""
        modelo_1 = PowerModelo()
        modelo_2 = PowerModelo()

        assert modelo_1 == modelo_2
