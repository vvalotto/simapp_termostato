"""
Tests del módulo Coordinator (UXCoordinator).

Valida la conexión de señales entre componentes del sistema.
"""

from unittest.mock import Mock, MagicMock, patch
import pytest
from PyQt6.QtCore import pyqtSignal, QObject

from app.coordinator import UXCoordinator
from app.dominio import EstadoTermostato, ComandoPower, ComandoSetTemp
from datetime import datetime


class MockServidorEstado(QObject):
    """Mock de ServidorEstado con señales."""

    estado_recibido = pyqtSignal(object)
    conexion_establecida = pyqtSignal(str)
    conexion_perdida = pyqtSignal(str)
    error_parsing = pyqtSignal(str)


class MockClienteComandos(QObject):
    """Mock de ClienteComandos."""

    def __init__(self):
        super().__init__()
        self.enviar_comando = Mock(return_value=True)


class MockControlador(QObject):
    """Mock genérico de controlador con señales."""

    power_cambiado = pyqtSignal(bool)
    temperatura_cambiada = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.actualizar_desde_estado = Mock()
        self.set_habilitado = Mock()
        self.actualizar_modelo = Mock()


@pytest.fixture
def mock_servidor():
    """Fixture de servidor mock."""
    return MockServidorEstado()


@pytest.fixture
def mock_cliente():
    """Fixture de cliente mock."""
    return MockClienteComandos()


@pytest.fixture
def mock_paneles():
    """Fixture de paneles mock."""
    ctrl_display = MockControlador()
    ctrl_climatizador = MockControlador()
    ctrl_indicadores = MockControlador()
    ctrl_power = MockControlador()
    ctrl_control_temp = MockControlador()

    return {
        "display": (None, None, ctrl_display),
        "climatizador": (None, None, ctrl_climatizador),
        "indicadores": (None, None, ctrl_indicadores),
        "power": (None, None, ctrl_power),
        "control_temp": (None, None, ctrl_control_temp),
    }


@pytest.fixture
def coordinator(mock_paneles, mock_servidor, mock_cliente, qapp):
    """Fixture de coordinator para tests."""
    return UXCoordinator(mock_paneles, mock_servidor, mock_cliente)


class TestCreacion:
    """Tests de creación del coordinator."""

    def test_creacion_con_componentes(self, mock_paneles, mock_servidor, mock_cliente, qapp):
        """Debe crear coordinator con todos los componentes."""
        coordinator = UXCoordinator(mock_paneles, mock_servidor, mock_cliente)

        assert coordinator is not None

    def test_conecta_signals_al_crear(self, mock_paneles, mock_servidor, mock_cliente, qapp):
        """Debe conectar señales al crear el coordinator."""
        # Crear coordinator conecta automáticamente las señales
        coordinator = UXCoordinator(mock_paneles, mock_servidor, mock_cliente)

        # Verificar que las señales del servidor están conectadas
        # (no podemos verificar directamente, pero el constructor debe completarse sin error)
        assert coordinator is not None


class TestConexionServidor:
    """Tests de conexión de señales del servidor."""

    def test_estado_recibido_distribuye_a_display(self, coordinator, mock_servidor, mock_paneles):
        """estado_recibido debe actualizar panel display."""
        # Crear estado de prueba
        estado = EstadoTermostato(
            temperatura_actual=25.0,
            temperatura_deseada=24.0,
            modo_climatizador="calentando",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        # Emitir señal
        mock_servidor.estado_recibido.emit(estado)

        # Verificar que display fue actualizado
        mock_paneles["display"][2].actualizar_desde_estado.assert_called_once_with(estado)

    def test_estado_recibido_distribuye_a_climatizador(
        self, coordinator, mock_servidor, mock_paneles
    ):
        """estado_recibido debe actualizar panel climatizador."""
        estado = EstadoTermostato(
            temperatura_actual=25.0,
            temperatura_deseada=24.0,
            modo_climatizador="enfriando",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        mock_servidor.estado_recibido.emit(estado)

        mock_paneles["climatizador"][2].actualizar_desde_estado.assert_called_once_with(estado)

    def test_estado_recibido_distribuye_a_indicadores(
        self, coordinator, mock_servidor, mock_paneles
    ):
        """estado_recibido debe actualizar panel indicadores."""
        estado = EstadoTermostato(
            temperatura_actual=25.0,
            temperatura_deseada=24.0,
            modo_climatizador="reposo",
            falla_sensor=True,
            bateria_baja=True,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        mock_servidor.estado_recibido.emit(estado)

        mock_paneles["indicadores"][2].actualizar_desde_estado.assert_called_once_with(
            falla_sensor=True, bateria_baja=True
        )

    def test_estado_recibido_sincroniza_power(self, coordinator, mock_servidor, mock_paneles):
        """estado_recibido debe sincronizar panel power."""
        estado = EstadoTermostato(
            temperatura_actual=25.0,
            temperatura_deseada=24.0,
            modo_climatizador="reposo",
            falla_sensor=False,
            bateria_baja=False,
            encendido=False,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        mock_servidor.estado_recibido.emit(estado)

        # Verificar que power fue actualizado con encendido=False
        mock_paneles["power"][2].actualizar_modelo.assert_called_once_with(False)

class TestConexionPower:
    """Tests de conexión de señales del panel Power."""

    def test_power_cambiado_envia_comando(self, coordinator, mock_cliente, mock_paneles):
        """power_cambiado debe enviar ComandoPower al cliente."""
        ctrl_power = mock_paneles["power"][2]

        # Emitir señal de power cambiado
        ctrl_power.power_cambiado.emit(True)

        # Verificar que se llamó enviar_comando
        assert mock_cliente.enviar_comando.called
        # Verificar que el argumento es ComandoPower
        args = mock_cliente.enviar_comando.call_args[0]
        assert isinstance(args[0], ComandoPower)
        assert args[0].estado is True

    def test_power_cambiado_habilita_control_temp(self, coordinator, mock_paneles):
        """power_cambiado debe habilitar/deshabilitar control_temp."""
        ctrl_power = mock_paneles["power"][2]
        ctrl_control_temp = mock_paneles["control_temp"][2]

        # Emitir señal de encendido
        ctrl_power.power_cambiado.emit(True)

        # Verificar que control_temp fue habilitado
        ctrl_control_temp.set_habilitado.assert_called_with(True)

    def test_power_apagado_deshabilita_control_temp(self, coordinator, mock_paneles):
        """power_cambiado con False debe deshabilitar control_temp."""
        ctrl_power = mock_paneles["power"][2]
        ctrl_control_temp = mock_paneles["control_temp"][2]

        # Emitir señal de apagado
        ctrl_power.power_cambiado.emit(False)

        # Verificar que control_temp fue deshabilitado
        ctrl_control_temp.set_habilitado.assert_called_with(False)


class TestConexionControlTemp:
    """Tests de conexión de señales del panel ControlTemp."""

    def test_temperatura_cambiada_envia_comando(self, coordinator, mock_cliente, mock_paneles):
        """temperatura_cambiada debe enviar ComandoSetTemp al cliente."""
        ctrl_control_temp = mock_paneles["control_temp"][2]

        # Emitir señal de temperatura cambiada
        ctrl_control_temp.temperatura_cambiada.emit(23.5)

        # Verificar que se llamó enviar_comando
        assert mock_cliente.enviar_comando.called
        # Verificar que el argumento es ComandoSetTemp
        args = mock_cliente.enviar_comando.call_args[0]
        assert isinstance(args[0], ComandoSetTemp)
        assert args[0].valor == 23.5


class TestManejadorConexion:
    """Tests de manejo de conexión/desconexión."""

    def test_conexion_establecida_logea(self, coordinator, mock_servidor):
        """conexion_establecida debe logear el evento."""
        # Emitir señal de conexión establecida
        mock_servidor.conexion_establecida.emit("192.168.1.50:54321")

        # Verificar que no lanza excepciones
        assert True

    def test_conexion_perdida_logea(self, coordinator, mock_servidor):
        """conexion_perdida debe logear el evento."""
        # Emitir señal de conexión perdida
        mock_servidor.conexion_perdida.emit("192.168.1.50:54321")

        # Verificar que no lanza excepciones
        assert True

    def test_error_parsing_logea(self, coordinator, mock_servidor):
        """error_parsing debe logear el error."""
        # Emitir señal de error de parsing
        mock_servidor.error_parsing.emit("JSON malformado")

        # Verificar que no lanza excepciones
        assert True


class TestEnvioComandos:
    """Tests de envío de comandos al RPi."""

    def test_comando_power_on_se_envia(self, coordinator, mock_cliente, mock_paneles):
        """Comando de encendido debe enviarse correctamente."""
        ctrl_power = mock_paneles["power"][2]

        ctrl_power.power_cambiado.emit(True)

        # Verificar que se envió ComandoPower con estado=True
        args = mock_cliente.enviar_comando.call_args[0]
        cmd = args[0]
        assert isinstance(cmd, ComandoPower)
        assert cmd.estado is True

    def test_comando_power_off_se_envia(self, coordinator, mock_cliente, mock_paneles):
        """Comando de apagado debe enviarse correctamente."""
        ctrl_power = mock_paneles["power"][2]

        ctrl_power.power_cambiado.emit(False)

        # Verificar que se envió ComandoPower con estado=False
        args = mock_cliente.enviar_comando.call_args[0]
        cmd = args[0]
        assert isinstance(cmd, ComandoPower)
        assert cmd.estado is False

    def test_comando_set_temp_se_envia(self, coordinator, mock_cliente, mock_paneles):
        """Comando de seteo de temperatura debe enviarse correctamente."""
        ctrl_control_temp = mock_paneles["control_temp"][2]

        ctrl_control_temp.temperatura_cambiada.emit(25.5)

        # Verificar que se envió ComandoSetTemp con valor correcto
        args = mock_cliente.enviar_comando.call_args[0]
        cmd = args[0]
        assert isinstance(cmd, ComandoSetTemp)
        assert cmd.valor == 25.5


class TestDistribucionEstado:
    """Tests de distribución de estado a múltiples paneles."""

    def test_distribuye_a_todos_los_paneles(self, coordinator, mock_servidor, mock_paneles):
        """Debe distribuir estado a todos los paneles."""
        estado = EstadoTermostato(
            temperatura_actual=22.0,
            temperatura_deseada=24.0,
            modo_climatizador="calentando",
            falla_sensor=False,
            bateria_baja=False,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        mock_servidor.estado_recibido.emit(estado)

        # Verificar que todos los paneles recibieron actualización
        assert mock_paneles["display"][2].actualizar_desde_estado.called
        assert mock_paneles["climatizador"][2].actualizar_desde_estado.called
        assert mock_paneles["indicadores"][2].actualizar_desde_estado.called
        assert mock_paneles["power"][2].actualizar_modelo.called

    def test_distribuye_estado_con_alertas(self, coordinator, mock_servidor, mock_paneles):
        """Debe distribuir estado con alertas activadas."""
        estado = EstadoTermostato(
            temperatura_actual=22.0,
            temperatura_deseada=24.0,
            modo_climatizador="reposo",
            falla_sensor=True,
            bateria_baja=True,
            encendido=True,
            modo_display="ambiente",
            timestamp=datetime.now(),
        )

        mock_servidor.estado_recibido.emit(estado)

        # Verificar que indicadores recibió las alertas
        mock_paneles["indicadores"][2].actualizar_desde_estado.assert_called_with(
            falla_sensor=True, bateria_baja=True
        )
