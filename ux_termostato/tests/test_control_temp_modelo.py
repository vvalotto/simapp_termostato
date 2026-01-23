"""
Tests unitarios para ControlTempModelo.

Valida la creación, inmutabilidad, validación de rangos y serialización
del modelo de datos del panel Control de Temperatura.
"""

import pytest

from app.presentacion.paneles.control_temp.modelo import ControlTempModelo


class TestCreacion:
    """Tests de creación e inicialización de ControlTempModelo."""

    def test_crear_modelo_con_valores_default(self):
        """Test que ControlTempModelo se crea con valores por defecto."""
        modelo = ControlTempModelo()

        assert modelo.temperatura_deseada == 22.0
        assert modelo.habilitado is False
        assert modelo.temp_min == 15.0
        assert modelo.temp_max == 35.0
        assert modelo.incremento == 0.5

    def test_crear_modelo_con_temperatura_custom(self):
        """Test que ControlTempModelo se puede crear con temperatura custom."""
        modelo = ControlTempModelo(temperatura_deseada=25.5)

        assert modelo.temperatura_deseada == 25.5
        assert modelo.habilitado is False

    def test_crear_modelo_habilitado(self):
        """Test que ControlTempModelo se puede crear habilitado."""
        modelo = ControlTempModelo(habilitado=True)

        assert modelo.habilitado is True
        assert modelo.temperatura_deseada == 22.0

    def test_crear_modelo_con_todos_los_parametros(self):
        """Test crear modelo con todos los parámetros personalizados."""
        modelo = ControlTempModelo(
            temperatura_deseada=30.0,
            habilitado=True,
            temp_min=10.0,
            temp_max=40.0,
            incremento=1.0
        )

        assert modelo.temperatura_deseada == 30.0
        assert modelo.habilitado is True
        assert modelo.temp_min == 10.0
        assert modelo.temp_max == 40.0
        assert modelo.incremento == 1.0


class TestInmutabilidad:
    """Tests de inmutabilidad del dataclass."""

    def test_modelo_es_frozen(self):
        """Test que el modelo es inmutable (frozen=True)."""
        modelo = ControlTempModelo(temperatura_deseada=22.0)

        # Intentar modificar un atributo debe lanzar FrozenInstanceError
        with pytest.raises(AttributeError):
            modelo.temperatura_deseada = 25.0

    def test_no_se_puede_modificar_habilitado(self):
        """Test que no se puede modificar el atributo habilitado."""
        modelo = ControlTempModelo(habilitado=False)

        with pytest.raises(AttributeError):
            modelo.habilitado = True

    def test_crear_nuevo_modelo_con_replace(self):
        """Test que se puede crear un nuevo modelo con dataclasses.replace."""
        from dataclasses import replace

        modelo_inicial = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)
        modelo_nuevo = replace(modelo_inicial, temperatura_deseada=23.0, habilitado=True)

        # El modelo inicial no cambió
        assert modelo_inicial.temperatura_deseada == 22.0
        assert modelo_inicial.habilitado is False

        # El nuevo modelo tiene los valores actualizados
        assert modelo_nuevo.temperatura_deseada == 23.0
        assert modelo_nuevo.habilitado is True


class TestPuedeAumentar:
    """Tests del método puede_aumentar()."""

    def test_puede_aumentar_cuando_habilitado_y_no_en_maximo(self):
        """Test que puede_aumentar retorna True cuando está habilitado y no alcanzó el máximo."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        assert modelo.puede_aumentar() is True

    def test_no_puede_aumentar_cuando_deshabilitado(self):
        """Test que puede_aumentar retorna False cuando está deshabilitado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)

        assert modelo.puede_aumentar() is False

    def test_no_puede_aumentar_cuando_en_maximo(self):
        """Test que puede_aumentar retorna False cuando alcanzó el máximo."""
        modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=True)

        assert modelo.puede_aumentar() is False

    def test_no_puede_aumentar_cuando_deshabilitado_y_en_maximo(self):
        """Test que puede_aumentar retorna False cuando deshabilitado y en máximo."""
        modelo = ControlTempModelo(temperatura_deseada=35.0, habilitado=False)

        assert modelo.puede_aumentar() is False

    def test_puede_aumentar_justo_antes_del_maximo(self):
        """Test que puede aumentar cuando está justo antes del máximo."""
        modelo = ControlTempModelo(temperatura_deseada=34.5, habilitado=True)

        assert modelo.puede_aumentar() is True


class TestPuedeDisminuir:
    """Tests del método puede_disminuir()."""

    def test_puede_disminuir_cuando_habilitado_y_no_en_minimo(self):
        """Test que puede_disminuir retorna True cuando está habilitado y no alcanzó el mínimo."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        assert modelo.puede_disminuir() is True

    def test_no_puede_disminuir_cuando_deshabilitado(self):
        """Test que puede_disminuir retorna False cuando está deshabilitado."""
        modelo = ControlTempModelo(temperatura_deseada=22.0, habilitado=False)

        assert modelo.puede_disminuir() is False

    def test_no_puede_disminuir_cuando_en_minimo(self):
        """Test que puede_disminuir retorna False cuando alcanzó el mínimo."""
        modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=True)

        assert modelo.puede_disminuir() is False

    def test_no_puede_disminuir_cuando_deshabilitado_y_en_minimo(self):
        """Test que puede_disminuir retorna False cuando deshabilitado y en mínimo."""
        modelo = ControlTempModelo(temperatura_deseada=15.0, habilitado=False)

        assert modelo.puede_disminuir() is False

    def test_puede_disminuir_justo_encima_del_minimo(self):
        """Test que puede disminuir cuando está justo encima del mínimo."""
        modelo = ControlTempModelo(temperatura_deseada=15.5, habilitado=True)

        assert modelo.puede_disminuir() is True


class TestRangos:
    """Tests de validación de rangos de temperatura."""

    def test_temperatura_minima_default(self):
        """Test que el rango mínimo por defecto es 15°C."""
        modelo = ControlTempModelo()

        assert modelo.temp_min == 15.0

    def test_temperatura_maxima_default(self):
        """Test que el rango máximo por defecto es 35°C."""
        modelo = ControlTempModelo()

        assert modelo.temp_max == 35.0

    def test_incremento_default(self):
        """Test que el incremento por defecto es 0.5°C."""
        modelo = ControlTempModelo()

        assert modelo.incremento == 0.5

    def test_temperatura_deseada_default(self):
        """Test que la temperatura deseada por defecto es 22°C."""
        modelo = ControlTempModelo()

        assert modelo.temperatura_deseada == 22.0


class TestSerializacion:
    """Tests de serialización a diccionario."""

    def test_to_dict_con_valores_default(self):
        """Test que to_dict() serializa correctamente con valores por defecto."""
        modelo = ControlTempModelo()
        resultado = modelo.to_dict()

        assert isinstance(resultado, dict)
        assert resultado == {
            "temperatura_deseada": 22.0,
            "habilitado": False,
            "temp_min": 15.0,
            "temp_max": 35.0,
            "incremento": 0.5,
        }

    def test_to_dict_con_modelo_habilitado(self):
        """Test que to_dict() serializa correctamente un modelo habilitado."""
        modelo = ControlTempModelo(temperatura_deseada=25.5, habilitado=True)
        resultado = modelo.to_dict()

        assert resultado["temperatura_deseada"] == 25.5
        assert resultado["habilitado"] is True

    def test_to_dict_contiene_todas_las_claves(self):
        """Test que to_dict() contiene todas las claves esperadas."""
        modelo = ControlTempModelo()
        resultado = modelo.to_dict()

        claves_esperadas = {
            "temperatura_deseada",
            "habilitado",
            "temp_min",
            "temp_max",
            "incremento",
        }

        assert set(resultado.keys()) == claves_esperadas

    def test_to_dict_valores_son_correctos(self):
        """Test que to_dict() preserva todos los valores correctamente."""
        modelo = ControlTempModelo(
            temperatura_deseada=30.0,
            habilitado=True,
            temp_min=10.0,
            temp_max=40.0,
            incremento=1.0
        )
        resultado = modelo.to_dict()

        assert resultado["temperatura_deseada"] == 30.0
        assert resultado["habilitado"] is True
        assert resultado["temp_min"] == 10.0
        assert resultado["temp_max"] == 40.0
        assert resultado["incremento"] == 1.0


class TestRepresentacion:
    """Tests de representación del modelo."""

    def test_repr_modelo(self):
        """Test que el repr del modelo es legible."""
        modelo = ControlTempModelo(temperatura_deseada=23.5, habilitado=True)
        repr_str = repr(modelo)

        assert "ControlTempModelo" in repr_str
        assert "temperatura_deseada=23.5" in repr_str
        assert "habilitado=True" in repr_str


class TestIgualdad:
    """Tests de comparación de modelos."""

    def test_modelos_iguales(self):
        """Test que dos modelos con mismo estado son iguales."""
        modelo_1 = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)
        modelo_2 = ControlTempModelo(temperatura_deseada=22.0, habilitado=True)

        assert modelo_1 == modelo_2

    def test_modelos_diferentes_temperatura(self):
        """Test que dos modelos con distinta temperatura no son iguales."""
        modelo_1 = ControlTempModelo(temperatura_deseada=22.0)
        modelo_2 = ControlTempModelo(temperatura_deseada=23.0)

        assert modelo_1 != modelo_2

    def test_modelos_diferentes_habilitado(self):
        """Test que dos modelos con distinto estado habilitado no son iguales."""
        modelo_1 = ControlTempModelo(habilitado=True)
        modelo_2 = ControlTempModelo(habilitado=False)

        assert modelo_1 != modelo_2

    def test_modelos_default_iguales(self):
        """Test que dos modelos creados con defaults son iguales."""
        modelo_1 = ControlTempModelo()
        modelo_2 = ControlTempModelo()

        assert modelo_1 == modelo_2
