"""Capa de presentación del simulador de batería.

Contiene la UI con arquitectura MVC:
- UIPrincipalCompositor: Composición del layout principal
- paneles/: Paneles MVC (estado, control, conexion)
"""
from app.presentacion.ui_compositor import UIPrincipalCompositor

__all__ = ['UIPrincipalCompositor']
