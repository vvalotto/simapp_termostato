"""Modelo de datos para el Panel de Control de Temperatura.

Contiene los parámetros de configuración de la simulación.
"""

from dataclasses import dataclass
from enum import Enum

from ..base import ModeloBase


class ModoOperacion(Enum):
    """Modo de operación del simulador."""

    AUTOMATICO = "automatico"
    MANUAL = "manual"


@dataclass
class ParametrosSenoidal:
    """Parámetros de variación senoidal."""

    temperatura_base: float = 22.0
    amplitud: float = 5.0
    periodo: float = 60.0


@dataclass
class RangosControl:
    """Rangos configurables para los controles."""

    temp_min: float = -10.0
    temp_max: float = 50.0
    amplitud_min: float = 0.0
    amplitud_max: float = 20.0
    periodo_min: float = 10.0
    periodo_max: float = 300.0


@dataclass
class ParametrosControl(ModeloBase):
    """Modelo con todos los parámetros de control.

    Attributes:
        modo: Modo de operación (automático/manual).
        temperatura_base: Temperatura central en modo automático.
        amplitud: Amplitud de variación senoidal.
        periodo: Periodo de la onda senoidal en segundos.
        temperatura_manual: Temperatura fija en modo manual.
    """

    modo: ModoOperacion = ModoOperacion.AUTOMATICO
    temperatura_base: float = 22.0
    amplitud: float = 5.0
    periodo: float = 60.0
    temperatura_manual: float = 22.0

    @property
    def es_manual(self) -> bool:
        """Indica si está en modo manual."""
        return self.modo == ModoOperacion.MANUAL

    @property
    def parametros_senoidal(self) -> ParametrosSenoidal:
        """Retorna los parámetros senoidales como dataclass."""
        return ParametrosSenoidal(
            temperatura_base=self.temperatura_base,
            amplitud=self.amplitud,
            periodo=self.periodo,
        )

    def cambiar_a_automatico(self) -> None:
        """Cambia a modo automático."""
        self.modo = ModoOperacion.AUTOMATICO

    def cambiar_a_manual(self) -> None:
        """Cambia a modo manual."""
        self.modo = ModoOperacion.MANUAL
