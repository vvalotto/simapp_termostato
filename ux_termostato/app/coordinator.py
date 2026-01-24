"""
Coordinador de señales de la aplicación UX Termostato.

Centraliza todas las conexiones de señales entre los componentes del sistema,
eliminando la necesidad de que componentes superiores gestionen callbacks manualmente.
"""

import logging
from typing import Optional

from PyQt6.QtCore import QObject

from .comunicacion import ServidorEstado, ClienteComandos
from .dominio import EstadoTermostato, ComandoPower, ComandoSetTemp, ComandoSetModoDisplay

logger = logging.getLogger(__name__)


class UXCoordinator(QObject):
    """
    Coordina las señales entre todos los componentes de la UX Termostato.

    Conecta:
    - ServidorEstado → Paneles (actualización de estado)
    - Paneles → ClienteComandos (envío de comandos)
    - Power → Controles (habilitar/deshabilitar)

    Este patrón evita dependencias circulares y centraliza la orquestación.
    """

    def __init__(
        self,
        paneles: dict[str, tuple],
        servidor_estado: ServidorEstado,
        cliente_comandos: ClienteComandos,
        parent: Optional[QObject] = None,
    ) -> None:
        """
        Inicializa el coordinador.

        Args:
            paneles: Diccionario con paneles MVC:
                - "display": (modelo, vista, controlador)
                - "climatizador": (modelo, vista, controlador)
                - "indicadores": (modelo, vista, controlador)
                - "power": (modelo, vista, controlador)
                - "control_temp": (modelo, vista, controlador)
            servidor_estado: Servidor TCP que recibe estado del RPi
            cliente_comandos: Cliente TCP que envía comandos al RPi
            parent: Objeto padre Qt opcional
        """
        super().__init__(parent)
        self._paneles = paneles
        self._servidor = servidor_estado
        self._cliente = cliente_comandos

        # Conectar todas las señales
        self._conectar_signals()

    def _conectar_signals(self) -> None:
        """Conecta todas las señales del sistema."""
        logger.info("Conectando señales del sistema...")
        self._conectar_servidor_estado()
        self._conectar_power()
        self._conectar_control_temp()

        # Paneles del Sprint 2
        if "selector_vista" in self._paneles:
            self._conectar_selector_vista()
        if "estado_conexion" in self._paneles:
            self._conectar_estado_conexion()
        if "conexion" in self._paneles:
            self._conectar_conexion()

        logger.info("Señales conectadas correctamente")

    # -- Conexión de Señales por Componente --

    def _conectar_servidor_estado(self) -> None:
        """Conecta señales del servidor que recibe estado del RPi."""
        # Servidor → Paneles (distribuir estado)
        self._servidor.estado_recibido.connect(self._on_estado_recibido)

        # Servidor → Logging (conexión establecida/perdida)
        self._servidor.conexion_establecida.connect(self._on_conexion_establecida)
        self._servidor.conexion_perdida.connect(self._on_conexion_perdida)
        self._servidor.error_parsing.connect(self._on_error_parsing)

        logger.debug("Señales de ServidorEstado conectadas")

    def _conectar_power(self) -> None:
        """Conecta señales del panel Power."""
        ctrl_power = self._paneles["power"][2]

        # Power → Cliente (enviar comando)
        ctrl_power.power_cambiado.connect(self._on_power_cambiado)

        # Power → ControlTemp (habilitar/deshabilitar)
        ctrl_control_temp = self._paneles["control_temp"][2]
        ctrl_power.power_cambiado.connect(ctrl_control_temp.set_habilitado)

        logger.debug("Señales de PowerControlador conectadas")

    def _conectar_control_temp(self) -> None:
        """Conecta señales del panel ControlTemp."""
        ctrl_control_temp = self._paneles["control_temp"][2]

        # ControlTemp → Cliente (enviar comando)
        ctrl_control_temp.temperatura_cambiada.connect(self._on_temperatura_cambiada)

        logger.debug("Señales de ControlTempControlador conectadas")

    def _conectar_selector_vista(self) -> None:
        """Conecta señales del panel SelectorVista."""
        ctrl_selector = self._paneles["selector_vista"][2]
        ctrl_power = self._paneles["power"][2]

        # SelectorVista → Cliente (enviar comando de cambio de modo)
        ctrl_selector.modo_cambiado.connect(self._on_modo_vista_cambiado)

        # Power → SelectorVista (habilitar/deshabilitar)
        ctrl_power.power_cambiado.connect(ctrl_selector.setEnabled)

        logger.debug("Señales de SelectorVistaControlador conectadas")

    def _conectar_estado_conexion(self) -> None:
        """Conecta señales del panel EstadoConexion."""
        ctrl_estado = self._paneles["estado_conexion"][2]

        # Servidor → EstadoConexion (actualizar estado)
        self._servidor.conexion_establecida.connect(ctrl_estado.conexion_establecida)
        self._servidor.conexion_perdida.connect(ctrl_estado.conexion_perdida)

        # Estado inicial: conectando
        ctrl_estado.conectando()

        logger.debug("Señales de EstadoConexionControlador conectadas")

    def _conectar_conexion(self) -> None:
        """Conecta señales del panel Conexion."""
        ctrl_conexion = self._paneles["conexion"][2]

        # Conexion → Reconectar servicios
        ctrl_conexion.ip_cambiada.connect(self._on_ip_cambiada)

        logger.debug("Señales de ConexionControlador conectadas")

    # -- Callbacks --

    def _on_estado_recibido(self, estado: EstadoTermostato) -> None:
        """
        Distribuye estado del RPi a todos los paneles.

        Args:
            estado: Estado completo del termostato recibido del RPi
        """
        # Display: actualizar temperatura según modo
        ctrl_display = self._paneles["display"][2]
        ctrl_display.actualizar_desde_estado(estado)

        # Climatizador: actualizar modo
        ctrl_climatizador = self._paneles["climatizador"][2]
        ctrl_climatizador.actualizar_desde_estado(estado)

        # Indicadores: actualizar alertas
        ctrl_indicadores = self._paneles["indicadores"][2]
        ctrl_indicadores.actualizar_desde_estado(
            falla_sensor=estado.falla_sensor, bateria_baja=estado.bateria_baja
        )

        # Power: sincronizar estado (sin emitir señal para evitar loop)
        ctrl_power = self._paneles["power"][2]
        if hasattr(ctrl_power, "actualizar_modelo"):
            # Usar actualizar_modelo que NO genera comando
            ctrl_power.actualizar_modelo(estado.encendido)

        logger.debug(
            "Estado distribuido: temp=%.1f°C, modo=%s, encendido=%s",
            estado.temperatura_actual,
            estado.modo_climatizador,
            estado.encendido,
        )

    def _on_power_cambiado(self, encendido: bool) -> None:
        """
        Envía comando de power al RPi.

        Args:
            encendido: True para encender, False para apagar
        """
        # Crear comando del dominio
        cmd = ComandoPower(estado=encendido)

        # Enviar al RPi
        exito = self._cliente.enviar_comando(cmd)

        if exito:
            logger.info("Comando power=%s enviado correctamente", encendido)
        else:
            logger.error("Error al enviar comando power=%s", encendido)

    def _on_temperatura_cambiada(self, temperatura: float) -> None:
        """
        Envía comando de seteo de temperatura al RPi.

        Args:
            temperatura: Nueva temperatura deseada en °C
        """
        # Crear comando del dominio
        cmd = ComandoSetTemp(valor=temperatura)

        # Enviar al RPi
        exito = self._cliente.enviar_comando(cmd)

        if exito:
            logger.info("Comando set_temp=%.1f°C enviado correctamente", temperatura)
        else:
            logger.error("Error al enviar comando set_temp=%.1f°C", temperatura)

    def _on_conexion_establecida(self, direccion: str) -> None:
        """
        Notifica que se estableció conexión con el RPi.

        Args:
            direccion: Dirección IP:puerto del cliente conectado
        """
        logger.info("Conexión establecida con %s", direccion)
        # Nota: US-015 conecta automáticamente este callback en _conectar_estado_conexion()

    def _on_conexion_perdida(self, direccion: str) -> None:
        """
        Notifica que se perdió conexión con el RPi.

        Args:
            direccion: Dirección IP:puerto del cliente desconectado
        """
        logger.warning("Conexión perdida con %s", direccion)
        # Nota: US-015 conecta automáticamente este callback en _conectar_estado_conexion()

    def _on_error_parsing(self, mensaje: str) -> None:
        """
        Notifica error de parsing de JSON del RPi.

        Args:
            mensaje: Descripción del error
        """
        logger.error("Error de parsing JSON: %s", mensaje)

    def _on_modo_vista_cambiado(self, modo: str) -> None:
        """
        Envía comando de cambio de modo de vista al RPi.

        Args:
            modo: Modo de vista ("ambiente" o "deseada")
        """
        # Crear comando del dominio
        cmd = ComandoSetModoDisplay(modo=modo)

        # Enviar al RPi
        exito = self._cliente.enviar_comando(cmd)

        if exito:
            logger.info("Comando set_modo_display=%s enviado correctamente", modo)
        else:
            logger.error("Error al enviar comando set_modo_display=%s", modo)

    def _on_ip_cambiada(self, nueva_ip: str) -> None:
        """
        Maneja cambio de IP del Raspberry Pi.

        Args:
            nueva_ip: Nueva dirección IP configurada

        Note:
            La persistencia de la IP en config.json se debe manejar
            en un ConfigManager separado (US-013). Por ahora solo
            registramos el cambio.
        """
        logger.info("IP del Raspberry Pi actualizada a: %s", nueva_ip)
        logger.warning(
            "Persistencia de IP no implementada aún. "
            "Requiere ConfigManager con método guardar_config()"
        )
        # TODO US-013: Implementar persistencia y reconexión
        # 1. Persistir en config.json via ConfigManager
        # 2. Reconectar ClienteComandos con nueva IP
