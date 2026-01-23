"""
Servidor TCP que recibe el estado del termostato desde el Raspberry Pi.

Este servidor escucha en el puerto 14001 y recibe mensajes JSON con el estado
completo del termostato. Parsea los mensajes y emite señales PyQt para notificar
a la UI de actualizaciones de estado.
"""
import json
import logging
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from compartido.networking import BaseSocketServer
from ..dominio import EstadoTermostato

logger = logging.getLogger(__name__)


class ServidorEstado(BaseSocketServer):
    """
    Servidor TCP que recibe estado del termostato desde el Raspberry Pi.

    Responsabilidades:
    - Escuchar conexiones en puerto configurado (default 14001)
    - Recibir mensajes JSON con estado del termostato
    - Parsear JSON a objetos EstadoTermostato
    - Emitir señales PyQt para notificar actualizaciones

    El servidor hereda de BaseSocketServer para manejar las conexiones TCP
    y se enfoca en el procesamiento de mensajes específicos del termostato.

    Signals:
        estado_recibido: Emitida cuando se recibe un estado válido del RPi.
            Parámetro: EstadoTermostato con el estado actualizado.
        conexion_establecida: Emitida cuando el RPi se conecta.
            Parámetro: str con la dirección del cliente (ip:puerto).
        conexion_perdida: Emitida cuando el RPi se desconecta.
            Parámetro: str con la dirección del cliente.
        error_parsing: Emitida cuando hay error al parsear JSON.
            Parámetro: str con el mensaje de error.

    Example:
        >>> servidor = ServidorEstado("0.0.0.0", 14001)
        >>> servidor.estado_recibido.connect(on_estado_actualizado)
        >>> servidor.iniciar()
        >>> # ... recibe estado del RPi ...
        >>> servidor.detener()
    """

    # Señales específicas del servidor de estado
    estado_recibido = pyqtSignal(EstadoTermostato)
    conexion_establecida = pyqtSignal(str)
    conexion_perdida = pyqtSignal(str)
    error_parsing = pyqtSignal(str)

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 14001,
        parent: Optional[QObject] = None
    ):
        """
        Inicializa el servidor de estado.

        Args:
            host: Dirección IP donde escuchar (default: "0.0.0.0" para todas).
            port: Puerto TCP donde escuchar (default: 14001).
            parent: Objeto padre Qt opcional.
        """
        super().__init__(host, port, parent)

        # Conectar señales de BaseSocketServer a nuestros handlers
        self.data_received.connect(self._procesar_mensaje)
        self.client_connected.connect(self._on_cliente_conectado)
        self.client_disconnected.connect(self._on_cliente_desconectado)

        logger.info(
            "ServidorEstado inicializado: %s:%d",
            host,
            port
        )

    def iniciar(self) -> bool:
        """
        Inicia el servidor en un hilo separado.

        Returns:
            True si el servidor inició correctamente, False si hubo error.
        """
        exito = self.start()
        if exito:
            logger.info(
                "ServidorEstado iniciado en %s:%d",
                self._host,
                self._port
            )
        else:
            logger.error(
                "Error al iniciar ServidorEstado en %s:%d",
                self._host,
                self._port
            )
        return exito

    def detener(self) -> None:
        """
        Detiene el servidor y cierra todas las conexiones.

        Es seguro llamar este método aunque el servidor no esté activo.
        """
        if self.is_running():
            logger.info("Deteniendo ServidorEstado...")
            self.stop()
            logger.info("ServidorEstado detenido")

    def esta_activo(self) -> bool:
        """
        Verifica si el servidor está ejecutándose.

        Returns:
            True si el servidor está activo, False en caso contrario.
        """
        return self.is_running()

    def _procesar_mensaje(self, data: str) -> None:
        """
        Procesa un mensaje JSON recibido del RPi.

        Este método parsea el JSON, crea un objeto EstadoTermostato
        y emite la señal estado_recibido. Si hay errores, los captura
        y emite error_parsing.

        Args:
            data: Mensaje JSON recibido del cliente.
        """
        try:
            # 1. Parsear JSON a diccionario
            datos = json.loads(data.strip())
            logger.debug("JSON recibido: %s", datos)

            # 2. Crear EstadoTermostato desde el diccionario
            estado = EstadoTermostato.from_json(datos)

            # 3. Emitir señal con el estado
            logger.debug(
                "Estado procesado: temp_actual=%.1f°C, "
                "temp_deseada=%.1f°C, modo=%s",
                estado.temperatura_actual,
                estado.temperatura_deseada,
                estado.modo_climatizador
            )
            self.estado_recibido.emit(estado)

        except json.JSONDecodeError as e:
            msg = f"JSON malformado: {e}"
            logger.error(msg)
            self.error_parsing.emit(msg)

        except KeyError as e:
            msg = f"Campo requerido faltante en JSON: {e}"
            logger.error(msg)
            self.error_parsing.emit(msg)

        except ValueError as e:
            msg = f"Error al validar estado: {e}"
            logger.error(msg)
            self.error_parsing.emit(msg)

        except Exception as e:  # pylint: disable=broad-except
            # Catch-all para no crashear el servidor
            msg = f"Error inesperado al procesar mensaje: {e}"
            logger.error(msg, exc_info=True)
            self.error_parsing.emit(msg)

    def _on_cliente_conectado(self, direccion: str) -> None:
        """
        Maneja la conexión de un cliente RPi.

        Args:
            direccion: Dirección del cliente (ip:puerto).
        """
        logger.info("Cliente RPi conectado: %s", direccion)
        self.conexion_establecida.emit(direccion)

    def _on_cliente_desconectado(self, direccion: str) -> None:
        """
        Maneja la desconexión de un cliente RPi.

        Args:
            direccion: Dirección del cliente (ip:puerto).
        """
        logger.info("Cliente RPi desconectado: %s", direccion)
        self.conexion_perdida.emit(direccion)
