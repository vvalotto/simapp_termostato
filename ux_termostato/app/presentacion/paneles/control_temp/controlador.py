"""
Controlador del panel Control de Temperatura.

Este módulo define el controlador MVC que coordina el modelo y la vista del
panel de control de temperatura, manejando aumentos/disminuciones y comandos.
"""

from dataclasses import replace
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

from .modelo import ControlTempModelo
from .vista import ControlTempVista


class ControlTempControlador(QObject):
    """
    Controlador del panel de control de temperatura.

    Responsabilidades:
    - Manejar incremento/decremento de temperatura deseada
    - Validar rangos (15-35°C) y estado habilitado
    - Actualizar el modelo cuando cambia la temperatura
    - Invocar vista.actualizar() cuando el modelo cambia
    - Emitir señales para comunicación con otros componentes
    - Generar comandos JSON con timestamp para enviar al Raspberry Pi
    """

    # Señales para comunicación con otros componentes
    temperatura_cambiada = pyqtSignal(float)  # Nueva temperatura deseada
    comando_enviado = pyqtSignal(dict)  # Comando JSON para el RPi

    def __init__(self, modelo: ControlTempModelo, vista: ControlTempVista):
        """
        Inicializa el controlador.

        Args:
            modelo: Instancia de ControlTempModelo con estado inicial
            vista: Instancia de ControlTempVista para renderizar
        """
        super().__init__()
        self._modelo = modelo
        self._vista = vista

        # Conectar señales de los botones
        self._vista.btn_subir.clicked.connect(self.aumentar_temperatura)
        self._vista.btn_bajar.clicked.connect(self.disminuir_temperatura)

        # Renderizar estado inicial
        self._vista.actualizar(self._modelo)

    @property
    def modelo(self) -> ControlTempModelo:
        """Retorna el modelo actual."""
        return self._modelo

    @property
    def vista(self) -> ControlTempVista:
        """Retorna la vista asociada."""
        return self._vista

    def aumentar_temperatura(self):
        """
        Incrementa la temperatura deseada en 0.5°C.

        Solo incrementa si:
        - El panel está habilitado (termostato encendido)
        - La temperatura actual es menor que el máximo (35°C)

        Flujo:
        1. Valida que se puede aumentar
        2. Calcula nueva temperatura
        3. Actualiza modelo (inmutable)
        4. Actualiza vista
        5. Genera y envía comando JSON al RPi
        6. Emite señales
        """
        if not self._modelo.puede_aumentar():
            return

        # Calcular nueva temperatura
        nueva_temp = self._modelo.temperatura_deseada + self._modelo.incremento

        # Asegurar que no supera el máximo (por redondeo de floats)
        nueva_temp = min(nueva_temp, self._modelo.temp_max)

        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, temperatura_deseada=nueva_temp)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Generar comando JSON para el Raspberry Pi
        comando = self._generar_comando_temperatura(nueva_temp)

        # Emitir señales
        self.temperatura_cambiada.emit(nueva_temp)
        self.comando_enviado.emit(comando)

    def disminuir_temperatura(self):
        """
        Decrementa la temperatura deseada en 0.5°C.

        Solo decrementa si:
        - El panel está habilitado (termostato encendido)
        - La temperatura actual es mayor que el mínimo (15°C)

        Flujo:
        1. Valida que se puede disminuir
        2. Calcula nueva temperatura
        3. Actualiza modelo (inmutable)
        4. Actualiza vista
        5. Genera y envía comando JSON al RPi
        6. Emite señales
        """
        if not self._modelo.puede_disminuir():
            return

        # Calcular nueva temperatura
        nueva_temp = self._modelo.temperatura_deseada - self._modelo.incremento

        # Asegurar que no baja del mínimo (por redondeo de floats)
        nueva_temp = max(nueva_temp, self._modelo.temp_min)

        # Actualizar modelo (inmutable, crear nueva instancia)
        self._modelo = replace(self._modelo, temperatura_deseada=nueva_temp)

        # Renderizar cambios en la vista
        self._vista.actualizar(self._modelo)

        # Generar comando JSON para el Raspberry Pi
        comando = self._generar_comando_temperatura(nueva_temp)

        # Emitir señales
        self.temperatura_cambiada.emit(nueva_temp)
        self.comando_enviado.emit(comando)

    def set_habilitado(self, habilitado: bool):
        """
        Habilita o deshabilita el panel de control.

        Este método debe conectarse a la señal power_cambiado del panel Power
        para habilitar/deshabilitar los botones según el estado del termostato.

        Args:
            habilitado: True para habilitar el panel, False para deshabilitar

        Example:
            >>> # En el coordinator:
            >>> power_ctrl.power_cambiado.connect(control_temp_ctrl.set_habilitado)
        """
        # Actualizar modelo (inmutable)
        self._modelo = replace(self._modelo, habilitado=habilitado)

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

    def set_temperatura_actual(self, temperatura: float):
        """
        Actualiza la temperatura deseada desde el servidor RPi.

        Este método permite sincronizar el estado local con el estado
        del Raspberry Pi cuando se recibe actualización vía puerto 14001.

        Args:
            temperatura: Nueva temperatura deseada en °C

        Example:
            >>> # En el coordinator:
            >>> servidor.temperatura_deseada_recibida.connect(
            ...     control_temp_ctrl.set_temperatura_actual
            ... )
        """
        # Validar rango
        temperatura = max(self._modelo.temp_min, min(temperatura, self._modelo.temp_max))

        # Actualizar modelo (inmutable)
        self._modelo = replace(self._modelo, temperatura_deseada=temperatura)

        # Renderizar cambios
        self._vista.actualizar(self._modelo)

        # Emitir señal (sin comando, ya que viene del exterior)
        self.temperatura_cambiada.emit(temperatura)

    def _generar_comando_temperatura(self, temperatura: float) -> dict:
        """
        Genera el comando JSON para enviar al Raspberry Pi.

        El comando incluye timestamp ISO 8601 para permitir al RPi
        detectar comandos duplicados o desfasados.

        Args:
            temperatura: Temperatura deseada en °C

        Returns:
            dict: Comando JSON con estructura:
                {
                    "comando": "set_temp_deseada",
                    "valor": 23.5,
                    "timestamp": "2026-01-22T14:30:00.123456"
                }
        """
        return {
            "comando": "set_temp_deseada",
            "valor": round(temperatura, 1),  # Redondear a 1 decimal
            "timestamp": datetime.now().isoformat()
        }
