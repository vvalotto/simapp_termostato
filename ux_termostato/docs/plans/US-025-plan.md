# Plan de Implementación - US-025: Entry Point (run.py)

## Información de la Historia

- **ID:** US-025
- **Título:** Integración Final - run.py
- **Puntos:** 5
- **Prioridad:** CRÍTICA
- **Épica:** Arquitectura e Integración
- **Estado:** En Desarrollo
- **Branch:** `development/simulador-ux-US025`

---

## Descripción

**Como** usuario final
**Quiero** ejecutar `python run.py`
**Para** iniciar la aplicación UX Desktop completa

---

## Criterios de Aceptación

- [ ] Script ejecutable con shebang `#!/usr/bin/env python3`
- [ ] Setup de logging con formato estándar
- [ ] Carga de configuración (config.json + .env)
- [ ] Creación de QApplication
- [ ] Factory + VentanaPrincipalUX
- [ ] Event loop con sys.exit()
- [ ] Manejo de excepciones (KeyboardInterrupt, errores fatales)
- [ ] Exit codes apropiados (0, 1, 130)
- [ ] Logging completo y útil
- [ ] `python run.py` inicia la aplicación sin errores

---

## Estructura del Entry Point

```python
#!/usr/bin/env python3
"""Entry point UX Termostato Desktop"""

import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from app.configuracion import ConfigUX
from app.factory import ComponenteFactoryUX
from app.presentacion import VentanaPrincipalUX

# Logging
logging.basicConfig(...)
logger = logging.getLogger(__name__)

def main():
    try:
        # 1. Cargar config
        # 2. Crear QApplication
        # 3. Crear Factory
        # 4. Crear VentanaPrincipalUX
        # 5. Iniciar ventana
        # 6. Event loop
    except KeyboardInterrupt:
        logger.info("Interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        logger.error("Error fatal: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Tasks de Implementación

### Fase 1: Implementación ✅

- [x] **Task 1.1:** Estructura básica del script (15 min)
  - [x] Shebang
  - [x] Docstring
  - [x] Imports necesarios
  - [x] Setup de path

- [x] **Task 1.2:** Setup de logging (15 min)
  - [x] logging.basicConfig con formato estándar
  - [x] Logger del módulo

- [x] **Task 1.3:** Carga de configuración (30 min)
  - [x] Leer config.json con valores por defecto
  - [x] ConfigUX con parámetros
  - [x] Logging de config cargada

- [x] **Task 1.4:** Creación de QApplication (15 min)
  - [x] Verificar instancia existente
  - [x] Crear si no existe
  - [x] setApplicationName
  - [x] setOrganizationName

- [x] **Task 1.5:** Creación de componentes (20 min)
  - [x] ComponenteFactoryUX con config
  - [x] VentanaPrincipalUX con factory
  - [x] ventana.iniciar()

- [x] **Task 1.6:** Event loop (10 min)
  - [x] sys.exit(app.exec())

- [x] **Task 1.7:** Manejo de excepciones (30 min)
  - [x] Try/catch global
  - [x] KeyboardInterrupt → sys.exit(0)
  - [x] Exception → sys.exit(1)
  - [x] Logging apropiado

**Subtotal Implementación:** ~2.5 horas

---

### Fase 2: Tests ✅

- [x] **Task 2.1:** Tests básicos (1 hora)
  - [x] Test de imports
  - [x] Test de configuración
  - [x] Test de creación de factory
  - [x] Verificación de sintaxis

**Subtotal Tests:** ~1 hora

---

### Fase 3: Validación Manual 🔲

- [x] **Task 3.1:** Tests básicos automatizados
  - [x] Imports correctos
  - [x] Configuración carga correctamente
  - [x] Factory se crea sin errores
  - [x] Sintaxis Python válida
  - [x] Script es ejecutable (chmod +x)
- [ ] **Task 3.2:** Validación manual completa (pendiente)
  - [ ] `python run.py` inicia sin errores
  - [ ] Ventana se muestra correctamente
  - [ ] Paneles visibles y funcionales
  - [ ] Servidor escuchando puerto 14001
  - [ ] Cierre con Ctrl+C funciona
  - [ ] Cierre con botón X funciona

**Subtotal Validación:** ~30 min

---

### Fase 4: Git Workflow 🔲

- [ ] **Task 4.1:** Commit (10 min)
- [ ] **Task 4.2:** Push y PR (10 min)

**Subtotal Git:** ~20 min

---

## Resultados de Quality Gates

**Pylint:** 10.00/10 ✅
**Sintaxis:** Válida ✅
**Ejecutable:** Correcto (chmod +x) ✅
**Tests Básicos:** Pasando ✅
  - Imports: OK
  - Configuración: OK
  - Factory: OK

---

## Estimación Total

| Fase | Duración Estimada |
|------|-------------------|
| Implementación | 2.5 horas |
| Tests | 1.0 hora |
| Validación Manual | 0.5 horas |
| Git Workflow | 0.33 horas |
| **TOTAL** | **4.33 horas** |

---

## Dependencias

### Requeridas (Completadas ✅)
- ✅ US-020: Capa Dominio
- ✅ US-021: Capa Comunicación
- ✅ US-022: Factory + Coordinator
- ✅ US-023: UICompositor
- ✅ US-024: VentanaPrincipalUX

### Bloquea
- Ninguna - **US-025 es la última historia del proyecto** 🎯

---

## Diferencias con Simuladores

**Simuladores:**
- AplicacionSimulador es wrapper complejo
- Maneja conexión/desconexión manual
- Callbacks para conectar/desconectar
- Servicio de envío separado

**ux_termostato:**
- VentanaPrincipalUX maneja todo el ciclo de vida
- Servidor se inicia automáticamente en ventana.iniciar()
- No hay callbacks de conexión manual
- **run.py es MUY simple**: config → factory → ventana → event loop

---

## Checklist de Progreso

### Implementación
- [x] Shebang y estructura básica
- [x] Setup de logging
- [x] Carga de configuración
- [x] Creación de QApplication
- [x] Factory + VentanaPrincipalUX
- [x] Event loop
- [x] Manejo de excepciones

### Tests
- [x] Tests básicos implementados
- [x] Tests pasando

### Validación
- [x] Tests automatizados pasando
- [ ] Validación manual completa (pendiente)

### Git
- [ ] Branch creada ✅
- [ ] Commit realizado
- [ ] PR creada
- [ ] PR mergeada a main

---

## Resultados Finales

**Métricas de Calidad:**
- Pylint: 10.00/10 ✅
- Sintaxis: Válida ✅
- Tests básicos: Pasando ✅

**Estado:** ✅ Implementación Completa (pendiente validación manual)

---

**Última actualización:** 2026-01-25
**Responsable:** Claude Code + Victor Valotto
