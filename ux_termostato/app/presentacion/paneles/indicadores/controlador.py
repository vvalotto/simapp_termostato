"""
Controlador del panel de Indicadores de Alerta.

Este módulo define el controlador MVC que coordina el modelo y la vista de los
indicadores de alerta, manejando las actualizaciones de estado.
"""
# pylint: disable=no-name-in-module

from dataclasses import replace
from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import IndicadoresModelo
from .vista import IndicadoresVista


class IndicadoresControlador(QObject):
    """
    Controlador del panel de indicadores de alerta.

    Responsabilidades:
    - Actualizar el modelo cuando cambian las alertas
    - Invocar vista.actualizar() cuando el modelo cambia
    - Emitir señales para comunicación con otros componentes
    - Centralizar lógica de presentación de indicadores
    """

    # Señales para comunicación con otros componentes
    alerta_activada = pyqtSignal(str)  # Notifica alerta activada ("sensor" o "bateria")
    alerta_desactivada = pyqtSignal(str)  # Notifica alerta desactivada

    def __init__(self, modelo: IndicadoresModelo, vista: IndicadoresVista):
        """
        Inicializa el controlador.

        Args:
            modelo: Instancia de IndicadoresModelo con estado inicial
            vista: Instancia de IndicadoresVista para renderizar
        """
        super().__init__()
        self._modelo = modelo
        self._vista = vista

        # Renderizar estado inicial
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self) -> IndicadoresModelo:
        """Retorna el modelo actual."""
        return self._modelo

    @property
    def vista(self) -> IndicadoresVista:
        """Retorna la vista asociada."""
        return self._vista

    def actualizar_falla_sensor(self, falla: bool):
        """
        Actualiza el estado de falla del sensor.

        Args:
            falla: True si hay falla del sensor, False si está normal
        """
        # Guardar estado anterior para detectar cambios
        falla_anterior = self._modelo.falla_sensor

        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, falla_sensor=falla)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Emitir señales si cambió el estado
        if falla and not falla_anterior:
            self.alerta_activada.emit("sensor")
        elif not falla and falla_anterior:
            self.alerta_desactivada.emit("sensor")

    def actualizar_bateria_baja(self, baja: bool):
        """
        Actualiza el estado de batería baja.

        Args:
            baja: True si la batería está baja, False si está normal
        """
        # Guardar estado anterior para detectar cambios
        baja_anterior = self._modelo.bateria_baja

        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, bateria_baja=baja)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Emitir señales si cambió el estado
        if baja and not baja_anterior:
            self.alerta_activada.emit("bateria")
        elif not baja and baja_anterior:
            self.alerta_desactivada.emit("bateria")

    def actualizar_desde_estado(self, falla_sensor: bool, bateria_baja: bool):
        """
        Actualiza ambos indicadores desde el estado del sistema.

        Este método es útil cuando se recibe el estado completo del sistema
        (ej: desde JSON del Raspberry Pi).

        Args:
            falla_sensor: True si hay falla del sensor
            bateria_baja: True si la batería está baja
        """
        # Guardar estados anteriores
        falla_anterior = self._modelo.falla_sensor
        baja_anterior = self._modelo.bateria_baja

        # Actualizar modelo con ambos valores
        self._modelo = replace(
            self._modelo,
            falla_sensor=falla_sensor,
            bateria_baja=bateria_baja
        )

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

        # Emitir señales para cambios detectados
        if falla_sensor and not falla_anterior:
            self.alerta_activada.emit("sensor")
        elif not falla_sensor and falla_anterior:
            self.alerta_desactivada.emit("sensor")

        if bateria_baja and not baja_anterior:
            self.alerta_activada.emit("bateria")
        elif not bateria_baja and baja_anterior:
            self.alerta_desactivada.emit("bateria")
