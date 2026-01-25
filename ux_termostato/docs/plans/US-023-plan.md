# Plan de Implementación - US-023: UICompositor

## Información de la Historia

- **ID:** US-023
- **Título:** Implementar UICompositor
- **Puntos:** 3
- **Prioridad:** Alta
- **Épica:** Arquitectura e Integración
- **Estado:** En Desarrollo
- **Branch:** `development/simulador-ux-US-023`

---

## Descripción

**Como** desarrollador del sistema
**Quiero** ensamblar todos los paneles en un layout coherente
**Para** tener la UI completa del termostato

---

## Criterios de Aceptación

- [x] Clase `UICompositor` recibe dict de paneles ✅
- [x] Método `crear_layout() -> QWidget` retorna widget completo ✅
- [x] Layout vertical principal con QVBoxLayout ✅
- [x] Header horizontal (EstadoConexion + Indicadores) ✅
- [x] Espaciado entre secciones: 12px ✅
- [x] Márgenes del widget principal: 15px ✅
- [x] Tamaño mínimo: 500x700 ✅
- [x] Tamaño preferido: 600x800 ✅
- [x] Sin lógica de negocio (solo layout) ✅
- [x] Validación de paneles requeridos ✅
- [ ] Tests unitarios (100% coverage)
- [ ] Pylint ≥ 8.0

---

## Estructura del Layout

```
┌─────────────────────────────────────┐
│ HEADER                              │
│ ┌─────────────┬──────────────────┐ │
│ │EstadoConex  │  Indicadores     │ │  ← US-015 + US-003
│ └─────────────┴──────────────────┘ │
├─────────────────────────────────────┤
│          DISPLAY LCD                │  ← US-001
│         25.5 °C                     │
│      Temperatura Ambiente           │
├─────────────────────────────────────┤
│ CLIMATIZADOR                        │  ← US-002
│  [🔥]    [🌬️]    [❄️]             │
├─────────────────────────────────────┤
│ POWER                               │  ← US-007/008
│        [⚡ APAGAR]                  │
├─────────────────────────────────────┤
│ CONTROL TEMPERATURA                 │  ← US-004/005
│    [▲ SUBIR]  [▼ BAJAR]           │
├─────────────────────────────────────┤
│ SELECTOR VISTA                      │  ← US-011
│  [Toggle: Ambiente / Deseada]      │
├─────────────────────────────────────┤
│ CONFIGURACIÓN                       │  ← US-013
│  IP: [192.168.1.50] [Aplicar]      │
└─────────────────────────────────────┘
```

---

## Componentes a Implementar

### 1. UICompositor

**Archivo:** `app/presentacion/ui_compositor.py`

**Interfaz:**
```python
class UICompositor:
    def __init__(self, paneles: dict[str, tuple]) -> None:
        """
        Args:
            paneles: Dict con tuplas (modelo, vista, controlador)
                - 'display': (DisplayModelo, DisplayVista, DisplayControlador)
                - 'climatizador': (...)
                - 'indicadores': (...)
                - 'power': (...)
                - 'control_temp': (...)
                - 'selector_vista': (...)
                - 'estado_conexion': (...)
                - 'conexion': (...)
        """

    def crear_layout(self) -> QWidget:
        """Crea y retorna el widget con layout completo."""
```

**Responsabilidades:**
- Extraer vistas del dict de paneles
- Crear layout principal (QVBoxLayout)
- Crear header horizontal (QHBoxLayout)
- Ensamblar todos los paneles en orden
- Configurar espaciado y márgenes
- Configurar tamaño mínimo/preferido
- **NO contiene lógica de negocio**

---

## Tasks de Implementación

### Fase 1: Implementación ✅

- [x] **Task 1.1:** Crear estructura básica de UICompositor (30 min)
  - [x] Clase con constructor que recibe dict de paneles
  - [x] Validación de paneles requeridos
  - [x] Imports necesarios de PyQt6

- [x] **Task 1.2:** Implementar método `crear_layout()` (45 min)
  - [x] Crear widget central
  - [x] Crear layout vertical principal
  - [x] Configurar márgenes y espaciado

- [x] **Task 1.3:** Implementar header horizontal (30 min)
  - [x] Layout horizontal para header
  - [x] EstadoConexion a la izquierda
  - [x] addStretch() para separar
  - [x] Indicadores a la derecha

- [x] **Task 1.4:** Ensamblar paneles restantes (30 min)
  - [x] Display LCD
  - [x] Climatizador
  - [x] Power
  - [x] ControlTemp
  - [x] SelectorVista
  - [x] Conexion

- [x] **Task 1.5:** Configurar tamaño del widget (15 min)
  - [x] setMinimumSize(500, 700)
  - [x] resize(600, 800)

**Subtotal Implementación:** ~2.5 horas

---

### Fase 2: Tests Unitarios ✅

- [x] **Task 2.1:** Setup de fixtures (30 min)
  - [x] Fixture `qapp` (QApplication)
  - [x] Fixture `todos_paneles` con todos los paneles MVC
  - [x] Fixtures de selector_vista, estado_conexion, conexion

- [x] **Task 2.2:** Tests de creación (45 min)
  - [x] test_crear_compositor_exitoso()
  - [x] test_compositor_almacena_paneles()
  - [x] test_crear_compositor_con_paneles_vacios_falla()

- [x] **Task 2.3:** Tests de validación (1 hora)
  - [x] test_falta_panel_display()
  - [x] test_falta_panel_climatizador()
  - [x] test_faltan_multiples_paneles()
  - [x] test_paneles_requeridos_definidos()

- [x] **Task 2.4:** Tests de extracción de vistas (45 min)
  - [x] test_extraer_vista_display()
  - [x] test_extraer_vista_de_cada_panel()
  - [x] test_extraer_vista_tupla_invalida()
  - [x] test_extraer_vista_no_es_widget()

- [x] **Task 2.5:** Tests de layout (1 hora)
  - [x] test_crear_layout_retorna_widget()
  - [x] test_widget_tiene_layout_vertical()
  - [x] test_layout_tiene_margenes_correctos()
  - [x] test_layout_tiene_espaciado_correcto()
  - [x] test_layout_contiene_todos_paneles()

- [x] **Task 2.6:** Tests de header (30 min)
  - [x] test_crear_header_retorna_layout()
  - [x] test_header_tiene_espaciado()
  - [x] test_header_contiene_estado_conexion_e_indicadores()

- [x] **Task 2.7:** Tests de tamaño (30 min)
  - [x] test_widget_tiene_tamano_minimo()
  - [x] test_widget_tiene_tamano_inicial()

- [x] **Task 2.8:** Tests de integración (30 min)
  - [x] test_multiples_llamadas_crear_layout()
  - [x] test_layout_completo_funcional()
  - [x] test_orden_paneles_en_layout()

**Subtotal Tests:** ~3 horas

---

### Fase 3: Quality Gates ✅

- [x] **Task 3.1:** Ejecutar tests (15 min)
  ```bash
  pytest tests/test_ui_compositor.py -v --cov=app/presentacion/ui_compositor.py
  ```
  - [x] Coverage: **100%** ✅

- [x] **Task 3.2:** Ejecutar pylint (15 min)
  ```bash
  pylint app/presentacion/ui_compositor.py
  ```
  - [x] Score: **10.00/10** ✅

- [x] **Task 3.3:** Verificar métricas (15 min)
  ```bash
  radon cc app/presentacion/ui_compositor.py -a
  radon mi app/presentacion/ui_compositor.py
  ```
  - [x] CC: **2.33** (A) - Objetivo ≤ 10 ✅
  - [x] MI: **A** (Excelente) - Objetivo > 20 ✅

**Subtotal Quality:** ~45 min

---

### Fase 4: Git Workflow 🔲

- [ ] **Task 4.1:** Commit implementación (10 min)
  ```bash
  git add app/presentacion/ui_compositor.py
  git commit -m "feat(US-023): implementar UICompositor"
  ```

- [ ] **Task 4.2:** Commit tests (10 min)
  ```bash
  git add tests/test_ui_compositor.py tests/conftest.py
  git commit -m "test(US-023): agregar tests unitarios UICompositor"
  ```

- [ ] **Task 4.3:** Push y crear PR (10 min)
  ```bash
  git push origin development/simulador-ux-US-023
  gh pr create --title "US-023: UICompositor" --body "..."
  ```

**Subtotal Git:** ~30 min

---

## Estimación Total

| Fase | Duración Estimada |
|------|-------------------|
| Implementación | 2.5 horas |
| Tests Unitarios | 3.0 horas |
| Quality Gates | 0.75 horas |
| Git Workflow | 0.5 horas |
| **TOTAL** | **6.75 horas** |

---

## Dependencias

### Requeridas (Completadas ✅)
- ✅ US-001: Panel Display
- ✅ US-002: Panel Climatizador
- ✅ US-003: Panel Indicadores
- ✅ US-007: Panel Power
- ✅ US-004/005/006: Panel ControlTemp
- ✅ US-011: Panel SelectorVista
- ✅ US-013: Panel Conexion
- ✅ US-015: Panel EstadoConexion
- ✅ US-022: Factory (método `crear_todos_paneles()`)

### Bloquea
- 🔲 US-024: VentanaPrincipal (necesita UICompositor)
- 🔲 US-025: run.py (integración final)

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Layout no se ve bien visualmente | Media | Alto | Inspección manual, ajustar espaciado |
| Paneles no se dimensionan correctamente | Baja | Medio | Usar stretch factors apropiados |
| Tests requieren setup complejo de PyQt | Media | Bajo | Usar mocks para vistas |

---

## Notas de Implementación

### Patrón de Referencia
El compositor debe seguir el patrón de `simulador_temperatura/app/presentacion/ui_compositor.py`:
- Recibe controladores/paneles en constructor
- Método público `crear_layout()` ensambla UI
- Solo responsable del layout, sin lógica
- Usa `addWidget`, `addLayout`, `addStretch`

### Diferencias con Simuladores
- **ux_termostato:** 8 paneles (vs 4 en simuladores)
- **Header horizontal:** EstadoConexion + Indicadores (nuevo)
- **Layout más complejo:** Más secciones verticales
- **No tiene gráfico:** Layout completamente vertical (no horizontal)

### Validaciones
El compositor debe validar que el dict de paneles contenga todas las claves:
```python
PANELES_REQUERIDOS = [
    "display", "climatizador", "indicadores", "power",
    "control_temp", "selector_vista", "estado_conexion", "conexion"
]
```

---

## Checklist de Progreso

### Implementación
- [x] Estructura básica de UICompositor
- [x] Método `crear_layout()`
- [x] Header horizontal
- [x] Paneles ensamblados en orden
- [x] Configuración de tamaño

### Tests
- [x] Fixtures de conftest.py (selector_vista, estado_conexion, conexion, todos_paneles)
- [x] Tests de creación (3 tests)
- [x] Tests de validación (4 tests)
- [x] Tests de extracción de vistas (4 tests)
- [x] Tests de layout (5 tests)
- [x] Tests de header (3 tests)
- [x] Tests de tamaño (2 tests)
- [x] Tests de integración (3 tests)

### Quality
- [x] Coverage: **100%** ✅
- [x] Pylint: **10.00/10** ✅
- [x] CC: **2.33** ✅
- [x] MI: **A** ✅

### Git
- [ ] Branch creada
- [ ] Commit de implementación
- [ ] Commit de tests
- [ ] PR creada
- [ ] PR mergeada a main

---

## Resultados Finales

**Métricas de Calidad:**
- Coverage: **100%** (59 statements, 0 missed) ✅
- Pylint: **10.00/10** ✅
- CC: **2.33** (A - Muy bajo) ✅
- MI: **A** (Excelente mantenibilidad) ✅

**Tests:**
- Total: **24 tests**
- Pasados: **24/24** (100%)
- Clases de tests: 6 (Creacion, Validacion, ExtraerVista, Layout, Header, Tamaño, Integración)

**Archivos Creados:**
- `app/presentacion/ui_compositor.py` (195 líneas)
- `app/presentacion/__init__.py` (exports)
- `tests/test_ui_compositor.py` (424 líneas, 24 tests)
- `tests/conftest.py` (fixtures agregadas: selector_vista, estado_conexion, conexion, todos_paneles)

**Estado:** ✅ COMPLETADO

---

**Última actualización:** 2026-01-25
**Responsable:** Claude Code + Victor Valotto
