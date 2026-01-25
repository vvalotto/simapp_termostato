"""
Tests del módulo Factory (ComponenteFactoryUX).

Valida la creación de componentes de comunicación y paneles MVC.
"""

import pytest

from app.factory import ComponenteFactoryUX
from app.configuracion import ConfigUX
from app.comunicacion import ServidorEstado, ClienteComandos
from app.presentacion.paneles.display import DisplayModelo, DisplayVista, DisplayControlador
from app.presentacion.paneles.climatizador import (
    ClimatizadorModelo,
    ClimatizadorVista,
    ClimatizadorControlador,
)
from app.presentacion.paneles.indicadores import (
    IndicadoresModelo,
    IndicadoresVista,
    IndicadoresControlador,
)
from app.presentacion.paneles.power import PowerModelo, PowerVista, PowerControlador
from app.presentacion.paneles.control_temp import (
    ControlTempModelo,
    ControlTempVista,
    ControlTempControlador,
)
from app.presentacion.paneles.selector_vista import (
    SelectorVistaModelo,
    SelectorVistaVista,
    SelectorVistaControlador,
)
from app.presentacion.paneles.estado_conexion import (
    EstadoConexionModelo,
    EstadoConexionVista,
    EstadoConexionControlador,
)
from app.presentacion.paneles.conexion import (
    ConexionModelo,
    ConexionVista,
    ConexionControlador,
)


@pytest.fixture
def config():
    """Fixture de configuración para tests."""
    return ConfigUX.defaults()


@pytest.fixture
def factory(config):
    """Fixture de factory para tests."""
    return ComponenteFactoryUX(config)


class TestCreacion:
    """Tests de creación de la factory."""

    def test_creacion_con_config(self, config):
        """Debe crear factory con configuración."""
        factory = ComponenteFactoryUX(config)

        assert factory.config == config

    def test_property_config(self, factory, config):
        """Property config debe retornar la configuración."""
        assert factory.config == config


class TestCrearServidor:
    """Tests de creación de ServidorEstado."""

    def test_crear_servidor_estado_default(self, factory, qapp):
        """Debe crear ServidorEstado con puerto de config."""
        servidor = factory.crear_servidor_estado()

        assert isinstance(servidor, ServidorEstado)
        assert servidor.port == factory.config.puerto_recv

    def test_crear_servidor_estado_custom_host(self, factory, qapp):
        """Debe crear ServidorEstado con host personalizado."""
        servidor = factory.crear_servidor_estado(host="192.168.1.1")

        assert isinstance(servidor, ServidorEstado)


class TestCrearCliente:
    """Tests de creación de ClienteComandos."""

    def test_crear_cliente_comandos_default(self, factory, qapp):
        """Debe crear ClienteComandos con IP/puerto de config."""
        cliente = factory.crear_cliente_comandos()

        assert isinstance(cliente, ClienteComandos)
        assert cliente.host == factory.config.ip_raspberry
        assert cliente.port == factory.config.puerto_send

    def test_crear_cliente_comandos_custom_host(self, factory, qapp):
        """Debe crear ClienteComandos con host personalizado."""
        cliente = factory.crear_cliente_comandos(host="192.168.1.100")

        assert isinstance(cliente, ClienteComandos)
        assert cliente.host == "192.168.1.100"


class TestCrearPaneles:
    """Tests de creación de paneles MVC."""

    def test_crear_panel_display(self, factory, qapp):
        """Debe crear panel Display completo (MVC)."""
        modelo, vista, controlador = factory.crear_panel_display()

        assert isinstance(modelo, DisplayModelo)
        assert isinstance(vista, DisplayVista)
        assert isinstance(controlador, DisplayControlador)
        assert controlador.modelo == modelo
        assert controlador.vista == vista

    def test_crear_panel_climatizador(self, factory, qapp):
        """Debe crear panel Climatizador completo (MVC)."""
        modelo, vista, controlador = factory.crear_panel_climatizador()

        assert isinstance(modelo, ClimatizadorModelo)
        assert isinstance(vista, ClimatizadorVista)
        assert isinstance(controlador, ClimatizadorControlador)
        assert controlador.modelo == modelo
        assert controlador.vista == vista

    def test_crear_panel_indicadores(self, factory, qapp):
        """Debe crear panel Indicadores completo (MVC)."""
        modelo, vista, controlador = factory.crear_panel_indicadores()

        assert isinstance(modelo, IndicadoresModelo)
        assert isinstance(vista, IndicadoresVista)
        assert isinstance(controlador, IndicadoresControlador)
        assert controlador.modelo == modelo
        assert controlador.vista == vista

    def test_crear_panel_power(self, factory, qapp):
        """Debe crear panel Power completo (MVC)."""
        modelo, vista, controlador = factory.crear_panel_power()

        assert isinstance(modelo, PowerModelo)
        assert isinstance(vista, PowerVista)
        assert isinstance(controlador, PowerControlador)
        assert controlador.modelo == modelo
        assert controlador.vista == vista

    def test_crear_panel_control_temp(self, factory, qapp):
        """Debe crear panel ControlTemp completo (MVC)."""
        modelo, vista, controlador = factory.crear_panel_control_temp()

        assert isinstance(modelo, ControlTempModelo)
        assert isinstance(vista, ControlTempVista)
        assert isinstance(controlador, ControlTempControlador)
        assert controlador.modelo == modelo
        assert controlador.vista == vista


class TestCrearTodosPaneles:
    """Tests de creación de todos los paneles."""

    def test_crear_todos_paneles_retorna_dict(self, factory, qapp):
        """Debe retornar diccionario con todos los paneles."""
        paneles = factory.crear_todos_paneles()

        assert isinstance(paneles, dict)
        assert len(paneles) == 8

    def test_crear_todos_paneles_tiene_claves_correctas(self, factory, qapp):
        """Debe tener claves de todos los paneles."""
        paneles = factory.crear_todos_paneles()

        assert "display" in paneles
        assert "climatizador" in paneles
        assert "indicadores" in paneles
        assert "power" in paneles
        assert "control_temp" in paneles
        assert "selector_vista" in paneles
        assert "estado_conexion" in paneles
        assert "conexion" in paneles

    def test_crear_todos_paneles_valores_son_tuplas(self, factory, qapp):
        """Cada valor debe ser tupla (modelo, vista, controlador)."""
        paneles = factory.crear_todos_paneles()

        for key, value in paneles.items():
            assert isinstance(value, tuple), f"Panel {key} no es tupla"
            assert len(value) == 3, f"Panel {key} no tiene 3 elementos"

    def test_crear_todos_paneles_tiene_componentes_correctos(self, factory, qapp):
        """Cada panel debe tener instancias correctas."""
        paneles = factory.crear_todos_paneles()

        # Display
        modelo, vista, ctrl = paneles["display"]
        assert isinstance(modelo, DisplayModelo)
        assert isinstance(vista, DisplayVista)
        assert isinstance(ctrl, DisplayControlador)

        # Climatizador
        modelo, vista, ctrl = paneles["climatizador"]
        assert isinstance(modelo, ClimatizadorModelo)
        assert isinstance(vista, ClimatizadorVista)
        assert isinstance(ctrl, ClimatizadorControlador)

        # Indicadores
        modelo, vista, ctrl = paneles["indicadores"]
        assert isinstance(modelo, IndicadoresModelo)
        assert isinstance(vista, IndicadoresVista)
        assert isinstance(ctrl, IndicadoresControlador)

        # Power
        modelo, vista, ctrl = paneles["power"]
        assert isinstance(modelo, PowerModelo)
        assert isinstance(vista, PowerVista)
        assert isinstance(ctrl, PowerControlador)

        # ControlTemp
        modelo, vista, ctrl = paneles["control_temp"]
        assert isinstance(modelo, ControlTempModelo)
        assert isinstance(vista, ControlTempVista)
        assert isinstance(ctrl, ControlTempControlador)

        # SelectorVista
        modelo, vista, ctrl = paneles["selector_vista"]
        assert isinstance(modelo, SelectorVistaModelo)
        assert isinstance(vista, SelectorVistaVista)
        assert isinstance(ctrl, SelectorVistaControlador)

        # EstadoConexion
        modelo, vista, ctrl = paneles["estado_conexion"]
        assert isinstance(modelo, EstadoConexionModelo)
        assert isinstance(vista, EstadoConexionVista)
        assert isinstance(ctrl, EstadoConexionControlador)

        # Conexion
        modelo, vista, ctrl = paneles["conexion"]
        assert isinstance(modelo, ConexionModelo)
        assert isinstance(vista, ConexionVista)
        assert isinstance(ctrl, ConexionControlador)


class TestConfigEnPaneles:
    """Tests de uso de config en creación de paneles."""

    def test_display_usa_temperatura_inicial_de_config(self, factory, qapp):
        """Display debe usar temperatura inicial de config."""
        modelo, _, _ = factory.crear_panel_display()

        assert modelo.temperatura == factory.config.temperatura_setpoint_inicial

    def test_control_temp_usa_rangos_de_config(self, factory, qapp):
        """ControlTemp debe usar rangos de temperatura de config."""
        modelo, _, _ = factory.crear_panel_control_temp()

        assert modelo.temp_min == factory.config.temperatura_min_setpoint
        assert modelo.temp_max == factory.config.temperatura_max_setpoint
        assert modelo.temperatura_deseada == factory.config.temperatura_setpoint_inicial
