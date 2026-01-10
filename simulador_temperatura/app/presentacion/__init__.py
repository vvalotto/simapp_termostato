"""
Modulo de presentacion (UI) del Simulador de Temperatura.

Contiene los widgets y ventanas de la interfaz grafica:
    - ControlTemperatura: Widget para ajustar parametros de simulacion
    - GraficoTemperatura: Widget de grafico en tiempo real
    - UIPrincipal: Ventana principal de la aplicacion (legacy)
    - UIPrincipalCompositor: Ventana principal usando controladores MVC
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
    ConfigConexion,
    PanelEstado,
    ConfigPanelEstado,
    ConfigTemaOscuro,
)
from .ui_compositor import UIPrincipalCompositor, ConfigVentanaCompositor

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
    "ConfigConexion",
    "PanelEstado",
    "ConfigPanelEstado",
    "ConfigTemaOscuro",
    "UIPrincipalCompositor",
    "ConfigVentanaCompositor",
]
