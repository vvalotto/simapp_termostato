"""Coordinador de señales del simulador.

Centraliza todas las conexiones de señales entre los componentes del sistema,
eliminando la necesidad de que AplicacionSimulador gestione callbacks.
"""

import logging
from typing import Callable, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from .dominio.generador_temperatura import GeneradorTemperatura
from .comunicacion.servicio_envio import ServicioEnvioTemperatura
from .presentacion.paneles.estado import PanelEstadoControlador
from .presentacion.paneles.control_temperatura import ControlTemperaturaControlador
from .presentacion.paneles.grafico import GraficoControlador
from .presentacion.paneles.conexion import PanelConexionControlador


logger = logging.getLogger(__name__)


class SimuladorCoordinator(QObject):
    """Coordina las señales entre todos los componentes del simulador.

    Conecta:
    - Generador -> UI (valores generados)
    - UI -> Generador (cambios de parámetros)
    - Servicio -> UI (estado de envíos)
    - UI -> Servicio (conexión/desconexión)

    Signals:
        conexion_solicitada: Re-emitido cuando se solicita conectar.
        desconexion_solicitada: Re-emitido cuando se solicita desconectar.
    """

    conexion_solicitada = pyqtSignal()
    desconexion_solicitada = pyqtSignal()

    def __init__(
        self,
        generador: GeneradorTemperatura,
        ctrl_estado: PanelEstadoControlador,
        ctrl_control: ControlTemperaturaControlador,
        ctrl_grafico: GraficoControlador,
        ctrl_conexion: PanelConexionControlador,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el coordinador.

        Args:
            generador: Generador de temperatura.
            ctrl_estado: Controlador del panel de estado.
            ctrl_control: Controlador de control de temperatura.
            ctrl_grafico: Controlador del gráfico.
            ctrl_conexion: Controlador del panel de conexión.
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._generador = generador
        self._ctrl_estado = ctrl_estado
        self._ctrl_control = ctrl_control
        self._ctrl_grafico = ctrl_grafico
        self._ctrl_conexion = ctrl_conexion

        self._servicio: Optional[ServicioEnvioTemperatura] = None

        self._conectar_generador()
        self._conectar_control()
        self._conectar_conexion()

    def set_servicio(self, servicio: ServicioEnvioTemperatura) -> None:
        """Establece el servicio de envío y conecta sus señales.

        Args:
            servicio: Servicio de envío de temperatura.
        """
        self._servicio = servicio
        self._conectar_servicio()
        logger.debug("Servicio conectado al coordinator")

    def _conectar_generador(self) -> None:
        """Conecta las señales del generador hacia la UI."""
        # Generador -> Gráfico y Estado
        self._generador.valor_generado.connect(self._on_valor_generado)

    def _conectar_control(self) -> None:
        """Conecta las señales del control de temperatura."""
        # Cambios de parámetros -> Generador
        self._ctrl_control.parametros_cambiados.connect(
            self._on_parametros_cambiados
        )
        self._ctrl_control.temperatura_manual_cambiada.connect(
            self._generador.set_temperatura_manual
        )
        self._ctrl_control.modo_cambiado.connect(self._on_modo_cambiado)

    def _conectar_conexion(self) -> None:
        """Conecta las señales del panel de conexión."""
        # Re-emitir señales de conexión para que AplicacionSimulador las maneje
        self._ctrl_conexion.conexion_solicitada.connect(
            self._on_conexion_solicitada
        )
        self._ctrl_conexion.desconexion_solicitada.connect(
            self._on_desconexion_solicitada
        )

    def _conectar_servicio(self) -> None:
        """Conecta las señales del servicio de envío."""
        if self._servicio is None:
            return

        # Servicio -> Estado
        self._servicio.envio_exitoso.connect(self._on_envio_exitoso)
        self._servicio.envio_fallido.connect(self._on_envio_fallido)

    def _on_valor_generado(self, estado) -> None:
        """Callback cuando se genera un nuevo valor."""
        temperatura = estado.temperatura
        self._ctrl_grafico.agregar_punto(temperatura)
        self._ctrl_estado.actualizar_temperatura(temperatura)

    def _on_parametros_cambiados(self, parametros) -> None:
        """Callback cuando cambian los parámetros senoidales."""
        self._generador.actualizar_variacion(
            temperatura_base=parametros.temperatura_base,
            amplitud=parametros.amplitud,
            periodo_segundos=parametros.periodo,
        )
        self._generador.set_modo_automatico()
        logger.debug(
            "Parámetros actualizados: base=%.1f, amp=%.1f, periodo=%.1f",
            parametros.temperatura_base,
            parametros.amplitud,
            parametros.periodo
        )

    def _on_modo_cambiado(self, es_manual: bool) -> None:
        """Callback cuando cambia el modo de operación."""
        if es_manual:
            temperatura = self._ctrl_control.temperatura_manual
            self._generador.set_temperatura_manual(temperatura)
            logger.info("Modo manual activado: %.1f°C", temperatura)
        else:
            self._generador.set_modo_automatico()
            logger.info("Modo automático activado")

    def _on_conexion_solicitada(self) -> None:
        """Callback cuando se solicita conectar."""
        self._ctrl_estado.reiniciar_contadores()
        self.conexion_solicitada.emit()

    def _on_desconexion_solicitada(self) -> None:
        """Callback cuando se solicita desconectar."""
        self._ctrl_estado.actualizar_conexion(False)
        self.desconexion_solicitada.emit()

    def _on_envio_exitoso(self, temperatura: float) -> None:
        """Callback cuando el envío es exitoso."""
        self._ctrl_estado.actualizar_conexion(True)
        self._ctrl_estado.registrar_envio_exitoso()
        self._ctrl_conexion.confirmar_conexion()
        logger.debug("Enviado exitosamente: %.2f°C", temperatura)

    def _on_envio_fallido(self, mensaje: str) -> None:
        """Callback cuando el envío falla."""
        self._ctrl_estado.actualizar_conexion(False)
        self._ctrl_estado.registrar_envio_fallido()
        self._ctrl_conexion.registrar_error(mensaje)
        logger.warning("Error de envío: %s", mensaje)

    # -- Propiedades de acceso a configuración --

    @property
    def ip_configurada(self) -> str:
        """Retorna la IP configurada en el panel de conexión."""
        return self._ctrl_conexion.ip

    @property
    def puerto_configurado(self) -> int:
        """Retorna el puerto configurado en el panel de conexión."""
        return self._ctrl_conexion.puerto
