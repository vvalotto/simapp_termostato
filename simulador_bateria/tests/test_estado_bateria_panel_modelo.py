"""Tests para EstadoBateriaPanelModelo.

Cubre: actualizar_voltaje, calcular_porcentaje, contadores, tasa_exito.
"""

import pytest

from app.presentacion.paneles.estado.modelo import EstadoBateriaPanelModelo


class TestEstadoBateriaPanelModeloCreacion:
    """Tests de inicializacion del modelo."""

    def test_valores_por_defecto(self):
        """El modelo inicia con valores por defecto."""
        modelo = EstadoBateriaPanelModelo()

        assert modelo.voltaje_actual == 0.0
        assert modelo.porcentaje == 0.0
        assert modelo.conectado is False
        assert modelo.envios_exitosos == 0
        assert modelo.envios_fallidos == 0

    def test_valores_personalizados(self):
        """El modelo acepta valores personalizados."""
        modelo = EstadoBateriaPanelModelo(
            voltaje_actual=2.5,
            porcentaje=50.0,
            conectado=True,
            envios_exitosos=10,
            envios_fallidos=2
        )

        assert modelo.voltaje_actual == 2.5
        assert modelo.porcentaje == 50.0
        assert modelo.conectado is True
        assert modelo.envios_exitosos == 10
        assert modelo.envios_fallidos == 2

    def test_rango_voltaje_por_defecto(self):
        """El rango de voltaje por defecto es 0.0-5.0."""
        modelo = EstadoBateriaPanelModelo()

        assert modelo._voltaje_min == 0.0
        assert modelo._voltaje_max == 5.0


class TestEstadoBateriaPanelModeloVoltaje:
    """Tests de actualizacion de voltaje y porcentaje."""

    def test_actualizar_voltaje_medio(self):
        """actualizar_voltaje con 2.5V da 50%."""
        modelo = EstadoBateriaPanelModelo()

        modelo.actualizar_voltaje(2.5)

        assert modelo.voltaje_actual == 2.5
        assert modelo.porcentaje == 50.0

    def test_actualizar_voltaje_minimo(self):
        """actualizar_voltaje con 0V da 0%."""
        modelo = EstadoBateriaPanelModelo()

        modelo.actualizar_voltaje(0.0)

        assert modelo.voltaje_actual == 0.0
        assert modelo.porcentaje == 0.0

    def test_actualizar_voltaje_maximo(self):
        """actualizar_voltaje con 5V da 100%."""
        modelo = EstadoBateriaPanelModelo()

        modelo.actualizar_voltaje(5.0)

        assert modelo.voltaje_actual == 5.0
        assert modelo.porcentaje == 100.0

    def test_porcentaje_clamp_superior(self):
        """Porcentaje no excede 100% con voltaje alto."""
        modelo = EstadoBateriaPanelModelo()

        modelo.actualizar_voltaje(10.0)

        assert modelo.porcentaje == 100.0

    def test_porcentaje_clamp_inferior(self):
        """Porcentaje no baja de 0% con voltaje negativo."""
        modelo = EstadoBateriaPanelModelo()

        modelo.actualizar_voltaje(-5.0)

        assert modelo.porcentaje == 0.0

    def test_porcentaje_rango_cero(self):
        """Si rango es cero, porcentaje es 0."""
        modelo = EstadoBateriaPanelModelo(_voltaje_min=5.0, _voltaje_max=5.0)

        modelo.actualizar_voltaje(5.0)

        assert modelo.porcentaje == 0.0


class TestEstadoBateriaPanelModeloContadores:
    """Tests de contadores de envios."""

    def test_incrementar_exitosos(self):
        """incrementar_exitosos aumenta contador."""
        modelo = EstadoBateriaPanelModelo()

        modelo.incrementar_exitosos()
        modelo.incrementar_exitosos()

        assert modelo.envios_exitosos == 2
        assert modelo.envios_fallidos == 0

    def test_incrementar_fallidos(self):
        """incrementar_fallidos aumenta contador."""
        modelo = EstadoBateriaPanelModelo()

        modelo.incrementar_fallidos()

        assert modelo.envios_fallidos == 1
        assert modelo.envios_exitosos == 0

    def test_reiniciar_contadores(self):
        """reiniciar_contadores pone ambos en cero."""
        modelo = EstadoBateriaPanelModelo(envios_exitosos=10, envios_fallidos=5)

        modelo.reiniciar_contadores()

        assert modelo.envios_exitosos == 0
        assert modelo.envios_fallidos == 0

    def test_total_envios(self):
        """total_envios suma exitosos y fallidos."""
        modelo = EstadoBateriaPanelModelo(envios_exitosos=10, envios_fallidos=3)

        assert modelo.total_envios == 13


class TestEstadoBateriaPanelModeloTasaExito:
    """Tests de tasa de exito."""

    def test_tasa_exito_sin_envios(self):
        """tasa_exito es 0.0 sin envios."""
        modelo = EstadoBateriaPanelModelo()

        assert modelo.tasa_exito == 0.0

    def test_tasa_exito_todos_exitosos(self):
        """tasa_exito es 1.0 si todos son exitosos."""
        modelo = EstadoBateriaPanelModelo(envios_exitosos=10, envios_fallidos=0)

        assert modelo.tasa_exito == 1.0

    def test_tasa_exito_todos_fallidos(self):
        """tasa_exito es 0.0 si todos fallan."""
        modelo = EstadoBateriaPanelModelo(envios_exitosos=0, envios_fallidos=5)

        assert modelo.tasa_exito == 0.0

    def test_tasa_exito_mixto(self):
        """tasa_exito calcula proporcion correcta."""
        modelo = EstadoBateriaPanelModelo(envios_exitosos=8, envios_fallidos=2)

        assert modelo.tasa_exito == 0.8

    def test_tasa_exito_precision(self):
        """tasa_exito mantiene precision decimal."""
        modelo = EstadoBateriaPanelModelo(envios_exitosos=1, envios_fallidos=2)

        assert modelo.tasa_exito == pytest.approx(0.333, abs=0.01)
