"""Factory para creación de componentes del simulador de batería.

Centraliza la creación de todos los componentes, permitiendo
configuración consistente y facilitando testing con mocks.
"""
from typing import Dict, Optional

from app.configuracion.config import ConfigSimuladorBateria
from app.dominio.generador_bateria import GeneradorBateria
from app.comunicacion.cliente_bateria import ClienteBateria
from app.comunicacion.servicio_envio import ServicioEnvioBateria


class ComponenteFactory:
    """Factory que crea todos los componentes del simulador.

    Responsabilidades:
    - Crear GeneradorBateria con configuración
    - Crear ClienteBateria con host/port
    - Crear ServicioEnvioBateria integrando generador y cliente
    - Crear controladores MVC para cada panel
    """

    def __init__(self, config: ConfigSimuladorBateria) -> None:
        """Inicializa la factory con configuración.

        Args:
            config: Configuración del simulador de batería.
        """
        self._config = config

    def crear_generador(self) -> GeneradorBateria:
        """Crea una instancia de GeneradorBateria.

        Returns:
            GeneradorBateria configurado.
        """
        return GeneradorBateria(self._config)

    def crear_cliente(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None
    ) -> ClienteBateria:
        """Crea una instancia de ClienteBateria.

        Args:
            host: IP del servidor (usa config si no se especifica).
            port: Puerto del servidor (usa config si no se especifica).

        Returns:
            ClienteBateria configurado.
        """
        return ClienteBateria(
            host=host or self._config.host,
            port=port or self._config.puerto
        )

    def crear_servicio(
        self,
        generador: GeneradorBateria,
        cliente: ClienteBateria
    ) -> ServicioEnvioBateria:
        """Crea una instancia de ServicioEnvioBateria.

        Args:
            generador: GeneradorBateria para obtener valores.
            cliente: ClienteBateria para enviar datos.

        Returns:
            ServicioEnvioBateria configurado.
        """
        return ServicioEnvioBateria(
            generador=generador,
            cliente=cliente
        )

    def crear_controladores(self) -> Dict[str, object]:
        """Crea todos los controladores MVC.

        Returns:
            Diccionario con controladores:
            - 'estado': PanelEstadoControlador
            - 'control': ControlBateriaControlador
            - 'conexion': PanelConexionControlador
        """
        # Imports locales para evitar dependencias circulares
        # (los controladores importan componentes de dominio)
        from app.presentacion.paneles.estado.controlador import (
            PanelEstadoControlador
        )
        from app.presentacion.paneles.control.controlador import (
            ControlBateriaControlador
        )
        from app.presentacion.paneles.conexion.controlador import (
            PanelConexionControlador
        )

        return {
            'estado': PanelEstadoControlador(),
            'control': ControlBateriaControlador(),
            'conexion': PanelConexionControlador(
                ip_inicial=self._config.host,
                puerto_inicial=self._config.puerto
            ),
        }
