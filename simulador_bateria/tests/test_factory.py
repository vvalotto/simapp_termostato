"""Tests para ComponenteFactory.

CRITICO: Verifica creacion de todos los componentes del simulador.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.configuracion.config import ConfigSimuladorBateria
from app.factory import ComponenteFactory
from app.dominio.generador_bateria import GeneradorBateria
from app.comunicacion.cliente_bateria import ClienteBateria
from app.comunicacion.servicio_envio import ServicioEnvioBateria


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
def factory(config):
    """Factory con configuracion de test."""
    return ComponenteFactory(config)


class TestComponenteFactoryCreacion:
    """Tests de inicializacion de la factory."""

    def test_creacion_con_config(self, config):
        """Factory acepta configuracion."""
        factory = ComponenteFactory(config)

        assert factory._config is config

    def test_factory_guarda_config(self, config):
        """Factory guarda referencia a config."""
        factory = ComponenteFactory(config)

        assert factory._config.host == "192.168.1.100"
        assert factory._config.puerto == 11000


class TestComponenteFactoryCrearGenerador:
    """Tests de crear_generador."""

    def test_crear_generador_retorna_instancia(self, factory, qtbot):
        """crear_generador retorna GeneradorBateria."""
        generador = factory.crear_generador()

        assert isinstance(generador, GeneradorBateria)

    def test_crear_generador_usa_config(self, factory, qtbot):
        """crear_generador usa configuracion de factory."""
        generador = factory.crear_generador()

        assert generador._voltaje_actual == 2.5  # voltaje_inicial
        assert generador._config.voltaje_minimo == 0.0
        assert generador._config.voltaje_maximo == 5.0

    def test_crear_generador_independientes(self, factory, qtbot):
        """Cada llamada crea instancia nueva."""
        gen1 = factory.crear_generador()
        gen2 = factory.crear_generador()

        assert gen1 is not gen2


class TestComponenteFactoryCrearCliente:
    """Tests de crear_cliente."""

    def test_crear_cliente_retorna_instancia(self, factory):
        """crear_cliente retorna ClienteBateria."""
        cliente = factory.crear_cliente()

        assert isinstance(cliente, ClienteBateria)

    def test_crear_cliente_usa_config_default(self, factory):
        """crear_cliente usa host/port de config si no se especifica."""
        cliente = factory.crear_cliente()

        assert cliente._host == "192.168.1.100"
        assert cliente._port == 11000

    def test_crear_cliente_override_host(self, factory):
        """crear_cliente acepta host override."""
        cliente = factory.crear_cliente(host="10.0.0.1")

        assert cliente._host == "10.0.0.1"
        assert cliente._port == 11000  # usa config

    def test_crear_cliente_override_port(self, factory):
        """crear_cliente acepta port override."""
        cliente = factory.crear_cliente(port=12000)

        assert cliente._host == "192.168.1.100"  # usa config
        assert cliente._port == 12000

    def test_crear_cliente_override_ambos(self, factory):
        """crear_cliente acepta host y port override."""
        cliente = factory.crear_cliente(host="localhost", port=9999)

        assert cliente._host == "localhost"
        assert cliente._port == 9999


class TestComponenteFactoryCrearServicio:
    """Tests de crear_servicio."""

    def test_crear_servicio_retorna_instancia(self, factory, qtbot):
        """crear_servicio retorna ServicioEnvioBateria."""
        generador = factory.crear_generador()
        cliente = factory.crear_cliente()

        servicio = factory.crear_servicio(generador, cliente)

        assert isinstance(servicio, ServicioEnvioBateria)

    def test_crear_servicio_conecta_generador(self, factory, qtbot):
        """crear_servicio conecta generador provisto."""
        generador = factory.crear_generador()
        cliente = factory.crear_cliente()

        servicio = factory.crear_servicio(generador, cliente)

        assert servicio._generador is generador

    def test_crear_servicio_conecta_cliente(self, factory, qtbot):
        """crear_servicio conecta cliente provisto."""
        generador = factory.crear_generador()
        cliente = factory.crear_cliente()

        servicio = factory.crear_servicio(generador, cliente)

        assert servicio._cliente is cliente


class TestComponenteFactoryCrearControladores:
    """Tests de crear_controladores."""

    def test_crear_controladores_retorna_dict(self, factory, qtbot):
        """crear_controladores retorna diccionario."""
        with patch('app.presentacion.paneles.estado.controlador.PanelEstadoVista'):
            with patch('app.presentacion.paneles.control.controlador.ControlPanelVista'):
                with patch('app.presentacion.paneles.conexion.controlador.ConexionPanelVista'):
                    controladores = factory.crear_controladores()

        assert isinstance(controladores, dict)

    def test_crear_controladores_tiene_estado(self, factory, qtbot):
        """crear_controladores incluye controlador de estado."""
        with patch('app.presentacion.paneles.estado.controlador.PanelEstadoVista'):
            with patch('app.presentacion.paneles.control.controlador.ControlPanelVista'):
                with patch('app.presentacion.paneles.conexion.controlador.ConexionPanelVista'):
                    controladores = factory.crear_controladores()

        assert 'estado' in controladores

    def test_crear_controladores_tiene_control(self, factory, qtbot):
        """crear_controladores incluye controlador de control."""
        with patch('app.presentacion.paneles.estado.controlador.PanelEstadoVista'):
            with patch('app.presentacion.paneles.control.controlador.ControlPanelVista'):
                with patch('app.presentacion.paneles.conexion.controlador.ConexionPanelVista'):
                    controladores = factory.crear_controladores()

        assert 'control' in controladores

    def test_crear_controladores_tiene_conexion(self, factory, qtbot):
        """crear_controladores incluye controlador de conexion."""
        with patch('app.presentacion.paneles.estado.controlador.PanelEstadoVista'):
            with patch('app.presentacion.paneles.control.controlador.ControlPanelVista'):
                with patch('app.presentacion.paneles.conexion.controlador.ConexionPanelVista'):
                    controladores = factory.crear_controladores()

        assert 'conexion' in controladores

    def test_crear_controladores_conexion_usa_config(self, factory, qtbot):
        """Controlador de conexion usa IP/puerto de config."""
        with patch('app.presentacion.paneles.estado.controlador.PanelEstadoVista'):
            with patch('app.presentacion.paneles.control.controlador.ControlPanelVista'):
                with patch('app.presentacion.paneles.conexion.controlador.ConexionPanelVista'):
                    controladores = factory.crear_controladores()

        ctrl_conexion = controladores['conexion']
        assert ctrl_conexion.modelo.ip == "192.168.1.100"
        assert ctrl_conexion.modelo.puerto == 11000


class TestComponenteFactoryIntegracion:
    """Tests de integracion de componentes."""

    def test_flujo_completo_creacion(self, factory, qtbot):
        """Factory crea todos los componentes necesarios."""
        # Crear componentes de dominio
        generador = factory.crear_generador()
        cliente = factory.crear_cliente()
        servicio = factory.crear_servicio(generador, cliente)

        # Verificar que todo esta conectado
        assert servicio._generador is generador
        assert servicio._cliente is cliente

    def test_multiples_generadores_independientes(self, factory, qtbot):
        """Multiples generadores son independientes."""
        gen1 = factory.crear_generador()
        gen2 = factory.crear_generador()

        gen1.set_voltaje(1.0)
        gen2.set_voltaje(4.0)

        assert gen1._voltaje_actual == 1.0
        assert gen2._voltaje_actual == 4.0
