"""Modelo de datos para el Panel de Estado.

Contiene el estado de la simulación sin conocimiento de la UI.
"""

from dataclasses import dataclass

from ..base import ModeloBase


@dataclass
class EstadoSimulacion(ModeloBase):
    """Modelo que representa el estado actual de la simulación.

    Attributes:
        temperatura_actual: Última temperatura generada.
        conectado: Estado de la conexión TCP.
        envios_exitosos: Contador de envíos exitosos.
        envios_fallidos: Contador de envíos fallidos.
    """

    temperatura_actual: float = 0.0
    conectado: bool = False
    envios_exitosos: int = 0
    envios_fallidos: int = 0

    def incrementar_exitosos(self) -> None:
        """Incrementa el contador de envíos exitosos."""
        self.envios_exitosos += 1

    def incrementar_fallidos(self) -> None:
        """Incrementa el contador de envíos fallidos."""
        self.envios_fallidos += 1

    def reiniciar_contadores(self) -> None:
        """Reinicia ambos contadores a cero."""
        self.envios_exitosos = 0
        self.envios_fallidos = 0

    @property
    def total_envios(self) -> int:
        """Retorna el total de envíos (exitosos + fallidos)."""
        return self.envios_exitosos + self.envios_fallidos

    @property
    def tasa_exito(self) -> float:
        """Retorna la tasa de éxito (0.0 a 1.0).

        Returns:
            Proporción de envíos exitosos, o 0.0 si no hay envíos.
        """
        total = self.total_envios
        if total == 0:
            return 0.0
        return self.envios_exitosos / total
