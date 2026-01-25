"""
Configuración de fixtures para tests de ux_termostato.

Este módulo contiene fixtures compartidas para todos los tests,
incluyendo configuración de PyQt6 y componentes del panel Display.
"""

import pytest
from PyQt6.QtWidgets import QApplication

from app.presentacion.paneles.display.modelo import DisplayModelo
from app.presentacion.paneles.display.vista import DisplayVista
from app.presentacion.paneles.display.controlador import DisplayControlador
from app.presentacion.paneles.climatizador.modelo import ClimatizadorModelo
from app.presentacion.paneles.climatizador.vista import ClimatizadorVista
from app.presentacion.paneles.climatizador.controlador import ClimatizadorControlador
from app.presentacion.paneles.indicadores.modelo import IndicadoresModelo
from app.presentacion.paneles.indicadores.vista import IndicadoresVista
from app.presentacion.paneles.indicadores.controlador import IndicadoresControlador
from app.presentacion.paneles.power.modelo import PowerModelo
from app.presentacion.paneles.power.vista import PowerVista
from app.presentacion.paneles.power.controlador import PowerControlador
from app.presentacion.paneles.control_temp.modelo import ControlTempModelo
from app.presentacion.paneles.control_temp.vista import ControlTempVista
from app.presentacion.paneles.control_temp.controlador import ControlTempControlador
from app.presentacion.paneles.conexion.modelo import ConexionModelo
from app.presentacion.paneles.conexion.vista import ConexionVista
from app.presentacion.paneles.conexion.controlador import ConexionControlador
from app.presentacion.paneles.estado_conexion.modelo import EstadoConexionModelo
from app.presentacion.paneles.estado_conexion.vista import EstadoConexionVista
from app.presentacion.paneles.estado_conexion.controlador import EstadoConexionControlador
from app.presentacion.paneles.selector_vista.modelo import SelectorVistaModelo
from app.presentacion.paneles.selector_vista.vista import SelectorVistaVista
from app.presentacion.paneles.selector_vista.controlador import SelectorVistaControlador


@pytest.fixture(scope="session")
def qapp():
    """
    Fixture de sesión para QApplication.

    PyQt6 requiere una instancia de QApplication para crear widgets.
    Esta fixture asegura que exista una única instancia durante toda
    la sesión de tests.

    Yields:
        QApplication: Instancia de la aplicación Qt
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def display_modelo():
    """
    Fixture para crear un DisplayModelo con valores por defecto.

    Returns:
        DisplayModelo: Instancia con temperatura=22.0, modo_vista="ambiente"
    """
    return DisplayModelo(
        temperatura=22.0,
        modo_vista="ambiente",
        encendido=True,
        error_sensor=False
    )


@pytest.fixture
def display_modelo_custom():
    """
    Fixture factory para crear DisplayModelo con valores personalizados.

    Returns:
        callable: Función que crea DisplayModelo con parámetros custom
    """
    def _crear_modelo(**kwargs):
        """
        Crea DisplayModelo con valores personalizados.

        Args:
            **kwargs: Parámetros para DisplayModelo

        Returns:
            DisplayModelo: Instancia con valores custom
        """
        defaults = {
            "temperatura": 22.0,
            "modo_vista": "ambiente",
            "encendido": True,
            "error_sensor": False
        }
        defaults.update(kwargs)
        return DisplayModelo(**defaults)
    return _crear_modelo


@pytest.fixture
def display_vista(qapp):
    """
    Fixture para crear un DisplayVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        DisplayVista: Instancia de la vista del display
    """
    return DisplayVista()


@pytest.fixture
def display_controlador(qapp, display_modelo, display_vista):
    """
    Fixture para crear un DisplayControlador completo.

    Args:
        qapp: Fixture de QApplication
        display_modelo: Fixture de DisplayModelo
        display_vista: Fixture de DisplayVista

    Returns:
        DisplayControlador: Controlador completamente configurado
    """
    return DisplayControlador(display_modelo, display_vista)


@pytest.fixture
def display_controlador_custom(qapp):
    """
    Fixture factory para crear DisplayControlador con configuración custom.

    Args:
        qapp: Fixture de QApplication

    Returns:
        callable: Función que crea DisplayControlador con parámetros custom
    """
    def _crear_controlador(modelo=None, vista=None):
        """
        Crea DisplayControlador con componentes personalizados.

        Args:
            modelo: DisplayModelo opcional (crea uno por defecto si None)
            vista: DisplayVista opcional (crea una por defecto si None)

        Returns:
            DisplayControlador: Controlador configurado
        """
        if modelo is None:
            modelo = DisplayModelo()
        if vista is None:
            vista = DisplayVista()
        return DisplayControlador(modelo, vista)
    return _crear_controlador


# ========== Fixtures para Panel Climatizador ==========

@pytest.fixture
def climatizador_modelo():
    """
    Fixture para crear un ClimatizadorModelo con valores por defecto.

    Returns:
        ClimatizadorModelo: Instancia con modo="reposo", encendido=True
    """
    return ClimatizadorModelo(
        modo="reposo",
        encendido=True
    )


@pytest.fixture
def climatizador_modelo_custom():
    """
    Fixture factory para crear ClimatizadorModelo con valores personalizados.

    Returns:
        callable: Función que crea ClimatizadorModelo con parámetros custom
    """
    def _crear_modelo(**kwargs):
        """
        Crea ClimatizadorModelo con valores personalizados.

        Args:
            **kwargs: Parámetros para ClimatizadorModelo

        Returns:
            ClimatizadorModelo: Instancia con valores custom
        """
        defaults = {
            "modo": "reposo",
            "encendido": True
        }
        defaults.update(kwargs)
        return ClimatizadorModelo(**defaults)
    return _crear_modelo


@pytest.fixture
def climatizador_vista(qapp):
    """
    Fixture para crear un ClimatizadorVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        ClimatizadorVista: Instancia de la vista del climatizador
    """
    return ClimatizadorVista()


@pytest.fixture
def climatizador_controlador(qapp, climatizador_modelo, climatizador_vista):
    """
    Fixture para crear un ClimatizadorControlador completo.

    Args:
        qapp: Fixture de QApplication
        climatizador_modelo: Fixture de ClimatizadorModelo
        climatizador_vista: Fixture de ClimatizadorVista

    Returns:
        ClimatizadorControlador: Controlador completamente configurado
    """
    return ClimatizadorControlador(climatizador_modelo, climatizador_vista)


@pytest.fixture
def climatizador_controlador_custom(qapp):
    """
    Fixture factory para crear ClimatizadorControlador con configuración custom.

    Args:
        qapp: Fixture de QApplication

    Returns:
        callable: Función que crea ClimatizadorControlador con parámetros custom
    """
    def _crear_controlador(modelo=None, vista=None):
        """
        Crea ClimatizadorControlador con componentes personalizados.

        Args:
            modelo: ClimatizadorModelo opcional (crea uno por defecto si None)
            vista: ClimatizadorVista opcional (crea una por defecto si None)

        Returns:
            ClimatizadorControlador: Controlador configurado
        """
        if modelo is None:
            modelo = ClimatizadorModelo()
        if vista is None:
            vista = ClimatizadorVista()
        return ClimatizadorControlador(modelo, vista)
    return _crear_controlador


# ========== Fixtures para Panel Indicadores ==========

@pytest.fixture
def indicadores_modelo():
    """
    Fixture para crear un IndicadoresModelo con valores por defecto.

    Returns:
        IndicadoresModelo: Instancia con falla_sensor=False, bateria_baja=False
    """
    return IndicadoresModelo(
        falla_sensor=False,
        bateria_baja=False
    )


@pytest.fixture
def indicadores_modelo_custom():
    """
    Fixture factory para crear IndicadoresModelo con valores personalizados.

    Returns:
        callable: Función que crea IndicadoresModelo con parámetros custom
    """
    def _crear_modelo(**kwargs):
        """
        Crea IndicadoresModelo con valores personalizados.

        Args:
            **kwargs: Parámetros para IndicadoresModelo

        Returns:
            IndicadoresModelo: Instancia con valores custom
        """
        defaults = {
            "falla_sensor": False,
            "bateria_baja": False
        }
        defaults.update(kwargs)
        return IndicadoresModelo(**defaults)
    return _crear_modelo


@pytest.fixture
def indicadores_vista(qapp):
    """
    Fixture para crear un IndicadoresVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        IndicadoresVista: Instancia de la vista de indicadores
    """
    return IndicadoresVista()


@pytest.fixture
def indicadores_controlador(qapp, indicadores_modelo, indicadores_vista):
    """
    Fixture para crear un IndicadoresControlador completo.

    Args:
        qapp: Fixture de QApplication
        indicadores_modelo: Fixture de IndicadoresModelo
        indicadores_vista: Fixture de IndicadoresVista

    Returns:
        IndicadoresControlador: Controlador completamente configurado
    """
    return IndicadoresControlador(indicadores_modelo, indicadores_vista)


@pytest.fixture
def indicadores_controlador_custom(qapp):
    """
    Fixture factory para crear IndicadoresControlador con configuración custom.

    Args:
        qapp: Fixture de QApplication

    Returns:
        callable: Función que crea IndicadoresControlador con parámetros custom
    """
    def _crear_controlador(modelo=None, vista=None):
        """
        Crea IndicadoresControlador con componentes personalizados.

        Args:
            modelo: IndicadoresModelo opcional (crea uno por defecto si None)
            vista: IndicadoresVista opcional (crea una por defecto si None)

        Returns:
            IndicadoresControlador: Controlador configurado
        """
        if modelo is None:
            modelo = IndicadoresModelo()
        if vista is None:
            vista = IndicadoresVista()
        return IndicadoresControlador(modelo, vista)
    return _crear_controlador


# ========== Fixtures para Panel Power ==========

@pytest.fixture
def power_modelo():
    """
    Fixture para crear un PowerModelo con valores por defecto.

    Returns:
        PowerModelo: Instancia con encendido=False
    """
    return PowerModelo(
        encendido=False
    )


@pytest.fixture
def power_modelo_custom():
    """
    Fixture factory para crear PowerModelo con valores personalizados.

    Returns:
        callable: Función que crea PowerModelo con parámetros custom
    """
    def _crear_modelo(**kwargs):
        """
        Crea PowerModelo con valores personalizados.

        Args:
            **kwargs: Parámetros para PowerModelo

        Returns:
            PowerModelo: Instancia con valores custom
        """
        defaults = {
            "encendido": False
        }
        defaults.update(kwargs)
        return PowerModelo(**defaults)
    return _crear_modelo


@pytest.fixture
def power_vista(qapp):
    """
    Fixture para crear un PowerVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        PowerVista: Instancia de la vista del panel power
    """
    return PowerVista()


@pytest.fixture
def power_controlador(qapp, power_modelo, power_vista):
    """
    Fixture para crear un PowerControlador completo.

    Args:
        qapp: Fixture de QApplication
        power_modelo: Fixture de PowerModelo
        power_vista: Fixture de PowerVista

    Returns:
        PowerControlador: Controlador completamente configurado
    """
    return PowerControlador(power_modelo, power_vista)


@pytest.fixture
def power_controlador_custom(qapp):
    """
    Fixture factory para crear PowerControlador con configuración custom.

    Args:
        qapp: Fixture de QApplication

    Returns:
        callable: Función que crea PowerControlador con parámetros custom
    """
    def _crear_controlador(modelo=None, vista=None):
        """
        Crea PowerControlador con componentes personalizados.

        Args:
            modelo: PowerModelo opcional (crea uno por defecto si None)
            vista: PowerVista opcional (crea una por defecto si None)

        Returns:
            PowerControlador: Controlador configurado
        """
        if modelo is None:
            modelo = PowerModelo()
        if vista is None:
            vista = PowerVista()
        return PowerControlador(modelo, vista)
    return _crear_controlador


# ========== Fixtures para Panel Control Temp ==========

@pytest.fixture
def control_temp_modelo():
    """
    Fixture para crear un ControlTempModelo con valores por defecto.

    Returns:
        ControlTempModelo: Instancia con temperatura_deseada=22.0, habilitado=False
    """
    return ControlTempModelo(
        temperatura_deseada=22.0,
        habilitado=False
    )


@pytest.fixture
def control_temp_modelo_custom():
    """
    Fixture factory para crear ControlTempModelo con valores personalizados.

    Returns:
        callable: Función que crea ControlTempModelo con parámetros custom
    """
    def _crear_modelo(**kwargs):
        """
        Crea ControlTempModelo con valores personalizados.

        Args:
            **kwargs: Parámetros para ControlTempModelo

        Returns:
            ControlTempModelo: Instancia con valores custom
        """
        defaults = {
            "temperatura_deseada": 22.0,
            "habilitado": False,
            "temp_min": 15.0,
            "temp_max": 35.0,
            "incremento": 0.5,
        }
        defaults.update(kwargs)
        return ControlTempModelo(**defaults)
    return _crear_modelo


@pytest.fixture
def control_temp_vista(qapp):
    """
    Fixture para crear un ControlTempVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        ControlTempVista: Instancia de la vista del panel control temp
    """
    return ControlTempVista()


@pytest.fixture
def control_temp_controlador(qapp, control_temp_modelo, control_temp_vista):
    """
    Fixture para crear un ControlTempControlador completo.

    Args:
        qapp: Fixture de QApplication
        control_temp_modelo: Fixture de ControlTempModelo
        control_temp_vista: Fixture de ControlTempVista

    Returns:
        ControlTempControlador: Controlador completamente configurado
    """
    return ControlTempControlador(control_temp_modelo, control_temp_vista)


@pytest.fixture
def control_temp_controlador_custom(qapp):
    """
    Fixture factory para crear ControlTempControlador con configuración custom.

    Args:
        qapp: Fixture de QApplication

    Returns:
        callable: Función que crea ControlTempControlador con parámetros custom
    """
    def _crear_controlador(modelo=None, vista=None):
        """
        Crea ControlTempControlador con componentes personalizados.

        Args:
            modelo: ControlTempModelo opcional (crea uno por defecto si None)
            vista: ControlTempVista opcional (crea una por defecto si None)

        Returns:
            ControlTempControlador: Controlador configurado
        """
        if modelo is None:
            modelo = ControlTempModelo()
        if vista is None:
            vista = ControlTempVista()
        return ControlTempControlador(modelo, vista)
    return _crear_controlador


# ========== Fixtures para Panel SelectorVista ==========

@pytest.fixture
def selector_vista_modelo():
    """
    Fixture para crear un SelectorVistaModelo con valores por defecto.

    Returns:
        SelectorVistaModelo: Instancia con modo="ambiente", habilitado=True
    """
    return SelectorVistaModelo(modo="ambiente", habilitado=True)


@pytest.fixture
def selector_vista_vista(qapp):
    """
    Fixture para crear un SelectorVistaVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        SelectorVistaVista: Instancia de la vista del selector
    """
    return SelectorVistaVista()


@pytest.fixture
def selector_vista_controlador(qapp, selector_vista_modelo, selector_vista_vista):
    """
    Fixture para crear un SelectorVistaControlador completo.

    Args:
        qapp: Fixture de QApplication
        selector_vista_modelo: Fixture de SelectorVistaModelo
        selector_vista_vista: Fixture de SelectorVistaVista

    Returns:
        SelectorVistaControlador: Controlador completamente configurado
    """
    return SelectorVistaControlador(selector_vista_modelo, selector_vista_vista)


# ========== Fixtures para UICompositor ==========

@pytest.fixture
def todos_paneles(
    qapp,
    display_modelo, display_vista, display_controlador,
    climatizador_modelo, climatizador_vista, climatizador_controlador,
    indicadores_modelo, indicadores_vista, indicadores_controlador,
    power_modelo, power_vista, power_controlador,
    control_temp_modelo, control_temp_vista, control_temp_controlador,
    selector_vista_modelo, selector_vista_vista, selector_vista_controlador,
    estado_conexion_modelo, estado_conexion_vista, estado_conexion_controlador,
    conexion_modelo, conexion_vista, conexion_controlador
):
    """
    Fixture que crea un diccionario completo con todos los paneles MVC.

    Este es el formato esperado por UICompositor.

    Returns:
        dict: Diccionario con todos los paneles en formato (modelo, vista, controlador)
    """
    return {
        "display": (display_modelo, display_vista, display_controlador),
        "climatizador": (climatizador_modelo, climatizador_vista, climatizador_controlador),
        "indicadores": (indicadores_modelo, indicadores_vista, indicadores_controlador),
        "power": (power_modelo, power_vista, power_controlador),
        "control_temp": (control_temp_modelo, control_temp_vista, control_temp_controlador),
        "selector_vista": (selector_vista_modelo, selector_vista_vista, selector_vista_controlador),
        "estado_conexion": (estado_conexion_modelo, estado_conexion_vista, estado_conexion_controlador),
        "conexion": (conexion_modelo, conexion_vista, conexion_controlador),
    }


# ========== Fixtures para Panel EstadoConexion ==========

@pytest.fixture
def estado_conexion_modelo():
    """
    Fixture para crear un EstadoConexionModelo con valores por defecto.

    Returns:
        EstadoConexionModelo: Instancia con estado="desconectado"
    """
    return EstadoConexionModelo(estado="desconectado", direccion_ip="")


@pytest.fixture
def estado_conexion_vista(qapp):
    """
    Fixture para crear un EstadoConexionVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        EstadoConexionVista: Instancia de la vista del estado de conexión
    """
    return EstadoConexionVista()


@pytest.fixture
def estado_conexion_controlador(qapp, estado_conexion_modelo, estado_conexion_vista):
    """
    Fixture para crear un EstadoConexionControlador completo.

    Args:
        qapp: Fixture de QApplication
        estado_conexion_modelo: Fixture de EstadoConexionModelo
        estado_conexion_vista: Fixture de EstadoConexionVista

    Returns:
        EstadoConexionControlador: Controlador completamente configurado
    """
    return EstadoConexionControlador(estado_conexion_modelo, estado_conexion_vista)


# ========== Fixtures para Panel Conexion ==========

@pytest.fixture
def conexion_modelo():
    """
    Fixture para crear un ConexionModelo con valores por defecto.

    Returns:
        ConexionModelo: Instancia con IP por defecto
    """
    return ConexionModelo(
        ip="192.168.1.50",
        puerto_recv=14001,
        puerto_send=14000,
        ip_valida=True,
        mensaje_error="",
    )


@pytest.fixture
def conexion_vista(qapp):
    """
    Fixture para crear un ConexionVista.

    Args:
        qapp: Fixture de QApplication

    Returns:
        ConexionVista: Instancia de la vista de conexión
    """
    return ConexionVista()


@pytest.fixture
def conexion_controlador(qapp, conexion_modelo, conexion_vista):
    """
    Fixture para crear un ConexionControlador completo.

    Args:
        qapp: Fixture de QApplication
        conexion_modelo: Fixture de ConexionModelo
        conexion_vista: Fixture de ConexionVista

    Returns:
        ConexionControlador: Controlador completamente configurado
    """
    return ConexionControlador(conexion_modelo, conexion_vista)
