"""Tests unitarios para VariacionSenoidal."""
import math
import pytest

from app.dominio import VariacionSenoidal


class TestVariacionSenoidalCreacion:
    """Tests de creación de VariacionSenoidal."""

    def test_crear_variacion_senoidal(self):
        """Verifica creación con parámetros básicos."""
        variacion = VariacionSenoidal(
            temperatura_base=20.0,
            amplitud=5.0,
            periodo_segundos=60.0
        )

        assert variacion.temperatura_base == pytest.approx(20.0)
        assert variacion.amplitud == pytest.approx(5.0)
        assert variacion.periodo_segundos == pytest.approx(60.0)

    def test_temperatura_maxima_property(self):
        """Verifica cálculo de temperatura máxima."""
        variacion = VariacionSenoidal(
            temperatura_base=20.0,
            amplitud=5.0,
            periodo_segundos=60.0
        )

        assert variacion.temperatura_maxima == pytest.approx(25.0)

    def test_temperatura_minima_property(self):
        """Verifica cálculo de temperatura mínima."""
        variacion = VariacionSenoidal(
            temperatura_base=20.0,
            amplitud=5.0,
            periodo_segundos=60.0
        )

        assert variacion.temperatura_minima == pytest.approx(15.0)


class TestVariacionSenoidalCalculoTemperatura:
    """Tests del método calcular_temperatura()."""

    @pytest.fixture
    def variacion(self):
        """Fixture con variación estándar para tests."""
        return VariacionSenoidal(
            temperatura_base=20.0,
            amplitud=5.0,
            periodo_segundos=60.0
        )

    def test_temperatura_en_tiempo_cero(self, variacion):
        """En t=0, sin(0)=0, debe retornar temperatura base."""
        resultado = variacion.calcular_temperatura(0.0)

        assert resultado == pytest.approx(20.0)

    def test_temperatura_en_cuarto_periodo(self, variacion):
        """En t=P/4, sin(π/2)=1, debe retornar base + amplitud."""
        tiempo = variacion.periodo_segundos / 4  # 15 segundos

        resultado = variacion.calcular_temperatura(tiempo)

        assert resultado == pytest.approx(25.0)

    def test_temperatura_en_medio_periodo(self, variacion):
        """En t=P/2, sin(π)=0, debe retornar temperatura base."""
        tiempo = variacion.periodo_segundos / 2  # 30 segundos

        resultado = variacion.calcular_temperatura(tiempo)

        assert resultado == pytest.approx(20.0)

    def test_temperatura_en_tres_cuartos_periodo(self, variacion):
        """En t=3P/4, sin(3π/2)=-1, debe retornar base - amplitud."""
        tiempo = 3 * variacion.periodo_segundos / 4  # 45 segundos

        resultado = variacion.calcular_temperatura(tiempo)

        assert resultado == pytest.approx(15.0)

    def test_temperatura_en_periodo_completo(self, variacion):
        """En t=P, sin(2π)=0, debe retornar temperatura base."""
        tiempo = variacion.periodo_segundos  # 60 segundos

        resultado = variacion.calcular_temperatura(tiempo)

        assert resultado == pytest.approx(20.0)

    def test_periodicidad(self, variacion):
        """Verifica que T(t) == T(t + P) para cualquier t."""
        tiempo_base = 17.5  # tiempo arbitrario

        temp_t = variacion.calcular_temperatura(tiempo_base)
        temp_t_plus_p = variacion.calcular_temperatura(
            tiempo_base + variacion.periodo_segundos
        )

        assert temp_t == pytest.approx(temp_t_plus_p)

    def test_rango_temperatura(self, variacion):
        """Verifica que la temperatura siempre está en rango [base-A, base+A]."""
        for i in range(100):
            tiempo = i * variacion.periodo_segundos / 100

            resultado = variacion.calcular_temperatura(tiempo)

            assert variacion.temperatura_minima <= resultado <= variacion.temperatura_maxima


class TestVariacionSenoidalCasosEspeciales:
    """Tests de casos especiales y edge cases."""

    def test_amplitud_cero(self):
        """Con amplitud 0, siempre retorna temperatura base."""
        variacion = VariacionSenoidal(
            temperatura_base=25.0,
            amplitud=0.0,
            periodo_segundos=60.0
        )

        for tiempo in [0, 15, 30, 45, 60]:
            assert variacion.calcular_temperatura(tiempo) == pytest.approx(25.0)

    def test_periodo_largo_ciclo_dia_noche(self):
        """Simula ciclo día/noche con período de 24 horas."""
        variacion = VariacionSenoidal(
            temperatura_base=20.0,
            amplitud=10.0,
            periodo_segundos=86400.0  # 24 horas
        )

        # Medianoche (t=0): temperatura base
        assert variacion.calcular_temperatura(0) == pytest.approx(20.0)

        # 6 AM (t=6h): temperatura máxima
        assert variacion.calcular_temperatura(6 * 3600) == pytest.approx(30.0)

        # Mediodía (t=12h): temperatura base
        assert variacion.calcular_temperatura(12 * 3600) == pytest.approx(20.0)

        # 6 PM (t=18h): temperatura mínima
        assert variacion.calcular_temperatura(18 * 3600) == pytest.approx(10.0)

    def test_temperatura_negativa(self):
        """Verifica funcionamiento con temperaturas negativas."""
        variacion = VariacionSenoidal(
            temperatura_base=-5.0,
            amplitud=3.0,
            periodo_segundos=60.0
        )

        assert variacion.temperatura_maxima == -2.0
        assert variacion.temperatura_minima == -8.0
        assert variacion.calcular_temperatura(0) == pytest.approx(-5.0)
