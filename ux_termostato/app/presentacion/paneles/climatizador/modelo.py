"""
Modelo de datos para el panel Climatizador.

Este módulo define el modelo MVC que representa el estado del climatizador
del termostato, mostrando si está calentando, enfriando o en reposo.
"""

from dataclasses import dataclass


# Constantes de modos del climatizador
MODO_CALENTANDO = "calentando"
MODO_ENFRIANDO = "enfriando"
MODO_REPOSO = "reposo"
MODO_APAGADO = "apagado"


@dataclass(frozen=True)
class ClimatizadorModelo:
    """
    Modelo inmutable que representa el estado del climatizador.

    Attributes:
        modo: Estado actual del climatizador ("calentando" | "enfriando" | "reposo" | "apagado")
        encendido: Si el termostato está encendido
    """

    modo: str = MODO_REPOSO
    encendido: bool = True

    def __post_init__(self):
        """Valida los valores del modelo después de la inicialización."""
        modos_validos = (MODO_CALENTANDO, MODO_ENFRIANDO, MODO_REPOSO, MODO_APAGADO)
        if self.modo not in modos_validos:
            raise ValueError(
                f"modo debe ser uno de {modos_validos}, "
                f"recibido: {self.modo}"
            )

    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.

        Returns:
            dict: Representación del modelo como diccionario
        """
        return {
            "modo": self.modo,
            "encendido": self.encendido,
        }

    @property
    def esta_calentando(self) -> bool:
        """Retorna True si el climatizador está calentando."""
        return self.encendido and self.modo == MODO_CALENTANDO

    @property
    def esta_enfriando(self) -> bool:
        """Retorna True si el climatizador está enfriando."""
        return self.encendido and self.modo == MODO_ENFRIANDO

    @property
    def esta_en_reposo(self) -> bool:
        """Retorna True si el climatizador está en reposo."""
        return self.encendido and self.modo == MODO_REPOSO

    @property
    def esta_apagado(self) -> bool:
        """Retorna True si el climatizador está apagado."""
        return not self.encendido or self.modo == MODO_APAGADO
