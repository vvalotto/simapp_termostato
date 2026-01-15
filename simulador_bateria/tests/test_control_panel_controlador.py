"""Tests para ControlPanelControlador.

Cubre: slider_cambiado callback, voltaje_cambiado signal, set_voltaje.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.presentacion.paneles.control.modelo import ControlPanelModelo
from app.presentacion.paneles.control.controlador import ControlPanelControlador


@pytest.fixture
def mock_vista():
    """Mock de ControlPanelVista para evitar crear UI."""
    with patch('app.presentacion.paneles.control.controlador.ControlPanelVista') as mock_class:
        mock_instance = MagicMock()
        mock_instance.slider_cambiado = MagicMock()
        mock_instance.slider_cambiado.connect = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def modelo():
    """Modelo de control para tests."""
    return ControlPanelModelo(
        voltaje=2.5,
        voltaje_minimo=0.0,
        voltaje_maximo=5.0,
        precision=0.1
    )


@pytest.fixture
def controlador(modelo, mock_vista, qtbot):
    """Controlador con modelo y vista mockeada."""
    ctrl = ControlPanelControlador(modelo=modelo, vista=mock_vista)
    return ctrl


class TestControlPanelControladorCreacion:
    """Tests de inicializacion del controlador."""

    def test_creacion_con_modelo_y_vista(self, modelo, mock_vista, qtbot):
        """Controlador acepta modelo y vista."""
        ctrl = ControlPanelControlador(modelo=modelo, vista=mock_vista)

        assert ctrl.modelo is modelo
        assert ctrl.vista is mock_vista

    def test_creacion_crea_modelo_por_defecto(self, mock_vista, qtbot):
        """Controlador crea modelo si no se provee."""
        ctrl = ControlPanelControlador(vista=mock_vista)

        assert ctrl.modelo is not None
        assert isinstance(ctrl.modelo, ControlPanelModelo)

    def test_creacion_conecta_signals(self, modelo, mock_vista, qtbot):
        """Controlador conecta signal slider_cambiado."""
        ctrl = ControlPanelControlador(modelo=modelo, vista=mock_vista)

        mock_vista.slider_cambiado.connect.assert_called_once()

    def test_creacion_actualiza_vista(self, modelo, mock_vista, qtbot):
        """Controlador actualiza vista en inicializacion."""
        ctrl = ControlPanelControlador(modelo=modelo, vista=mock_vista)

        mock_vista.actualizar.assert_called()


class TestControlPanelControladorSliderCallback:
    """Tests de _on_slider_cambiado callback."""

    def test_slider_cambiado_actualiza_modelo(self, controlador):
        """Cambio de slider actualiza voltaje en modelo."""
        # Simular paso 30 -> voltaje 3.0
        controlador._on_slider_cambiado(30)

        assert controlador.voltaje == 3.0

    def test_slider_cambiado_actualiza_vista(self, controlador, mock_vista):
        """Cambio de slider llama actualizar en vista."""
        mock_vista.actualizar.reset_mock()

        controlador._on_slider_cambiado(25)

        mock_vista.actualizar.assert_called()

    def test_slider_cambiado_emite_signal(self, controlador, qtbot):
        """Cambio de slider emite voltaje_cambiado."""
        with qtbot.waitSignal(controlador.voltaje_cambiado, timeout=1000) as blocker:
            controlador._on_slider_cambiado(40)

        assert blocker.args[0] == 4.0


class TestControlPanelControladorSetVoltaje:
    """Tests de set_voltaje desde codigo externo."""

    def test_set_voltaje_actualiza_modelo(self, controlador):
        """set_voltaje cambia valor en modelo."""
        controlador.set_voltaje(3.5)

        assert controlador.voltaje == 3.5

    def test_set_voltaje_actualiza_vista(self, controlador, mock_vista):
        """set_voltaje llama actualizar en vista."""
        mock_vista.actualizar.reset_mock()

        controlador.set_voltaje(4.0)

        mock_vista.actualizar.assert_called()

    def test_set_voltaje_clamp_superior(self, controlador):
        """set_voltaje limita al maximo."""
        controlador.set_voltaje(10.0)

        assert controlador.voltaje == 5.0

    def test_set_voltaje_clamp_inferior(self, controlador):
        """set_voltaje limita al minimo."""
        controlador.set_voltaje(-5.0)

        assert controlador.voltaje == 0.0


class TestControlPanelControladorProperties:
    """Tests de propiedades de solo lectura."""

    def test_voltaje(self, controlador):
        """voltaje retorna valor del modelo."""
        controlador.set_voltaje(3.7)

        assert controlador.voltaje == 3.7

    def test_voltaje_minimo(self, controlador):
        """voltaje_minimo retorna valor del modelo."""
        assert controlador.voltaje_minimo == 0.0

    def test_voltaje_maximo(self, controlador):
        """voltaje_maximo retorna valor del modelo."""
        assert controlador.voltaje_maximo == 5.0
