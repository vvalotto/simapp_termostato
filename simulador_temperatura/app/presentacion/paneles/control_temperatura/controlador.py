"""Controlador para el Panel de Control de Temperatura.

Coordina la comunicación entre el modelo y la vista,
gestionando los cambios de parámetros de simulación.
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..base import ControladorBase
from .modelo import ParametrosControl, ParametrosSenoidal, ModoOperacion, RangosControl
from .vista import ControlTemperaturaVista


class ControlTemperaturaControlador(
    ControladorBase[ParametrosControl, ControlTemperaturaVista]
):
    """Controlador del panel de control de temperatura.

    Gestiona los cambios de modo y parámetros de simulación.

    Signals:
        modo_cambiado: Emitido cuando cambia el modo (True=manual).
        parametros_cambiados: Emitido cuando cambian parámetros senoidales.
        temperatura_manual_cambiada: Emitido cuando cambia T_manual.
    """

    modo_cambiado = pyqtSignal(bool)
    parametros_cambiados = pyqtSignal(object)  # ParametrosSenoidal
    temperatura_manual_cambiada = pyqtSignal(float)

    def __init__(
        self,
        modelo: Optional[ParametrosControl] = None,
        vista: Optional[ControlTemperaturaVista] = None,
        rangos: Optional[RangosControl] = None,
        parent: Optional[QObject] = None
    ) -> None:
        """Inicializa el controlador.

        Args:
            modelo: Modelo de parámetros, se crea uno si no se provee.
            vista: Vista del panel, se crea una si no se provee.
            rangos: Rangos para los controles.
            parent: Objeto padre Qt opcional.
        """
        modelo = modelo or ParametrosControl()
        vista = vista or ControlTemperaturaVista(rangos=rangos)
        super().__init__(modelo, vista, parent)

        # Sincronizar vista con modelo inicial
        self._actualizar_vista()

    def _conectar_signals(self) -> None:
        """Conecta las señales de la vista con el controlador."""
        self._vista.modo_cambiado.connect(self._on_modo_cambiado)
        self._vista.temperatura_base_cambiada.connect(self._on_temp_base_cambiada)
        self._vista.amplitud_cambiada.connect(self._on_amplitud_cambiada)
        self._vista.periodo_cambiado.connect(self._on_periodo_cambiado)
        self._vista.temperatura_manual_cambiada.connect(self._on_temp_manual_cambiada)

    def _on_modo_cambiado(self, es_manual: bool) -> None:
        """Callback cuando cambia el modo."""
        if es_manual:
            self._modelo.cambiar_a_manual()
        else:
            self._modelo.cambiar_a_automatico()
        self.modo_cambiado.emit(es_manual)
        self.modelo_cambiado.emit(self._modelo)

    def _on_temp_base_cambiada(self, valor: float) -> None:
        """Callback cuando cambia temperatura base."""
        self._modelo.temperatura_base = valor
        self._emitir_parametros_cambiados()

    def _on_amplitud_cambiada(self, valor: float) -> None:
        """Callback cuando cambia amplitud."""
        self._modelo.amplitud = valor
        self._emitir_parametros_cambiados()

    def _on_periodo_cambiado(self, valor: float) -> None:
        """Callback cuando cambia periodo."""
        self._modelo.periodo = valor
        self._emitir_parametros_cambiados()

    def _on_temp_manual_cambiada(self, valor: float) -> None:
        """Callback cuando cambia temperatura manual."""
        self._modelo.temperatura_manual = valor
        self.temperatura_manual_cambiada.emit(valor)
        self.modelo_cambiado.emit(self._modelo)

    def _emitir_parametros_cambiados(self) -> None:
        """Emite signal de parámetros senoidales cambiados."""
        self.parametros_cambiados.emit(self._modelo.parametros_senoidal)
        self.modelo_cambiado.emit(self._modelo)

    def set_modo(self, manual: bool) -> None:
        """Establece el modo sin emitir signal."""
        if manual:
            self._modelo.cambiar_a_manual()
        else:
            self._modelo.cambiar_a_automatico()
        self._actualizar_vista()

    def set_parametros_senoidal(self, parametros: ParametrosSenoidal) -> None:
        """Establece los parámetros senoidales sin emitir signal."""
        self._modelo.temperatura_base = parametros.temperatura_base
        self._modelo.amplitud = parametros.amplitud
        self._modelo.periodo = parametros.periodo
        self._actualizar_vista()

    def set_temperatura_manual(self, temperatura: float) -> None:
        """Establece la temperatura manual sin emitir signal."""
        self._modelo.temperatura_manual = temperatura
        self._actualizar_vista()

    @property
    def es_modo_manual(self) -> bool:
        """Indica si está en modo manual."""
        return self._modelo.es_manual

    @property
    def parametros_senoidal(self) -> ParametrosSenoidal:
        """Retorna los parámetros senoidales actuales."""
        return self._modelo.parametros_senoidal

    @property
    def temperatura_manual(self) -> float:
        """Retorna la temperatura manual actual."""
        return self._modelo.temperatura_manual

    @property
    def temperatura_base(self) -> float:
        """Retorna la temperatura base actual."""
        return self._modelo.temperatura_base

    @property
    def amplitud(self) -> float:
        """Retorna la amplitud actual."""
        return self._modelo.amplitud

    @property
    def periodo(self) -> float:
        """Retorna el periodo actual."""
        return self._modelo.periodo
