"""Compositor de UI - Ensambla todos los paneles MVC.

Este módulo implementa el UICompositor que es responsable únicamente
del layout y composición visual de la interfaz de usuario.
Toda la lógica de negocio está en los controladores MVC.
"""

import logging

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

logger = logging.getLogger(__name__)


class UICompositor:
    """Compositor de UI - Ensambla todos los paneles en un layout coherente.

    Responsabilidades:
    - Extraer vistas de paneles MVC
    - Crear layout principal vertical
    - Ensamblar header horizontal (EstadoConexion + Indicadores)
    - Ensamblar paneles en orden lógico
    - Configurar espaciado, márgenes y tamaño

    NO contiene lógica de negocio.
    """

    # Paneles requeridos para validación
    PANELES_REQUERIDOS = [
        "display",
        "climatizador",
        "indicadores",
        "power",
        "control_temp",
        "selector_vista",
        "estado_conexion",
        "conexion",
    ]

    def __init__(self, paneles: dict[str, tuple]) -> None:
        """Inicializa el compositor con los paneles MVC.

        Args:
            paneles: Diccionario con tuplas (modelo, vista, controlador):
                - 'display': (DisplayModelo, DisplayVista,
                              DisplayControlador)
                - 'climatizador': (ClimatizadorModelo, ClimatizadorVista,
                                   ClimatizadorControlador)
                - 'indicadores': (IndicadoresModelo, IndicadoresVista,
                                  IndicadoresControlador)
                - 'power': (PowerModelo, PowerVista, PowerControlador)
                - 'control_temp': (ControlTempModelo, ControlTempVista,
                                   ControlTempControlador)
                - 'selector_vista': (SelectorVistaModelo, SelectorVistaVista,
                                     SelectorVistaControlador)
                - 'estado_conexion': (EstadoConexionModelo,
                                      EstadoConexionVista,
                                      EstadoConexionControlador)
                - 'conexion': (ConexionModelo, ConexionVista,
                               ConexionControlador)

        Raises:
            ValueError: Si faltan paneles requeridos o el dict está vacío.
        """
        self._validar_paneles(paneles)
        self._paneles = paneles
        logger.debug("UICompositor inicializado con %d paneles", len(paneles))

    def _validar_paneles(self, paneles: dict[str, tuple]) -> None:
        """Valida que el dict de paneles contenga todos los requeridos.

        Args:
            paneles: Diccionario de paneles a validar.

        Raises:
            ValueError: Si el dict está vacío o faltan paneles.
        """
        if not paneles:
            raise ValueError("El diccionario de paneles está vacío")

        faltantes = [p for p in self.PANELES_REQUERIDOS if p not in paneles]
        if faltantes:
            raise ValueError(f"Faltan paneles requeridos: {', '.join(faltantes)}")

        logger.debug(
            "Validación de paneles exitosa: %d/%d",
            len(paneles),
            len(self.PANELES_REQUERIDOS)
        )

    def _extraer_vista(self, nombre_panel: str) -> QWidget:
        """Extrae la vista de un panel MVC.

        Args:
            nombre_panel: Nombre del panel en el dict.

        Returns:
            Widget de la vista (índice 1 de la tupla MVC).

        Raises:
            IndexError: Si la tupla no tiene al menos 2 elementos.
            AttributeError: Si el elemento no es un QWidget.
        """
        tupla_mvc = self._paneles[nombre_panel]
        if len(tupla_mvc) < 2:
            raise IndexError(f"Panel '{nombre_panel}' no tiene estructura MVC válida")

        vista = tupla_mvc[1]  # Índice 1 es la Vista
        if not isinstance(vista, QWidget):
            raise AttributeError(f"Vista de '{nombre_panel}' no es un QWidget")

        return vista

    def crear_layout(self) -> QWidget:
        """Crea y retorna el widget con layout completo.

        Estructura del layout:
        - Header horizontal (EstadoConexion + Indicadores)
        - Display LCD
        - Climatizador
        - Power
        - ControlTemp
        - SelectorVista
        - Conexion

        Returns:
            QWidget con todos los paneles ensamblados.
        """
        # Widget central
        widget_central = QWidget()
        widget_central.setMinimumSize(QSize(500, 700))
        widget_central.resize(600, 800)

        # Layout principal vertical
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(12)

        # 1. Header horizontal (EstadoConexion + Indicadores)
        layout_header = self._crear_header()
        layout_principal.addLayout(layout_header)

        # 2. Display LCD
        vista_display = self._extraer_vista("display")
        layout_principal.addWidget(vista_display)

        # 3. Climatizador
        vista_climatizador = self._extraer_vista("climatizador")
        layout_principal.addWidget(vista_climatizador)

        # 4. Power
        vista_power = self._extraer_vista("power")
        layout_principal.addWidget(vista_power)

        # 5. Control Temperatura
        vista_control_temp = self._extraer_vista("control_temp")
        layout_principal.addWidget(vista_control_temp)

        # 6. Selector Vista
        vista_selector = self._extraer_vista("selector_vista")
        layout_principal.addWidget(vista_selector)

        # 7. Conexión
        vista_conexion = self._extraer_vista("conexion")
        layout_principal.addWidget(vista_conexion)

        logger.info("Layout completo creado: %d paneles ensamblados", len(self.PANELES_REQUERIDOS))
        return widget_central

    def _crear_header(self) -> QHBoxLayout:
        """Crea el header horizontal con EstadoConexion e Indicadores.

        Estructura:
        [EstadoConexion] <-- stretch --> [Indicadores]

        Returns:
            QHBoxLayout con el header ensamblado.
        """
        layout_header = QHBoxLayout()
        layout_header.setSpacing(10)

        # Estado de conexión a la izquierda
        vista_estado_conexion = self._extraer_vista("estado_conexion")
        layout_header.addWidget(vista_estado_conexion)

        # Separador flexible
        layout_header.addStretch()

        # Indicadores a la derecha
        vista_indicadores = self._extraer_vista("indicadores")
        layout_header.addWidget(vista_indicadores)

        logger.debug("Header horizontal creado (EstadoConexion + Indicadores)")
        return layout_header
