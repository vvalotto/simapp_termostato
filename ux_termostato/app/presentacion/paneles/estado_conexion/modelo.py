"""Modelo del panel de estado de conexión."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EstadoConexionModelo:
    """Modelo del estado de conexión con el Raspberry Pi.

    Attributes:
        estado: Estado de la conexión ("conectado", "desconectado", "conectando")
        direccion_ip: Dirección IP del Raspberry Pi conectado (vacío si desconectado)
    """

    estado: str  # "conectado", "desconectado", "conectando"
    direccion_ip: str = ""

    def __post_init__(self):
        """Valida que el estado sea válido."""
        estados_validos = ["conectado", "desconectado", "conectando"]
        if self.estado not in estados_validos:
            raise ValueError(
                f"Estado inválido: {self.estado}. "
                f"Debe ser uno de: {', '.join(estados_validos)}"
            )
