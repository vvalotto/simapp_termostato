"""
Controlador del panel Display LCD.

Este módulo define el controlador MVC que coordina el modelo y la vista del display,
manejando la lógica de actualización y comunicación con otros componentes.
"""

import logging
from dataclasses import replace
from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import DisplayModelo
from .vista import DisplayVista

logger = logging.getLogger(__name__)


class DisplayControlador(QObject):
    """
    Controlador del display LCD principal.

    Responsabilidades:
    - Actualizar el modelo cuando cambian datos (temperatura, modo, etc.)
    - Invocar vista.actualizar() cuando el modelo cambia
    - Emitir señales para comunicación con otros componentes
    - Centralizar lógica de presentación del display
    """

    # Señales para comunicación con otros componentes
    temperatura_actualizada = pyqtSignal(float)  # Notifica cambio de temperatura
    modo_vista_cambiado = pyqtSignal(str)  # Notifica cambio de modo

    def __init__(self, modelo: DisplayModelo, vista: DisplayVista):
        """
        Inicializa el controlador.

        Args:
            modelo: Instancia de DisplayModelo con estado inicial
            vista: Instancia de DisplayVista para renderizar
        """
        super().__init__()
        self._modelo = modelo
        self._vista = vista

        # Renderizar estado inicial
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self) -> DisplayModelo:
        """Retorna el modelo actual."""
        return self._modelo

    @property
    def vista(self) -> DisplayVista:
        """Retorna la vista asociada."""
        return self._vista

    def actualizar_temperatura(self, temperatura: float):
        """
        Actualiza la temperatura mostrada en el display.

        Args:
            temperatura: Nuevo valor de temperatura en °C
        """
        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, temperatura=temperatura)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Emitir señal para otros componentes
        self.temperatura_actualizada.emit(temperatura)

    def cambiar_modo_vista(self, modo: str):
        """
        Cambia el modo de visualización del display.

        Args:
            modo: Nuevo modo ("ambiente" o "deseada")

        Raises:
            ValueError: Si el modo no es válido
        """
        if modo not in ("ambiente", "deseada"):
            raise ValueError(f"Modo inválido: {modo}")

        # Actualizar modelo
        self._modelo = replace(self._modelo, modo_vista=modo)

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

        # Emitir señal
        self.modo_vista_cambiado.emit(modo)

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

    def set_error_sensor(self, tiene_error: bool):
        """
        Establece o limpia el estado de error del sensor.

        Args:
            tiene_error: True si hay error, False si está normal
        """
        # Actualizar modelo
        self._modelo = replace(self._modelo, error_sensor=tiene_error)

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

    def actualizar_desde_estado(self, estado_termostato):
        """
        Actualiza el display desde un objeto EstadoTermostato completo.

        Este método es útil para integración con el servidor que recibe
        datos del Raspberry Pi.

        Args:
            estado_termostato: Instancia de EstadoTermostato con datos del RPi
        """
        logger.info("🔄 Display actualizando desde estado: modo_vista=%s, encendido=%s",
                   self._modelo.modo_vista, estado_termostato.encendido)

        # CRÍTICO: Actualizar estado de encendido primero
        self.set_encendido(estado_termostato.encendido)

        # Determinar qué temperatura mostrar según modo actual
        if self._modelo.modo_vista == "ambiente":
            temperatura = estado_termostato.temperatura_actual
        else:
            temperatura = estado_termostato.temperatura_deseada

        logger.info("📊 Actualizando temperatura a %.1f°C (falla_sensor=%s)",
                   temperatura, estado_termostato.falla_sensor)

        # Actualizar temperatura
        self.actualizar_temperatura(temperatura)

        # Actualizar estado de error sensor
        self.set_error_sensor(estado_termostato.falla_sensor)

        logger.info("✅ Display actualizado correctamente")
