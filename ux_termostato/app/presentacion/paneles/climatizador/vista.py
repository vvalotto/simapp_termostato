"""
Vista del panel Climatizador.

Este módulo define la vista MVC que renderiza los 3 indicadores del estado
del climatizador: Calor (🔥), Reposo (🌬️) y Frío (❄️).
"""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .modelo import (
    ClimatizadorModelo,
    MODO_CALENTANDO,
    MODO_ENFRIANDO,
    MODO_REPOSO,
)


class ClimatizadorVista(QWidget):
    """
    Vista del panel de estado del climatizador.

    Renderiza 3 indicadores visuales:
    - Calor 🔥: Naranja, con animación pulsante cuando activo
    - Reposo 🌬️: Verde, sin animación cuando activo
    - Frío ❄️: Azul, con animación pulsante cuando activo

    Solo un indicador está activo a la vez. Los inactivos se muestran en gris.
    """

    def __init__(self):
        """Inicializa la vista del climatizador."""
        super().__init__()
        self._setup_ui()
        self._aplicar_estilos()

    def _setup_ui(self):
        """Configura los widgets y layout de la vista."""
        # Layout principal horizontal
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Crear los 3 indicadores
        self.indicador_calor = self._crear_indicador("🔥", "Calor", "calor")
        self.indicador_reposo = self._crear_indicador("🌬️", "Reposo", "reposo")
        self.indicador_frio = self._crear_indicador("❄️", "Frío", "frio")

        # Agregar indicadores al layout
        layout.addWidget(self.indicador_calor)
        layout.addWidget(self.indicador_reposo)
        layout.addWidget(self.indicador_frio)

        self.setLayout(layout)
        self.setObjectName("panelClimatizador")

    def _crear_indicador(self, emoji: str, texto: str, nombre: str) -> QWidget:
        """
        Crea un widget indicador con icono y texto.

        Args:
            emoji: Icono emoji del indicador
            texto: Texto descriptivo
            nombre: Nombre para identificación (calor, reposo, frio)

        Returns:
            QWidget configurado como indicador
        """
        # Widget contenedor
        indicador = QWidget()
        indicador.setObjectName(f"indicador_{nombre}")

        # Layout vertical
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label del emoji (icono)
        label_icono = QLabel(emoji)
        label_icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_icono.setObjectName(f"icono_{nombre}")
        font_icono = QFont()
        font_icono.setPointSize(48)
        label_icono.setFont(font_icono)

        # Label del texto
        label_texto = QLabel(texto)
        label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_texto.setObjectName(f"texto_{nombre}")
        font_texto = QFont()
        font_texto.setPointSize(14)
        font_texto.setBold(True)
        label_texto.setFont(font_texto)

        # Agregar al layout
        layout.addWidget(label_icono)
        layout.addWidget(label_texto)

        indicador.setLayout(layout)
        return indicador

    def _aplicar_estilos(self):
        """Aplica estilos CSS a los indicadores."""
        self.setStyleSheet("""
            QWidget#panelClimatizador {
                background: transparent;
            }

            /* Estilos base de indicadores */
            QWidget[id^="indicador_"] {
                border: 2px solid #64748b;
                border-radius: 12px;
                background: rgba(100, 116, 139, 0.3);
                min-width: 140px;
                min-height: 160px;
            }

            /* Indicador Calor - Activo */
            QWidget#indicador_calor[activo="true"] {
                border: 3px solid #f97316;
                background: rgba(249, 115, 22, 0.2);
            }

            /* Indicador Reposo - Activo */
            QWidget#indicador_reposo[activo="true"] {
                border: 3px solid #22c55e;
                background: rgba(34, 197, 94, 0.2);
            }

            /* Indicador Frío - Activo */
            QWidget#indicador_frio[activo="true"] {
                border: 3px solid #3b82f6;
                background: rgba(59, 130, 246, 0.2);
            }

            /* Texto de indicadores */
            QLabel[id^="texto_"] {
                color: #e2e8f0;
                background: transparent;
            }

            /* Iconos */
            QLabel[id^="icono_"] {
                background: transparent;
            }
        """)

    def actualizar(self, modelo: ClimatizadorModelo):
        """
        Actualiza la vista con los datos del modelo.

        Args:
            modelo: Instancia de ClimatizadorModelo con el estado actual
        """
        # Determinar qué indicador está activo
        if not modelo.encendido:
            # Todos inactivos si está apagado
            self._set_indicador_activo(None)
        elif modelo.modo == MODO_CALENTANDO:
            self._set_indicador_activo("calor")
        elif modelo.modo == MODO_ENFRIANDO:
            self._set_indicador_activo("frio")
        elif modelo.modo == MODO_REPOSO:
            self._set_indicador_activo("reposo")
        else:
            # Modo desconocido, todos inactivos
            self._set_indicador_activo(None)

    def _set_indicador_activo(self, indicador_nombre: str | None):
        """
        Establece qué indicador está activo.

        Args:
            indicador_nombre: Nombre del indicador activo ("calor", "reposo", "frio")
                            o None para todos inactivos
        """
        # Desactivar todos primero
        self.indicador_calor.setProperty("activo", "false")
        self.indicador_reposo.setProperty("activo", "false")
        self.indicador_frio.setProperty("activo", "false")

        # Detener animaciones
        self._detener_animacion(self.indicador_calor)
        self._detener_animacion(self.indicador_reposo)
        self._detener_animacion(self.indicador_frio)

        # Activar el indicador correspondiente
        if indicador_nombre == "calor":
            self.indicador_calor.setProperty("activo", "true")
            self._iniciar_animacion(self.indicador_calor)
        elif indicador_nombre == "reposo":
            self.indicador_reposo.setProperty("activo", "true")
            # Reposo NO tiene animación
        elif indicador_nombre == "frio":
            self.indicador_frio.setProperty("activo", "true")
            self._iniciar_animacion(self.indicador_frio)

        # Forzar actualización de estilos
        self.indicador_calor.style().unpolish(self.indicador_calor)
        self.indicador_calor.style().polish(self.indicador_calor)
        self.indicador_reposo.style().unpolish(self.indicador_reposo)
        self.indicador_reposo.style().polish(self.indicador_reposo)
        self.indicador_frio.style().unpolish(self.indicador_frio)
        self.indicador_frio.style().polish(self.indicador_frio)

    def _iniciar_animacion(self, widget: QWidget):
        """
        Inicia la animación pulsante en un widget.

        Args:
            widget: Widget al que aplicar la animación
        """
        # Guardar referencia para poder detenerla después
        if not hasattr(widget, '_animation'):
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

            animation = QPropertyAnimation(widget, b"windowOpacity")
            animation.setDuration(2000)  # 2 segundos
            animation.setStartValue(1.0)
            animation.setKeyValueAt(0.5, 0.7)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.setLoopCount(-1)  # Infinito
            widget._animation = animation

        widget._animation.start()

    def _detener_animacion(self, widget: QWidget):
        """
        Detiene la animación pulsante en un widget.

        Args:
            widget: Widget cuya animación detener
        """
        if hasattr(widget, '_animation'):
            widget._animation.stop()
            widget.setWindowOpacity(1.0)  # Restaurar opacidad completa
