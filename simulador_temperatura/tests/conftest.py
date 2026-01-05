"""Configuración de pytest para el Simulador de Temperatura."""
import sys
from pathlib import Path

# Agregar el directorio raíz del producto al PYTHONPATH
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
