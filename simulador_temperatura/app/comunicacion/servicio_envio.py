"""Servicio de integración entre GeneradorTemperatura y ClienteTemperatura.

Conecta el generador de valores con el cliente TCP para envío automático
de temperaturas al servidor ISSE_Termostato.
"""
import logging
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .cliente_temperatura import ClienteTemperatura
from ..dominio.generador_temperatura import GeneradorTemperatura
from ..dominio.estado_temperatura import EstadoTemperatura

logger = logging.getLogger(__name__)


class ServicioEnvioTemperatura(QObject):
    """Servicio que integra generador de temperatura con cliente TCP.

    Conecta las señales del GeneradorTemperatura con el ClienteTemperatura
    para enviar automáticamente cada valor generado al servidor.

    Signals:
        envio_exitoso: Emitida cuando un valor se envía correctamente.
            Parámetro: float con la temperatura enviada.
        envio_fallido: Emitida cuando falla el envío.
            Parámetro: str con el mensaje de error.
        servicio_iniciado: Emitida cuando se inicia el servicio.
        servicio_detenido: Emitida cuando se detiene el servicio.

    Example:
        >>> generador = GeneradorTemperatura(config)
        >>> cliente = ClienteTemperatura("127.0.0.1", 12000)
        >>> servicio = ServicioEnvioTemperatura(generador, cliente)
        >>> servicio.iniciar()  # Comienza envío automático
    """

    envio_exitoso = pyqtSignal(float)
    envio_fallido = pyqtSignal(str)
    servicio_iniciado = pyqtSignal()
    servicio_detenido = pyqtSignal()

    def __init__(
        self,
        generador: GeneradorTemperatura,
        cliente: ClienteTemperatura,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el servicio de envío.

        Args:
            generador: Generador de valores de temperatura.
            cliente: Cliente TCP para enviar al servidor.
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._generador = generador
        self._cliente = cliente
        self._activo = False

        self._cliente.dato_enviado.connect(self._on_dato_enviado)
        self._cliente.error_conexion.connect(self._on_error_conexion)

        logger.info("ServicioEnvioTemperatura inicializado")

    @property
    def activo(self) -> bool:
        """Indica si el servicio está activo."""
        return self._activo

    @property
    def generador(self) -> GeneradorTemperatura:
        """Generador de temperatura asociado."""
        return self._generador

    @property
    def cliente(self) -> ClienteTemperatura:
        """Cliente TCP asociado."""
        return self._cliente

    def iniciar(self) -> None:
        """Inicia el servicio de envío automático.

        Conecta la señal valor_generado del generador para enviar
        automáticamente cada valor al servidor.
        """
        if self._activo:
            logger.warning("ServicioEnvioTemperatura ya está activo")
            return

        self._generador.valor_generado.connect(self._on_valor_generado)
        self._generador.iniciar()
        self._activo = True

        logger.info(
            "ServicioEnvioTemperatura iniciado -> %s:%d",
            self._cliente.host, self._cliente.port
        )
        self.servicio_iniciado.emit()

    def detener(self) -> None:
        """Detiene el servicio de envío automático."""
        if not self._activo:
            logger.warning("ServicioEnvioTemperatura no está activo")
            return

        self._generador.detener()
        self._generador.valor_generado.disconnect(self._on_valor_generado)
        self._activo = False

        logger.info("ServicioEnvioTemperatura detenido")
        self.servicio_detenido.emit()

    def _on_valor_generado(self, estado: EstadoTemperatura) -> None:
        """Callback cuando el generador produce un nuevo valor."""
        self._cliente.enviar_estado_async(estado)

    def _on_dato_enviado(self, temperatura: float) -> None:
        """Callback cuando el cliente envía exitosamente."""
        self.envio_exitoso.emit(temperatura)

    def _on_error_conexion(self, mensaje: str) -> None:
        """Callback cuando ocurre un error de conexión."""
        self.envio_fallido.emit(mensaje)
