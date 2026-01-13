"""Generador de valores de voltaje de bateria."""
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from .estado_bateria import EstadoBateria
from ..configuracion.config import ConfigSimuladorBateria


class GeneradorBateria(QObject):
    """Genera valores de voltaje de bateria (solo modo manual).

    El usuario controla el voltaje mediante un slider.
    Los valores se emiten periodicamente para envio TCP.

    Signals:
        valor_generado: Emitido cada vez que se genera un nuevo valor.
        voltaje_cambiado: Emitido cuando el voltaje cambia.
    """

    valor_generado = pyqtSignal(object)  # EstadoBateria
    voltaje_cambiado = pyqtSignal(float)

    def __init__(
        self,
        config: ConfigSimuladorBateria,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el generador de bateria.

        Args:
            config: Configuracion del simulador.
            parent: Objeto padre Qt opcional.
        """
        super().__init__(parent)
        self._config = config
        self._voltaje_actual: float = config.voltaje_inicial

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_timeout)

    @property
    def voltaje_actual(self) -> float:
        """Retorna el voltaje actual."""
        return self._voltaje_actual

    def set_voltaje(self, voltaje: float) -> None:
        """Establece el voltaje actual.

        El voltaje se clampea al rango [voltaje_minimo, voltaje_maximo]
        definido en la configuración.

        Args:
            voltaje: Voltaje a establecer (V).
        """
        voltaje_clamped = max(
            self._config.voltaje_minimo,
            min(voltaje, self._config.voltaje_maximo)
        )
        self._voltaje_actual = voltaje_clamped
        self.voltaje_cambiado.emit(voltaje_clamped)

    def generar_valor(self) -> EstadoBateria:
        """Genera un nuevo valor de voltaje.

        Returns:
            EstadoBateria con el valor generado.
        """
        estado = EstadoBateria(voltaje=self._voltaje_actual)
        estado.validar_rango(
            self._config.voltaje_minimo,
            self._config.voltaje_maximo
        )

        self.valor_generado.emit(estado)
        return estado

    def iniciar(self) -> None:
        """Inicia la generacion periodica de valores."""
        self._timer.start(self._config.intervalo_envio_ms)

    def detener(self) -> None:
        """Detiene la generacion periodica de valores."""
        self._timer.stop()

    def _on_timer_timeout(self) -> None:
        """Callback del timer para generar valores periodicamente."""
        self.generar_valor()
