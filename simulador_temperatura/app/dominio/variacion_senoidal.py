"""Lógica de variación senoidal para simulación de temperatura."""
import math
from dataclasses import dataclass


@dataclass
class VariacionSenoidal:
    """Genera variación de temperatura siguiendo una curva senoidal.

    Simula cambios naturales de temperatura como ciclos día/noche.

    Fórmula: T(t) = temperatura_base + amplitud * sin(2π * t / periodo)

    Attributes:
        temperatura_base: Temperatura central de la oscilación (°C).
        amplitud: Máxima desviación respecto a la base (°C).
        periodo_segundos: Tiempo para completar un ciclo (segundos).
    """

    temperatura_base: float
    amplitud: float
    periodo_segundos: float

    def calcular_temperatura(self, tiempo_segundos: float) -> float:
        """Calcula la temperatura en el tiempo dado.

        Args:
            tiempo_segundos: Tiempo transcurrido desde el inicio (segundos).

        Returns:
            Temperatura calculada en grados Celsius.
        """
        angulo = 2 * math.pi * tiempo_segundos / self.periodo_segundos
        return self.temperatura_base + self.amplitud * math.sin(angulo)

    @property
    def temperatura_maxima(self) -> float:
        """Temperatura máxima alcanzable (base + amplitud)."""
        return self.temperatura_base + self.amplitud

    @property
    def temperatura_minima(self) -> float:
        """Temperatura mínima alcanzable (base - amplitud)."""
        return self.temperatura_base - self.amplitud
