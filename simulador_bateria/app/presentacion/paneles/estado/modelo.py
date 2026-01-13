"""Modelo de datos para el Panel de Estado de Bateria.

Contiene el estado de la simulacion sin conocimiento de la UI.
"""

from dataclasses import dataclass

from ..base import ModeloBase


@dataclass
class EstadoBateriaPanelModelo(ModeloBase):
    """Modelo que representa el estado actual de la simulacion de bateria.

    Attributes:
        voltaje_actual: Ultimo voltaje generado en Volts.
        porcentaje: Porcentaje equivalente de bateria (0-100).
        conectado: Estado de la conexion TCP.
        envios_exitosos: Contador de envios exitosos.
        envios_fallidos: Contador de envios fallidos.
    """

    voltaje_actual: float = 0.0
    porcentaje: float = 0.0
    conectado: bool = False
    envios_exitosos: int = 0
    envios_fallidos: int = 0
    _voltaje_min: float = 0.0
    _voltaje_max: float = 5.0

    def actualizar_voltaje(self, voltaje: float) -> None:
        """Actualiza el voltaje y recalcula el porcentaje.

        Args:
            voltaje: Nuevo valor de voltaje en Volts.
        """
        self.voltaje_actual = voltaje
        self.porcentaje = self._calcular_porcentaje(voltaje)

    def _calcular_porcentaje(self, voltaje: float) -> float:
        """Calcula el porcentaje de bateria basado en el voltaje.

        Args:
            voltaje: Valor de voltaje en Volts.

        Returns:
            Porcentaje de bateria (0-100).
        """
        rango = self._voltaje_max - self._voltaje_min
        if rango <= 0:
            return 0.0
        porcentaje = ((voltaje - self._voltaje_min) / rango) * 100
        return max(0.0, min(100.0, porcentaje))

    def incrementar_exitosos(self) -> None:
        """Incrementa el contador de envios exitosos."""
        self.envios_exitosos += 1

    def incrementar_fallidos(self) -> None:
        """Incrementa el contador de envios fallidos."""
        self.envios_fallidos += 1

    def reiniciar_contadores(self) -> None:
        """Reinicia ambos contadores a cero."""
        self.envios_exitosos = 0
        self.envios_fallidos = 0

    @property
    def total_envios(self) -> int:
        """Retorna el total de envios (exitosos + fallidos)."""
        return self.envios_exitosos + self.envios_fallidos

    @property
    def tasa_exito(self) -> float:
        """Retorna la tasa de exito (0.0 a 1.0).

        Returns:
            Proporcion de envios exitosos, o 0.0 si no hay envios.
        """
        total = self.total_envios
        if total == 0:
            return 0.0
        return self.envios_exitosos / total
