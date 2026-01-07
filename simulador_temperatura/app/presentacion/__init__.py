"""
Modulo de presentacion (UI) del Simulador de Temperatura.

Contiene los widgets y ventanas de la interfaz grafica:
    - ControlTemperatura: Widget para ajustar parametros de simulacion
    - GraficoTemperatura: Widget de grafico en tiempo real
    - UIPrincipal: Ventana principal de la aplicacion
"""
from .control_temperatura import (
    ControlTemperatura,
    SliderConValor,
    PanelParametrosSenoidal,
    PanelTemperaturaManual,
    ParametrosSenoidal,
    RangosControl,
)
from .grafico_temperatura import GraficoTemperatura, ConfigGrafico
from .ui_principal import (
    UIPrincipal,
    ConfigVentana,
    PanelEstado,
    ConfigPanelEstado,
    ConfigTemaOscuro,
)

__all__ = [
    "ControlTemperatura",
    "SliderConValor",
    "PanelParametrosSenoidal",
    "PanelTemperaturaManual",
    "ParametrosSenoidal",
    "RangosControl",
    "GraficoTemperatura",
    "ConfigGrafico",
    "UIPrincipal",
    "ConfigVentana",
    "PanelEstado",
    "ConfigPanelEstado",
    "ConfigTemaOscuro",
]
