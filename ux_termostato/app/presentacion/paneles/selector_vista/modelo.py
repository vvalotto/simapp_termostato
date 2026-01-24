"""Modelo del panel selector de vista (ambiente vs deseada)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectorVistaModelo:
    """Modelo del selector de vista (ambiente vs deseada).

    Attributes:
        modo: Modo de vista actual ("ambiente" o "deseada")
        habilitado: Si el selector está habilitado para interacción
    """

    modo: str  # "ambiente" o "deseada"
    habilitado: bool = True

    def __post_init__(self):
        """Valida que el modo sea válido."""
        if self.modo not in ["ambiente", "deseada"]:
            raise ValueError(
                f"Modo inválido: {self.modo}. Debe ser 'ambiente' o 'deseada'."
            )
