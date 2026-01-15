"""Tests para PanelEstadoControlador.

Cubre: actualizar_voltaje, actualizar_conexion, registrar_envios, signals.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.presentacion.paneles.estado.modelo import EstadoBateriaPanelModelo
from app.presentacion.paneles.estado.controlador import PanelEstadoControlador


@pytest.fixture
def mock_vista():
    """Mock de PanelEstadoVista para evitar crear UI."""
    with patch('app.presentacion.paneles.estado.controlador.PanelEstadoVista') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def modelo():
    """Modelo de estado para tests."""
    return EstadoBateriaPanelModelo()


@pytest.fixture
def controlador(modelo, mock_vista, qtbot):
    """Controlador con modelo y vista mockeada."""
    ctrl = PanelEstadoControlador(modelo=modelo, vista=mock_vista)
    return ctrl


class TestPanelEstadoControladorCreacion:
    """Tests de inicializacion del controlador."""

    def test_creacion_con_modelo_y_vista(self, modelo, mock_vista, qtbot):
        """Controlador acepta modelo y vista."""
        ctrl = PanelEstadoControlador(modelo=modelo, vista=mock_vista)

        assert ctrl.modelo is modelo
        assert ctrl.vista is mock_vista

    def test_creacion_crea_modelo_por_defecto(self, mock_vista, qtbot):
        """Controlador crea modelo si no se provee."""
        ctrl = PanelEstadoControlador(vista=mock_vista)

        assert ctrl.modelo is not None
        assert isinstance(ctrl.modelo, EstadoBateriaPanelModelo)


class TestPanelEstadoControladorActualizarVoltaje:
    """Tests de actualizar_voltaje."""

    def test_actualizar_voltaje_actualiza_modelo(self, controlador):
        """actualizar_voltaje cambia valor en modelo."""
        controlador.actualizar_voltaje(3.5)

        assert controlador.voltaje_actual == 3.5

    def test_actualizar_voltaje_actualiza_porcentaje(self, controlador):
        """actualizar_voltaje recalcula porcentaje."""
        controlador.actualizar_voltaje(2.5)

        assert controlador.porcentaje == 50.0

    def test_actualizar_voltaje_actualiza_vista(self, controlador, mock_vista):
        """actualizar_voltaje llama actualizar en vista."""
        controlador.actualizar_voltaje(3.0)

        mock_vista.actualizar.assert_called()

    def test_actualizar_voltaje_emite_signal(self, controlador, qtbot):
        """actualizar_voltaje emite voltaje_actualizado."""
        with qtbot.waitSignal(controlador.voltaje_actualizado, timeout=1000) as blocker:
            controlador.actualizar_voltaje(4.0)

        assert blocker.args[0] == 4.0


class TestPanelEstadoControladorActualizarConexion:
    """Tests de actualizar_conexion."""

    def test_actualizar_conexion_true(self, controlador):
        """actualizar_conexion establece True."""
        controlador.actualizar_conexion(True)

        assert controlador.conectado is True

    def test_actualizar_conexion_false(self, controlador):
        """actualizar_conexion establece False."""
        controlador.actualizar_conexion(True)
        controlador.actualizar_conexion(False)

        assert controlador.conectado is False

    def test_actualizar_conexion_actualiza_vista(self, controlador, mock_vista):
        """actualizar_conexion llama actualizar en vista."""
        controlador.actualizar_conexion(True)

        mock_vista.actualizar.assert_called()

    def test_actualizar_conexion_emite_signal(self, controlador, qtbot):
        """actualizar_conexion emite conexion_actualizada."""
        with qtbot.waitSignal(controlador.conexion_actualizada, timeout=1000) as blocker:
            controlador.actualizar_conexion(True)

        assert blocker.args[0] is True


class TestPanelEstadoControladorContadores:
    """Tests de registrar_envio_exitoso/fallido."""

    def test_registrar_envio_exitoso(self, controlador):
        """registrar_envio_exitoso incrementa contador."""
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_exitoso()

        assert controlador.envios_exitosos == 2
        assert controlador.envios_fallidos == 0

    def test_registrar_envio_fallido(self, controlador):
        """registrar_envio_fallido incrementa contador."""
        controlador.registrar_envio_fallido()

        assert controlador.envios_fallidos == 1
        assert controlador.envios_exitosos == 0

    def test_registrar_envio_emite_signal_exitoso(self, controlador, qtbot):
        """registrar_envio_exitoso emite contadores_actualizados."""
        with qtbot.waitSignal(controlador.contadores_actualizados, timeout=1000) as blocker:
            controlador.registrar_envio_exitoso()

        assert blocker.args == [1, 0]  # exitosos, fallidos

    def test_registrar_envio_emite_signal_fallido(self, controlador, qtbot):
        """registrar_envio_fallido emite contadores_actualizados."""
        with qtbot.waitSignal(controlador.contadores_actualizados, timeout=1000) as blocker:
            controlador.registrar_envio_fallido()

        assert blocker.args == [0, 1]  # exitosos, fallidos

    def test_reiniciar_contadores(self, controlador):
        """reiniciar_contadores pone ambos en cero."""
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_fallido()

        controlador.reiniciar_contadores()

        assert controlador.envios_exitosos == 0
        assert controlador.envios_fallidos == 0

    def test_reiniciar_contadores_emite_signal(self, controlador, qtbot):
        """reiniciar_contadores emite contadores_actualizados(0, 0)."""
        controlador.registrar_envio_exitoso()

        with qtbot.waitSignal(controlador.contadores_actualizados, timeout=1000) as blocker:
            controlador.reiniciar_contadores()

        assert blocker.args == [0, 0]


class TestPanelEstadoControladorProperties:
    """Tests de propiedades de solo lectura."""

    def test_voltaje_actual(self, controlador):
        """voltaje_actual retorna valor del modelo."""
        controlador.actualizar_voltaje(3.7)

        assert controlador.voltaje_actual == 3.7

    def test_porcentaje(self, controlador):
        """porcentaje retorna valor del modelo."""
        controlador.actualizar_voltaje(2.5)

        assert controlador.porcentaje == 50.0

    def test_conectado(self, controlador):
        """conectado retorna valor del modelo."""
        controlador.actualizar_conexion(True)

        assert controlador.conectado is True

    def test_envios_exitosos(self, controlador):
        """envios_exitosos retorna valor del modelo."""
        controlador.registrar_envio_exitoso()
        controlador.registrar_envio_exitoso()

        assert controlador.envios_exitosos == 2

    def test_envios_fallidos(self, controlador):
        """envios_fallidos retorna valor del modelo."""
        controlador.registrar_envio_fallido()

        assert controlador.envios_fallidos == 1
