"""
Controlador del panel Power (Encendido/Apagado).

Este módulo define el controlador MVC que coordina el modelo y la vista del
botón de encendido/apagado, manejando la lógica de toggle y generación de comandos.
"""

from dataclasses import replace
from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import PowerModelo
from .vista import PowerVista


class PowerControlador(QObject):
    """
    Controlador del panel de encendido/apagado del termostato.

    Responsabilidades:
    - Manejar el toggle del estado encendido/apagado
    - Actualizar el modelo cuando cambia el estado
    - Invocar vista.actualizar() cuando el modelo cambia
    - Emitir señales para comunicación con otros componentes
    - Generar comandos JSON para enviar al Raspberry Pi
    """

    # Señales para comunicación con otros componentes
    power_cambiado = pyqtSignal(bool)  # True=encendido, False=apagado
    comando_enviado = pyqtSignal(dict)  # Comando JSON para el RPi

    def __init__(self, modelo: PowerModelo, vista: PowerVista):
        """
        Inicializa el controlador.

        Args:
            modelo: Instancia de PowerModelo con estado inicial
            vista: Instancia de PowerVista para renderizar
        """
        super().__init__()
        self._modelo = modelo
        self._vista = vista

        # Conectar señales del botón
        self._vista.btn_power.clicked.connect(self.cambiar_estado)

        # Renderizar estado inicial
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self) -> PowerModelo:
        """Retorna el modelo actual."""
        return self._modelo

    @property
    def vista(self) -> PowerVista:
        """Retorna la vista asociada."""
        return self._vista

    def cambiar_estado(self):
        """
        Toggle del estado encendido/apagado.

        Invoca la lógica completa:
        1. Cambia el estado del modelo (inmutable)
        2. Actualiza la vista
        3. Genera comando JSON
        4. Emite señales para otros componentes
        """
        # Toggle del estado
        nuevo_estado = not self._modelo.encendido

        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, encendido=nuevo_estado)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Generar comando JSON para el Raspberry Pi
        comando = self._generar_comando_power(nuevo_estado)

        # Emitir señales
        self.power_cambiado.emit(nuevo_estado)
        self.comando_enviado.emit(comando)

    def actualizar_modelo(self, encendido: bool):
        """
        Actualiza el modelo con un nuevo estado SIN emitir señales.

        Este método es útil para sincronizar el estado desde el servidor
        cuando se recibe confirmación del Raspberry Pi, evitando loops
        de comandos.

        Args:
            encendido: True si está encendido, False si apagado
        """
        # Actualizar modelo (inmutable)
        self._modelo = replace(self._modelo, encendido=encendido)

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

        # NO emitir señal para evitar enviar comando de vuelta al RPi

    def _generar_comando_power(self, encendido: bool) -> dict:
        """
        Genera el comando JSON para enviar al Raspberry Pi.

        Args:
            encendido: True para encender, False para apagar

        Returns:
            dict: Comando JSON con estructura:
                {
                    "comando": "power",
                    "estado": "on" | "off"
                }
        """
        return {
            "comando": "power",
            "estado": "on" if encendido else "off"
        }
