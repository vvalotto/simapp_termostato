"""
Coordinador de señales de la aplicación UX Termostato.

Centraliza todas las conexiones de señales entre los componentes del sistema,
eliminando la necesidad de que componentes superiores gestionen callbacks manualmente.
"""

import logging
from typing import Optional

from PyQt6.QtCore import QObject

from .comunicacion import ServidorEstado, ClienteComandos
from .dominio import EstadoTermostato, ComandoPower, ComandoSetTemp

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
        # [futuro US-015] Actualizar widget de estado de conexión

    def _on_conexion_perdida(self, direccion: str) -> None:
        """
        Notifica que se perdió conexión con el RPi.

        Args:
            direccion: Dirección IP:puerto del cliente desconectado
        """
        logger.warning("Conexión perdida con %s", direccion)
        # [futuro US-015] Actualizar widget de estado de conexión

    def _on_error_parsing(self, mensaje: str) -> None:
        """
        Notifica error de parsing de JSON del RPi.

        Args:
            mensaje: Descripción del error
        """
        logger.error("Error de parsing JSON: %s", mensaje)
