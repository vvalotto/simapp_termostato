"""
Modulo de presentacion (UI) del Simulador de Temperatura.

Contiene los widgets y ventanas de la interfaz grafica:
    - ControlTemperatura: Widget para ajustar parametros de simulacion
    - GraficoTemperatura: Widget de grafico en tiempo real
    - UIPrincipalCompositor: Ventana principal usando controladores MVC
"""
from .control_temperatura import (
    ControlTemperatura,
    ConfigSlider,
    SliderConValor,
    PanelParametrosSenoidal,
    PanelTemperaturaManual,
    ParametrosSenoidal,
    RangosControl,
)
from .grafico_temperatura import GraficoTemperatura, ConfigGrafico
from .ui_compositor import UIPrincipalCompositor, ConfigVentanaCompositor

__all__ = [
    "ControlTemperatura",
    "ConfigSlider",
    "SliderConValor",
    "PanelParametrosSenoidal",
    "PanelTemperaturaManual",
    "ParametrosSenoidal",
    "RangosControl",
    "GraficoTemperatura",
    "ConfigGrafico",
    "UIPrincipalCompositor",
    "ConfigVentanaCompositor",
]
