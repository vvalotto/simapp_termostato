"""
Factory para crear componentes de la aplicación UX Termostato.

Centraliza la creación de componentes de dominio, comunicación y presentación,
permitiendo configuración consistente y facilitando el testing.
"""

import logging
from typing import Optional

from .configuracion import ConfigUX
from .comunicacion import ServidorEstado, ClienteComandos
from .presentacion.paneles.display import DisplayModelo, DisplayVista, DisplayControlador
from .presentacion.paneles.climatizador import (
    ClimatizadorModelo,
    ClimatizadorVista,
    ClimatizadorControlador,
)
from .presentacion.paneles.indicadores import (
    IndicadoresModelo,
    IndicadoresVista,
    IndicadoresControlador,
)
from .presentacion.paneles.power import PowerModelo, PowerVista, PowerControlador
from .presentacion.paneles.control_temp import (
    ControlTempModelo,
    ControlTempVista,
    ControlTempControlador,
)
from .presentacion.paneles.selector_vista import (
    SelectorVistaModelo,
    SelectorVistaVista,
    SelectorVistaControlador,
)
from .presentacion.paneles.estado_conexion import (
    EstadoConexionModelo,
    EstadoConexionVista,
    EstadoConexionControlador,
)
from .presentacion.paneles.conexion import (
    ConexionModelo,
    ConexionVista,
    ConexionControlador,
)

logger = logging.getLogger(__name__)


class ComponenteFactoryUX:
    """
    Factory para crear componentes de la aplicación UX Termostato.

    Centraliza la creación de:
    - Componentes de comunicación (ServidorEstado, ClienteComandos)
    - Paneles MVC de presentación
    - Aplicación de configuración consistente
    """

    def __init__(self, config: ConfigUX) -> None:
        """
        Inicializa la factory con la configuración.

        Args:
            config: Configuración de la aplicación.
        """
        self._config = config
        logger.debug("ComponenteFactoryUX inicializado con config: IP=%s", config.ip_raspberry)

    @property
    def config(self) -> ConfigUX:
        """Retorna la configuración de la aplicación."""
        return self._config

    # -- Componentes de Comunicación --

    def crear_servidor_estado(
        self, host: str = "0.0.0.0", parent: Optional[object] = None
    ) -> ServidorEstado:
        """
        Crea el servidor TCP que recibe estado del RPi.

        Args:
            host: IP para bind (por defecto 0.0.0.0 escucha todas las interfaces)
            parent: Objeto padre Qt opcional

        Returns:
            Nueva instancia de ServidorEstado configurada
        """
        servidor = ServidorEstado(host=host, port=self._config.puerto_recv, parent=parent)
        logger.info(
            "ServidorEstado creado en %s:%d (recibe estado del RPi)",
            host,
            self._config.puerto_recv,
        )
        return servidor

    def crear_cliente_comandos(
        self, host: Optional[str] = None, parent: Optional[object] = None
    ) -> ClienteComandos:
        """
        Crea el cliente TCP para enviar comandos al RPi.

        Args:
            host: IP del RPi (usa config si no se especifica)
            parent: Objeto padre Qt opcional

        Returns:
            Nueva instancia de ClienteComandos configurada
        """
        ip_destino = host or self._config.ip_raspberry
        cliente = ClienteComandos(host=ip_destino, port=self._config.puerto_send, parent=parent)
        logger.info(
            "ClienteComandos creado para %s:%d (envía comandos al RPi)",
            ip_destino,
            self._config.puerto_send,
        )
        return cliente

    # -- Paneles MVC de Presentación --

    def crear_panel_display(self) -> tuple[DisplayModelo, DisplayVista, DisplayControlador]:
        """
        Crea el panel Display LCD completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel Display
        """
        # 1. Crear modelo con estado inicial
        modelo = DisplayModelo(
            temperatura=self._config.temperatura_setpoint_inicial,
            modo_vista="ambiente",
            encendido=False,
            error_sensor=False,
        )

        # 2. Crear vista
        vista = DisplayVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = DisplayControlador(modelo, vista)

        logger.debug("Panel Display creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_climatizador(
        self,
    ) -> tuple[ClimatizadorModelo, ClimatizadorVista, ClimatizadorControlador]:
        """
        Crea el panel Climatizador completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel Climatizador
        """
        # 1. Crear modelo con estado inicial (apagado)
        modelo = ClimatizadorModelo(modo="apagado")

        # 2. Crear vista
        vista = ClimatizadorVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = ClimatizadorControlador(modelo, vista)

        logger.debug("Panel Climatizador creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_indicadores(
        self,
    ) -> tuple[IndicadoresModelo, IndicadoresVista, IndicadoresControlador]:
        """
        Crea el panel Indicadores completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel Indicadores
        """
        # 1. Crear modelo con estado inicial (sin alertas)
        modelo = IndicadoresModelo(falla_sensor=False, bateria_baja=False)

        # 2. Crear vista
        vista = IndicadoresVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = IndicadoresControlador(modelo, vista)

        logger.debug("Panel Indicadores creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_power(self) -> tuple[PowerModelo, PowerVista, PowerControlador]:
        """
        Crea el panel Power completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel Power

        Note:
            Panel oculto en UI pero mantiene funcionalidad interna.
            Inicia encendido para que los controles estén habilitados.
        """
        # 1. Crear modelo con estado inicial ENCENDIDO (panel oculto, siempre activo)
        modelo = PowerModelo(encendido=True)

        # 2. Crear vista
        vista = PowerVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = PowerControlador(modelo, vista)

        logger.debug("Panel Power creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_control_temp(
        self,
    ) -> tuple[ControlTempModelo, ControlTempVista, ControlTempControlador]:
        """
        Crea el panel Control de Temperatura completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel ControlTemp
        """
        # 1. Crear modelo con temperatura inicial de config
        modelo = ControlTempModelo(
            temperatura_deseada=self._config.temperatura_setpoint_inicial,
            habilitado=True,  # Inicia habilitado (power oculto pero activo)
            temp_min=self._config.temperatura_min_setpoint,
            temp_max=self._config.temperatura_max_setpoint,
            incremento=0.5,
        )

        # 2. Crear vista
        vista = ControlTempVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = ControlTempControlador(modelo, vista)

        logger.debug("Panel ControlTemp creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_selector_vista(
        self,
    ) -> tuple[SelectorVistaModelo, SelectorVistaVista, SelectorVistaControlador]:
        """
        Crea el panel Selector de Vista completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel SelectorVista
        """
        # 1. Crear modelo con modo inicial "ambiente"
        modelo = SelectorVistaModelo(modo="ambiente", habilitado=True)

        # 2. Crear vista
        vista = SelectorVistaVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = SelectorVistaControlador(modelo, vista)

        logger.debug("Panel SelectorVista creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_estado_conexion(
        self,
    ) -> tuple[EstadoConexionModelo, EstadoConexionVista, EstadoConexionControlador]:
        """
        Crea el panel de Estado de Conexión completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel EstadoConexion
        """
        # 1. Crear modelo con estado inicial "desconectado"
        modelo = EstadoConexionModelo(estado="desconectado", direccion_ip="")

        # 2. Crear vista
        vista = EstadoConexionVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = EstadoConexionControlador(modelo, vista)

        logger.debug("Panel EstadoConexion creado correctamente")
        return (modelo, vista, controlador)

    def crear_panel_conexion(
        self,
    ) -> tuple[ConexionModelo, ConexionVista, ConexionControlador]:
        """
        Crea el panel de Configuración de Conexión completo (MVC).

        Returns:
            Tupla (modelo, vista, controlador) del panel Conexion
        """
        # 1. Crear modelo con configuración actual
        modelo = ConexionModelo(
            ip=self._config.ip_raspberry,
            puerto_recv=self._config.puerto_recv,
            puerto_send=self._config.puerto_send,
            ip_valida=True,
            mensaje_error="",
        )

        # 2. Crear vista
        vista = ConexionVista()

        # 3. Crear controlador conectando modelo y vista
        controlador = ConexionControlador(modelo, vista)

        logger.debug("Panel Conexion creado correctamente")
        return (modelo, vista, controlador)

    # -- Método Auxiliar --

    def crear_todos_paneles(self) -> dict[str, tuple]:
        """
        Crea todos los paneles de la UI.

        Returns:
            Diccionario con todos los paneles creados:
            - 'display': tuple (DisplayModelo, DisplayVista, DisplayControlador)
            - 'climatizador': tuple (...)
            - 'indicadores': tuple (...)
            - 'power': tuple (...)
            - 'control_temp': tuple (...)
            - 'selector_vista': tuple (...)
            - 'estado_conexion': tuple (...)
            - 'conexion': tuple (...)
        """
        paneles = {
            "display": self.crear_panel_display(),
            "climatizador": self.crear_panel_climatizador(),
            "indicadores": self.crear_panel_indicadores(),
            "power": self.crear_panel_power(),
            "control_temp": self.crear_panel_control_temp(),
            "selector_vista": self.crear_panel_selector_vista(),
            "estado_conexion": self.crear_panel_estado_conexion(),
            "conexion": self.crear_panel_conexion(),
        }
        logger.info("Todos los paneles creados correctamente (%d paneles)", len(paneles))
        return paneles
