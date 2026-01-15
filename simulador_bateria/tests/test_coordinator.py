"""Tests para SimuladorCoordinator.

COMPLEJO: Verifica conexiones de signals entre componentes.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.coordinator import SimuladorCoordinator
from app.configuracion.config import ConfigSimuladorBateria
from app.dominio.generador_bateria import GeneradorBateria
from app.dominio.estado_bateria import EstadoBateria


@pytest.fixture
def config():
    """Configuracion para tests."""
    return ConfigSimuladorBateria(
        host="192.168.1.100",
        puerto=11000,
        intervalo_envio_ms=100,
        voltaje_minimo=0.0,
        voltaje_maximo=5.0,
        voltaje_inicial=2.5
    )


@pytest.fixture
def generador(config, qtbot):
    """GeneradorBateria real para tests."""
    return GeneradorBateria(config)


@pytest.fixture
def mock_ctrl_estado():
    """Mock de PanelEstadoControlador."""
    mock = MagicMock()
    mock.actualizar_voltaje = MagicMock()
    mock.actualizar_conexion = MagicMock()
    mock.registrar_envio_exitoso = MagicMock()
    return mock


@pytest.fixture
def mock_ctrl_control():
    """Mock de ControlPanelControlador."""
    mock = MagicMock()
    mock.voltaje_cambiado = MagicMock()
    mock.voltaje_cambiado.connect = MagicMock()
    return mock


@pytest.fixture
def mock_ctrl_conexion():
    """Mock de ConexionPanelControlador."""
    mock = MagicMock()
    mock.conectar_solicitado = MagicMock()
    mock.conectar_solicitado.connect = MagicMock()
    mock.desconectar_solicitado = MagicMock()
    mock.desconectar_solicitado.connect = MagicMock()
    mock.ip = "192.168.1.100"
    mock.puerto = 11000
    return mock


@pytest.fixture
def coordinator(generador, mock_ctrl_estado, mock_ctrl_control, mock_ctrl_conexion, qtbot):
    """Coordinator con componentes mockeados."""
    return SimuladorCoordinator(
        generador=generador,
        ctrl_estado=mock_ctrl_estado,
        ctrl_control=mock_ctrl_control,
        ctrl_conexion=mock_ctrl_conexion
    )


class TestSimuladorCoordinatorCreacion:
    """Tests de inicializacion del coordinator."""

    def test_creacion_guarda_referencias(
        self, generador, mock_ctrl_estado, mock_ctrl_control, mock_ctrl_conexion, qtbot
    ):
        """Coordinator guarda referencias a componentes."""
        coord = SimuladorCoordinator(
            generador=generador,
            ctrl_estado=mock_ctrl_estado,
            ctrl_control=mock_ctrl_control,
            ctrl_conexion=mock_ctrl_conexion
        )

        assert coord._generador is generador
        assert coord._ctrl_estado is mock_ctrl_estado
        assert coord._ctrl_control is mock_ctrl_control
        assert coord._ctrl_conexion is mock_ctrl_conexion

    def test_creacion_servicio_none(self, coordinator):
        """Coordinator inicia sin servicio."""
        assert coordinator._servicio is None

    def test_creacion_conecta_signals_control(self, mock_ctrl_control, coordinator):
        """Coordinator conecta voltaje_cambiado del control."""
        mock_ctrl_control.voltaje_cambiado.connect.assert_called_once()

    def test_creacion_conecta_signals_conexion(self, mock_ctrl_conexion, coordinator):
        """Coordinator conecta signals del panel de conexion."""
        mock_ctrl_conexion.conectar_solicitado.connect.assert_called_once()
        mock_ctrl_conexion.desconectar_solicitado.connect.assert_called_once()


class TestSimuladorCoordinatorGenerador:
    """Tests de conexion generador -> ctrl_estado."""

    def test_generador_valor_actualiza_estado(
        self, coordinator, mock_ctrl_estado, generador, qtbot
    ):
        """valor_generado del generador actualiza ctrl_estado."""
        # Generar un valor
        generador.generar_valor()
        qtbot.wait(50)

        # Verificar que se llamo actualizar_voltaje
        mock_ctrl_estado.actualizar_voltaje.assert_called()

    def test_generador_pasa_voltaje_correcto(
        self, coordinator, mock_ctrl_estado, generador, qtbot
    ):
        """El voltaje correcto llega a ctrl_estado."""
        generador.set_voltaje(3.5)
        generador.generar_valor()
        qtbot.wait(50)

        # El ultimo call debe tener voltaje 3.5
        args = mock_ctrl_estado.actualizar_voltaje.call_args
        assert args[0][0] == 3.5


class TestSimuladorCoordinatorServicio:
    """Tests de set_servicio y conexiones."""

    def test_set_servicio_guarda_referencia(self, coordinator):
        """set_servicio guarda referencia al servicio."""
        mock_servicio = MagicMock()
        mock_servicio.servicio_iniciado = MagicMock()
        mock_servicio.servicio_iniciado.connect = MagicMock()
        mock_servicio.servicio_detenido = MagicMock()
        mock_servicio.servicio_detenido.connect = MagicMock()
        mock_servicio.envio_exitoso = MagicMock()
        mock_servicio.envio_exitoso.connect = MagicMock()

        coordinator.set_servicio(mock_servicio)

        assert coordinator._servicio is mock_servicio

    def test_set_servicio_conecta_iniciado(self, coordinator):
        """set_servicio conecta servicio_iniciado."""
        mock_servicio = MagicMock()
        mock_servicio.servicio_iniciado = MagicMock()
        mock_servicio.servicio_iniciado.connect = MagicMock()
        mock_servicio.servicio_detenido = MagicMock()
        mock_servicio.servicio_detenido.connect = MagicMock()
        mock_servicio.envio_exitoso = MagicMock()
        mock_servicio.envio_exitoso.connect = MagicMock()

        coordinator.set_servicio(mock_servicio)

        mock_servicio.servicio_iniciado.connect.assert_called_once()

    def test_set_servicio_conecta_detenido(self, coordinator):
        """set_servicio conecta servicio_detenido."""
        mock_servicio = MagicMock()
        mock_servicio.servicio_iniciado = MagicMock()
        mock_servicio.servicio_iniciado.connect = MagicMock()
        mock_servicio.servicio_detenido = MagicMock()
        mock_servicio.servicio_detenido.connect = MagicMock()
        mock_servicio.envio_exitoso = MagicMock()
        mock_servicio.envio_exitoso.connect = MagicMock()

        coordinator.set_servicio(mock_servicio)

        mock_servicio.servicio_detenido.connect.assert_called_once()

    def test_set_servicio_conecta_envio_exitoso(self, coordinator):
        """set_servicio conecta envio_exitoso."""
        mock_servicio = MagicMock()
        mock_servicio.servicio_iniciado = MagicMock()
        mock_servicio.servicio_iniciado.connect = MagicMock()
        mock_servicio.servicio_detenido = MagicMock()
        mock_servicio.servicio_detenido.connect = MagicMock()
        mock_servicio.envio_exitoso = MagicMock()
        mock_servicio.envio_exitoso.connect = MagicMock()

        coordinator.set_servicio(mock_servicio)

        mock_servicio.envio_exitoso.connect.assert_called_once()


class TestSimuladorCoordinatorProperties:
    """Tests de propiedades de configuracion."""

    def test_ip_configurada(self, coordinator, mock_ctrl_conexion):
        """ip_configurada retorna IP del ctrl_conexion."""
        mock_ctrl_conexion.ip = "10.0.0.1"

        assert coordinator.ip_configurada == "10.0.0.1"

    def test_puerto_configurado(self, coordinator, mock_ctrl_conexion):
        """puerto_configurado retorna puerto del ctrl_conexion."""
        mock_ctrl_conexion.puerto = 9999

        assert coordinator.puerto_configurado == 9999


class TestSimuladorCoordinatorSignals:
    """Tests de signals propios del coordinator."""

    def test_tiene_signal_conexion_solicitada(self, coordinator):
        """Coordinator tiene signal conexion_solicitada."""
        assert hasattr(coordinator, 'conexion_solicitada')

    def test_tiene_signal_desconexion_solicitada(self, coordinator):
        """Coordinator tiene signal desconexion_solicitada."""
        assert hasattr(coordinator, 'desconexion_solicitada')
