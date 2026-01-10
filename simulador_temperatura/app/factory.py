"""Factory para crear componentes del simulador.

Centraliza la creación de componentes de dominio, comunicación y presentación,
permitiendo configuración flexible y facilitando el testing.
"""

from typing import Dict, Optional

from .configuracion.config import ConfigSimuladorTemperatura
from .dominio.generador_temperatura import GeneradorTemperatura
from .comunicacion.cliente_temperatura import ClienteTemperatura
from .comunicacion.servicio_envio import ServicioEnvioTemperatura
from .presentacion.paneles.estado import PanelEstadoControlador
from .presentacion.paneles.control_temperatura import (
    ControlTemperaturaControlador,
    RangosControl,
)
from .presentacion.paneles.grafico import GraficoControlador, ConfigGrafico
from .presentacion.paneles.conexion import PanelConexionControlador


class ComponenteFactory:
    """Factory para crear componentes del simulador.

    Centraliza la creación de:
    - Componentes de dominio (GeneradorTemperatura)
    - Componentes de comunicación (ClienteTemperatura, ServicioEnvio)
    - Controladores MVC de presentación
    """

    def __init__(self, config: ConfigSimuladorTemperatura) -> None:
        """Inicializa la factory con la configuración.

        Args:
            config: Configuración del simulador.
        """
        self._config = config

    @property
    def config(self) -> ConfigSimuladorTemperatura:
        """Retorna la configuración del simulador."""
        return self._config

    # -- Componentes de Dominio --

    def crear_generador(self) -> GeneradorTemperatura:
        """Crea el generador de temperatura.

        Returns:
            Nueva instancia de GeneradorTemperatura configurada.
        """
        return GeneradorTemperatura(self._config)

    # -- Componentes de Comunicación --

    def crear_cliente(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None
    ) -> ClienteTemperatura:
        """Crea un cliente TCP para envío de temperatura.

        Args:
            host: IP del servidor (usa config si no se especifica).
            port: Puerto del servidor (usa config si no se especifica).

        Returns:
            Nueva instancia de ClienteTemperatura.
        """
        return ClienteTemperatura(
            host=host or self._config.ip_raspberry,
            port=port or self._config.puerto
        )

    def crear_servicio(
        self,
        generador: GeneradorTemperatura,
        cliente: ClienteTemperatura
    ) -> ServicioEnvioTemperatura:
        """Crea el servicio de envío de temperatura.

        Args:
            generador: Generador de valores de temperatura.
            cliente: Cliente TCP para envío.

        Returns:
            Nueva instancia de ServicioEnvioTemperatura.
        """
        return ServicioEnvioTemperatura(
            generador=generador,
            cliente=cliente
        )

    # -- Controladores MVC de Presentación --

    def crear_controlador_estado(self) -> PanelEstadoControlador:
        """Crea el controlador del panel de estado.

        Returns:
            Nueva instancia de PanelEstadoControlador.
        """
        return PanelEstadoControlador()

    def crear_controlador_control_temperatura(
        self,
        rangos: Optional[RangosControl] = None
    ) -> ControlTemperaturaControlador:
        """Crea el controlador de control de temperatura.

        Args:
            rangos: Rangos para los controles (opcionales).

        Returns:
            Nueva instancia de ControlTemperaturaControlador.
        """
        return ControlTemperaturaControlador(rangos=rangos)

    def crear_controlador_grafico(
        self,
        config: Optional[ConfigGrafico] = None
    ) -> GraficoControlador:
        """Crea el controlador del gráfico.

        Args:
            config: Configuración del gráfico (opcional).

        Returns:
            Nueva instancia de GraficoControlador.
        """
        return GraficoControlador(config=config)

    def crear_controlador_conexion(self) -> PanelConexionControlador:
        """Crea el controlador del panel de conexión.

        Returns:
            Nueva instancia de PanelConexionControlador.
        """
        return PanelConexionControlador(
            ip_inicial=self._config.ip_raspberry,
            puerto_inicial=self._config.puerto
        )

    def crear_controladores(
        self,
        rangos_control: Optional[RangosControl] = None,
        config_grafico: Optional[ConfigGrafico] = None
    ) -> Dict[str, object]:
        """Crea todos los controladores MVC.

        Args:
            rangos_control: Rangos para control de temperatura.
            config_grafico: Configuración del gráfico.

        Returns:
            Diccionario con los controladores creados:
            - 'estado': PanelEstadoControlador
            - 'control': ControlTemperaturaControlador
            - 'grafico': GraficoControlador
            - 'conexion': PanelConexionControlador
        """
        return {
            'estado': self.crear_controlador_estado(),
            'control': self.crear_controlador_control_temperatura(rangos_control),
            'grafico': self.crear_controlador_grafico(config_grafico),
            'conexion': self.crear_controlador_conexion(),
        }
