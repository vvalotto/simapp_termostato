"""Paneles MVC del simulador de batería.

Cada panel sigue el patrón MVC:
- modelo.py: Dataclass con datos del panel
- vista.py: QWidget con UI
- controlador.py: QObject que coordina modelo y vista
"""
from app.presentacion.paneles.base import ModeloBase, VistaBase, ControladorBase

__all__ = ['ModeloBase', 'VistaBase', 'ControladorBase']
