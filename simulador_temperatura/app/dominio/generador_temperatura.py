"""Generador de valores de temperatura simulados."""
import time
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from .estado_temperatura import EstadoTemperatura
from .variacion_senoidal import VariacionSenoidal
from ..configuracion.config import ConfigSimuladorTemperatura


class GeneradorTemperatura(QObject):
    """Genera valores de temperatura simulados con variación senoidal.

    Soporta dos modos de operación:
    - Automático: Genera temperaturas siguiendo una curva senoidal
    - Manual: Retorna un valor fijo definido por el usuario

    Signals:
        valor_generado: Emitido cada vez que se genera un nuevo valor.
        temperatura_cambiada: Emitido cuando la temperatura cambia.
    """

    valor_generado = pyqtSignal(object)  # EstadoTemperatura
    temperatura_cambiada = pyqtSignal(float)

    def __init__(
        self,
        config: ConfigSimuladorTemperatura,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el generador de temperatura.

        Args:
            config: Configuración del simulador.
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._config = config
        self._modo_manual = False
        self._temperatura_manual: float = config.temperatura_inicial
        self._tiempo_inicio = time.time()

        self._variacion = VariacionSenoidal(
            temperatura_base=config.temperatura_inicial,
            amplitud=config.variacion_amplitud,
            periodo_segundos=config.variacion_periodo_segundos,
        )

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_timeout)

        self._ultima_temperatura: Optional[float] = None

    @property
    def modo_manual(self) -> bool:
        """Indica si está en modo manual."""
        return self._modo_manual

    @property
    def temperatura_actual(self) -> float:
        """Retorna la temperatura actual según el modo."""
        if self._modo_manual:
            return self._temperatura_manual
        tiempo = time.time() - self._tiempo_inicio
        return self._variacion.calcular_temperatura(tiempo)

    def set_temperatura_manual(self, temperatura: float) -> None:
        """Establece una temperatura manual y cambia a modo manual.

        Args:
            temperatura: Temperatura a establecer (°C).
        """
        self._modo_manual = True
        self._temperatura_manual = temperatura
        self.temperatura_cambiada.emit(temperatura)

    def set_modo_automatico(self) -> None:
        """Cambia a modo automático (variación senoidal)."""
        self._modo_manual = False
        self._tiempo_inicio = time.time()

    def actualizar_variacion(
        self,
        temperatura_base: float,
        amplitud: float,
        periodo_segundos: float
    ) -> None:
        """Actualiza los parámetros de variación senoidal.

        Args:
            temperatura_base: Temperatura central de la onda (°C).
            amplitud: Amplitud de variación en grados.
            periodo_segundos: Periodo de la onda senoidal.
        """
        self._variacion = VariacionSenoidal(
            temperatura_base=temperatura_base,
            amplitud=amplitud,
            periodo_segundos=periodo_segundos,
        )

    def generar_valor(self) -> EstadoTemperatura:
        """Genera un nuevo valor de temperatura.

        Returns:
            EstadoTemperatura con el valor generado.
        """
        temperatura = self.temperatura_actual
        estado = EstadoTemperatura(temperatura=temperatura)
        estado.validar_rango(
            self._config.temperatura_minima,
            self._config.temperatura_maxima
        )

        if self._ultima_temperatura != temperatura:
            self._ultima_temperatura = temperatura
            self.temperatura_cambiada.emit(temperatura)

        self.valor_generado.emit(estado)
        return estado

    def iniciar(self) -> None:
        """Inicia la generación periódica de valores."""
        self._tiempo_inicio = time.time()
        self._timer.start(self._config.intervalo_envio_ms)

    def detener(self) -> None:
        """Detiene la generación periódica de valores."""
        self._timer.stop()

    def _on_timer_timeout(self) -> None:
        """Callback del timer para generar valores periódicamente."""
        self.generar_valor()
