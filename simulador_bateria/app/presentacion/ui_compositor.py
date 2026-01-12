"""Compositor de UI principal del simulador de batería.

Compone el layout visual a partir de controladores ya configurados.
Solo responsable del layout, sin lógica de negocio.
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
)


class UIPrincipalCompositor(QMainWindow):
    """Ventana principal que compone los paneles MVC.

    Recibe controladores pre-configurados y extrae sus vistas
    para componer el layout. No contiene lógica de negocio.

    Layout:
    ┌────────────────────────────────────┐
    │         Panel Estado               │
    │    (voltaje actual + porcentaje)   │
    ├────────────────────────────────────┤
    │         Panel Control              │
    │      (slider de voltaje)           │
    ├────────────────────────────────────┤
    │         Panel Conexión             │
    │   (IP, puerto, conectar/desconec)  │
    └────────────────────────────────────┘
    """

    def __init__(
        self,
        ctrl_estado,
        ctrl_control,
        ctrl_conexion,
        parent: Optional[QWidget] = None
    ) -> None:
        """Inicializa el compositor con controladores.

        Args:
            ctrl_estado: PanelEstadoControlador con vista de estado.
            ctrl_control: ControlBateriaControlador con vista de control.
            ctrl_conexion: PanelConexionControlador con vista de conexión.
            parent: Widget padre opcional.
        """
        super().__init__(parent)
        self._ctrl_estado = ctrl_estado
        self._ctrl_control = ctrl_control
        self._ctrl_conexion = ctrl_conexion

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Simulador de Batería - ISSE")
        self.setMinimumSize(400, 300)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal vertical
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Agregar vistas de los controladores
        layout.addWidget(self._ctrl_estado.vista)
        layout.addWidget(self._ctrl_control.vista)
        layout.addWidget(self._ctrl_conexion.vista)

        # Stretch al final para empujar todo hacia arriba
        layout.addStretch()
