"""Tests para ControlPanelModelo.

CRITICO: Cubre conversion bidireccional voltaje <-> paso slider.
"""

import pytest

from app.presentacion.paneles.control.modelo import ControlPanelModelo


class TestControlPanelModeloCreacion:
    """Tests de inicializacion del modelo."""

    def test_valores_por_defecto(self):
        """El modelo inicia con valores por defecto."""
        modelo = ControlPanelModelo()

        assert modelo.voltaje == 4.2
        assert modelo.voltaje_minimo == 0.0
        assert modelo.voltaje_maximo == 5.0
        assert modelo.precision == 0.1

    def test_valores_personalizados(self):
        """El modelo acepta valores personalizados."""
        modelo = ControlPanelModelo(
            voltaje=2.5,
            voltaje_minimo=1.0,
            voltaje_maximo=4.0,
            precision=0.5
        )

        assert modelo.voltaje == 2.5
        assert modelo.voltaje_minimo == 1.0
        assert modelo.voltaje_maximo == 4.0
        assert modelo.precision == 0.5


class TestControlPanelModeloSetVoltaje:
    """Tests de set_voltaje con validacion de rango."""

    def test_set_voltaje_en_rango(self):
        """set_voltaje acepta valor en rango."""
        modelo = ControlPanelModelo()

        modelo.set_voltaje(3.5)

        assert modelo.voltaje == 3.5

    def test_set_voltaje_clamp_superior(self):
        """set_voltaje limita al maximo."""
        modelo = ControlPanelModelo(voltaje_maximo=5.0)

        modelo.set_voltaje(10.0)

        assert modelo.voltaje == 5.0

    def test_set_voltaje_clamp_inferior(self):
        """set_voltaje limita al minimo."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0)

        modelo.set_voltaje(-5.0)

        assert modelo.voltaje == 0.0

    def test_set_voltaje_exacto_limites(self):
        """set_voltaje acepta valores exactos en limites."""
        modelo = ControlPanelModelo(voltaje_minimo=1.0, voltaje_maximo=4.0)

        modelo.set_voltaje(1.0)
        assert modelo.voltaje == 1.0

        modelo.set_voltaje(4.0)
        assert modelo.voltaje == 4.0


class TestControlPanelModeloVoltajeNormalizado:
    """Tests de voltaje_normalizado (0.0 a 1.0)."""

    def test_normalizado_minimo(self):
        """Voltaje minimo da 0.0 normalizado."""
        modelo = ControlPanelModelo(voltaje=0.0, voltaje_minimo=0.0, voltaje_maximo=5.0)

        assert modelo.voltaje_normalizado == 0.0

    def test_normalizado_maximo(self):
        """Voltaje maximo da 1.0 normalizado."""
        modelo = ControlPanelModelo(voltaje=5.0, voltaje_minimo=0.0, voltaje_maximo=5.0)

        assert modelo.voltaje_normalizado == 1.0

    def test_normalizado_medio(self):
        """Voltaje medio da 0.5 normalizado."""
        modelo = ControlPanelModelo(voltaje=2.5, voltaje_minimo=0.0, voltaje_maximo=5.0)

        assert modelo.voltaje_normalizado == 0.5

    def test_normalizado_rango_cero(self):
        """Si rango es cero, normalizado es 0.0."""
        modelo = ControlPanelModelo(voltaje=5.0, voltaje_minimo=5.0, voltaje_maximo=5.0)

        assert modelo.voltaje_normalizado == 0.0


class TestControlPanelModeloPasosSlider:
    """Tests de pasos_slider."""

    def test_pasos_slider_defecto(self):
        """Rango 0-5 con precision 0.1 da 50 pasos."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.pasos_slider == 50

    def test_pasos_slider_precision_mayor(self):
        """Rango 0-5 con precision 0.5 da 10 pasos."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.5)

        assert modelo.pasos_slider == 10

    def test_pasos_slider_precision_cero(self):
        """Si precision es cero, pasos es 0."""
        modelo = ControlPanelModelo(precision=0.0)

        assert modelo.pasos_slider == 0

    def test_pasos_slider_rango_personalizado(self):
        """Rango 1-4 con precision 0.1 da 30 pasos."""
        modelo = ControlPanelModelo(voltaje_minimo=1.0, voltaje_maximo=4.0, precision=0.1)

        assert modelo.pasos_slider == 30


class TestControlPanelModeloConversionVoltajePaso:
    """Tests CRITICOS de conversion voltaje <-> paso slider."""

    def test_voltaje_a_paso_minimo(self):
        """Voltaje minimo da paso 0."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.voltaje_a_paso(0.0) == 0

    def test_voltaje_a_paso_maximo(self):
        """Voltaje maximo da paso 50."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.voltaje_a_paso(5.0) == 50

    def test_voltaje_a_paso_medio(self):
        """Voltaje 2.5 da paso 25."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.voltaje_a_paso(2.5) == 25

    def test_voltaje_a_paso_precision_cero(self):
        """Si precision es cero, paso es 0."""
        modelo = ControlPanelModelo(precision=0.0)

        assert modelo.voltaje_a_paso(2.5) == 0

    def test_paso_a_voltaje_minimo(self):
        """Paso 0 da voltaje minimo."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.paso_a_voltaje(0) == 0.0

    def test_paso_a_voltaje_maximo(self):
        """Paso 50 da voltaje maximo."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.paso_a_voltaje(50) == 5.0

    def test_paso_a_voltaje_medio(self):
        """Paso 25 da voltaje 2.5."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        assert modelo.paso_a_voltaje(25) == 2.5


class TestControlPanelModeloConversionBidireccional:
    """Tests de conversion bidireccional (voltaje -> paso -> voltaje)."""

    @pytest.mark.parametrize("voltaje", [0.0, 1.0, 2.5, 3.7, 5.0])
    def test_conversion_ida_vuelta(self, voltaje):
        """La conversion ida y vuelta preserva el valor."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        paso = modelo.voltaje_a_paso(voltaje)
        voltaje_recuperado = modelo.paso_a_voltaje(paso)

        assert voltaje_recuperado == pytest.approx(voltaje, abs=0.1)

    @pytest.mark.parametrize("paso", [0, 10, 25, 40, 50])
    def test_conversion_vuelta_ida(self, paso):
        """La conversion vuelta e ida preserva el valor."""
        modelo = ControlPanelModelo(voltaje_minimo=0.0, voltaje_maximo=5.0, precision=0.1)

        voltaje = modelo.paso_a_voltaje(paso)
        paso_recuperado = modelo.voltaje_a_paso(voltaje)

        assert paso_recuperado == paso

    def test_conversion_rango_personalizado(self):
        """Conversion funciona con rango personalizado."""
        modelo = ControlPanelModelo(voltaje_minimo=1.0, voltaje_maximo=4.0, precision=0.1)

        # 2.5V en rango 1-4 -> paso 15 de 30
        paso = modelo.voltaje_a_paso(2.5)
        assert paso == 15

        voltaje = modelo.paso_a_voltaje(15)
        assert voltaje == 2.5
