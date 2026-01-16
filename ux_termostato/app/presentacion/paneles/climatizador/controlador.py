"""
Controlador del panel Climatizador.

Este módulo define el controlador MVC que coordina el modelo y la vista del
climatizador, manejando la lógica de actualización y comunicación con otros componentes.
"""

from dataclasses import replace
from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import ClimatizadorModelo, MODO_CALENTANDO, MODO_ENFRIANDO, MODO_REPOSO
from .vista import ClimatizadorVista


class ClimatizadorControlador(QObject):
    """
    Controlador del panel de estado del climatizador.

    Responsabilidades:
    - Actualizar el modelo cuando cambia el estado del climatizador
    - Invocar vista.actualizar() cuando el modelo cambia
    - Emitir señales para comunicación con otros componentes
    - Centralizar lógica de presentación del climatizador
    """

    # Señales para comunicación con otros componentes
    estado_cambiado = pyqtSignal(str)  # Notifica cambio de estado (modo)

    def __init__(self, modelo: ClimatizadorModelo, vista: ClimatizadorVista):
        """
        Inicializa el controlador.

        Args:
            modelo: Instancia de ClimatizadorModelo con estado inicial
            vista: Instancia de ClimatizadorVista para renderizar
        """
        super().__init__()
        self._modelo = modelo
        self._vista = vista

        # Renderizar estado inicial
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self) -> ClimatizadorModelo:
        """Retorna el modelo actual."""
        return self._modelo

    @property
    def vista(self) -> ClimatizadorVista:
        """Retorna la vista asociada."""
        return self._vista

    def actualizar_estado(self, modo: str):
        """
        Actualiza el estado del climatizador.

        Args:
            modo: Nuevo modo ("calentando" | "enfriando" | "reposo" | "apagado")

        Raises:
            ValueError: Si el modo no es válido
        """
        # Validar que el modo sea válido
        modos_validos = (MODO_CALENTANDO, MODO_ENFRIANDO, MODO_REPOSO, "apagado")
        if modo not in modos_validos:
            raise ValueError(f"Modo inválido: {modo}. Debe ser uno de {modos_validos}")

        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, modo=modo)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Emitir señal para otros componentes
        self.estado_cambiado.emit(modo)

    def set_encendido(self, encendido: bool):
        """
        Cambia el estado de encendido del termostato.

        Args:
            encendido: True si está encendido, False si apagado
        """
        # Actualizar modelo
        self._modelo = replace(self._modelo, encendido=encendido)

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

    def actualizar_desde_estado(self, estado_termostato):
        """
        Actualiza el climatizador desde un objeto EstadoTermostato completo.

        Este método es útil para integración con el servidor que recibe
        datos del Raspberry Pi.

        Args:
            estado_termostato: Instancia de EstadoTermostato con datos del RPi

        El objeto estado_termostato debe tener el atributo:
        - modo_climatizador: str con el modo actual ("calentando", "enfriando", "reposo")
        """
        # Determinar el modo desde el estado del termostato
        if hasattr(estado_termostato, 'modo_climatizador'):
            modo = estado_termostato.modo_climatizador
        else:
            # Si no tiene el atributo, asumir reposo
            modo = MODO_REPOSO

        # Actualizar estado
        self.actualizar_estado(modo)
