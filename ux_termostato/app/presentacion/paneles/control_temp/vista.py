"""
Vista del panel Control de Temperatura.

Este módulo define la vista MVC que renderiza los botones de control
de temperatura (aumentar/disminuir) con estilos condicionales.
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .modelo import ControlTempModelo


class ControlTempVista(QWidget):
    """
    Vista del panel de control de temperatura.

    Renderiza:
    - Botón "SUBIR" (rojo, ▲) para aumentar temperatura
    - Botón "BAJAR" (azul, ▼) para disminuir temperatura
    - Label central con temperatura deseada
    - Estados habilitados/deshabilitados según modelo
    - Feedback visual al presionar
    """

    def __init__(self):
        """Inicializa la vista del panel de control de temperatura."""
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Configura los widgets y layout de la vista."""
        # Layout principal vertical
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(10)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # Label de título
        self.label_titulo = QLabel("Control de Temperatura")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_titulo = QFont()
        font_titulo.setPointSize(10)
        font_titulo.setBold(True)
        self.label_titulo.setFont(font_titulo)
        self.label_titulo.setStyleSheet("color: #94a3b8;")  # slate-400

        # Label de temperatura deseada
        self.label_temp = QLabel("--.-°C")
        self.label_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_temp = QFont()
        font_temp.setPointSize(24)
        font_temp.setBold(True)
        self.label_temp.setFont(font_temp)
        self.label_temp.setStyleSheet("color: #e2e8f0; margin: 10px 0;")  # slate-200

        # Layout horizontal para botones
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(15)

        # Botón BAJAR (azul, izquierda)
        self.btn_bajar = QPushButton("▼\nBAJAR")
        self.btn_bajar.setObjectName("btnBajar")
        self.btn_bajar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bajar.setToolTip("Disminuir temperatura en 0.5°C")

        # Configurar fuente del botón
        font_btn = QFont()
        font_btn.setPointSize(12)
        font_btn.setBold(True)
        self.btn_bajar.setFont(font_btn)

        # Configurar tamaño
        self.btn_bajar.setMinimumHeight(80)
        self.btn_bajar.setMinimumWidth(120)

        # Botón SUBIR (rojo, derecha)
        self.btn_subir = QPushButton("▲\nSUBIR")
        self.btn_subir.setObjectName("btnSubir")
        self.btn_subir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_subir.setToolTip("Aumentar temperatura en 0.5°C")
        self.btn_subir.setFont(font_btn)
        self.btn_subir.setMinimumHeight(80)
        self.btn_subir.setMinimumWidth(120)

        # Agregar botones al layout horizontal
        layout_botones.addWidget(self.btn_bajar)
        layout_botones.addWidget(self.btn_subir)

        # Agregar todo al layout principal
        layout_principal.addWidget(self.label_titulo)
        layout_principal.addWidget(self.label_temp)
        layout_principal.addLayout(layout_botones)

        self.setLayout(layout_principal)

        # Aplicar estilos iniciales (deshabilitados)
        self._aplicar_estilo_bajar(habilitado=False)
        self._aplicar_estilo_subir(habilitado=False)

    def _aplicar_estilo_subir(self, habilitado: bool):
        """
        Aplica estilos al botón SUBIR según estado.

        Args:
            habilitado: True si el botón debe estar habilitado
        """
        if habilitado:
            self.btn_subir.setStyleSheet("""
                QPushButton#btnSubir {
                    background-color: #dc2626;  /* red-600 */
                    color: white;
                    border: 2px solid #b91c1c;  /* red-700 */
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }

                QPushButton#btnSubir:hover {
                    background-color: #b91c1c;  /* red-700 */
                    border-color: #991b1b;      /* red-800 */
                }

                QPushButton#btnSubir:pressed {
                    background-color: #991b1b;  /* red-800 */
                }

                QPushButton#btnSubir:disabled {
                    background-color: #475569;  /* slate-600 */
                    border-color: #334155;      /* slate-700 */
                    color: #64748b;             /* slate-500 */
                    cursor: not-allowed;
                }
            """)
            self.btn_subir.setEnabled(True)
        else:
            self.btn_subir.setStyleSheet("""
                QPushButton#btnSubir {
                    background-color: #475569;  /* slate-600 */
                    color: #64748b;             /* slate-500 */
                    border: 2px solid #334155;  /* slate-700 */
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            self.btn_subir.setEnabled(False)

    def _aplicar_estilo_bajar(self, habilitado: bool):
        """
        Aplica estilos al botón BAJAR según estado.

        Args:
            habilitado: True si el botón debe estar habilitado
        """
        if habilitado:
            self.btn_bajar.setStyleSheet("""
                QPushButton#btnBajar {
                    background-color: #2563eb;  /* blue-600 */
                    color: white;
                    border: 2px solid #1d4ed8;  /* blue-700 */
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }

                QPushButton#btnBajar:hover {
                    background-color: #1d4ed8;  /* blue-700 */
                    border-color: #1e40af;      /* blue-800 */
                }

                QPushButton#btnBajar:pressed {
                    background-color: #1e40af;  /* blue-800 */
                }

                QPushButton#btnBajar:disabled {
                    background-color: #475569;  /* slate-600 */
                    border-color: #334155;      /* slate-700 */
                    color: #64748b;             /* slate-500 */
                    cursor: not-allowed;
                }
            """)
            self.btn_bajar.setEnabled(True)
        else:
            self.btn_bajar.setStyleSheet("""
                QPushButton#btnBajar {
                    background-color: #475569;  /* slate-600 */
                    color: #64748b;             /* slate-500 */
                    border: 2px solid #334155;  /* slate-700 */
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
            self.btn_bajar.setEnabled(False)

    def actualizar(self, modelo: ControlTempModelo):
        """
        Actualiza la vista con los datos del modelo.

        Actualiza:
        - Label de temperatura deseada
        - Estados habilitados/deshabilitados de los botones
        - Estilos condicionales según límites alcanzados

        Args:
            modelo: Instancia de ControlTempModelo con el estado actual
        """
        # Actualizar label de temperatura
        if modelo.habilitado:
            self.label_temp.setText(f"{modelo.temperatura_deseada:.1f}°C")
        else:
            self.label_temp.setText("--.-°C")

        # Actualizar botón SUBIR
        puede_subir = modelo.puede_aumentar()
        self._aplicar_estilo_subir(habilitado=puede_subir)

        # Actualizar botón BAJAR
        puede_bajar = modelo.puede_disminuir()
        self._aplicar_estilo_bajar(habilitado=puede_bajar)
