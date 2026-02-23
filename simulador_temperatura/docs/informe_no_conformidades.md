# Informe de No-Conformidades — Simulador de Temperatura

**Fecha:** 2026-02-23
**Revisor:** Claude Code (claude-sonnet-4-6)
**Versión analizada:** branch `main`, commit `c287b05`
**Herramientas:** pylint 3.x, pytest-cov, radon, inspección manual de código

---

## Resumen Ejecutivo

| Categoría | Crítica | Mayor | Menor |
|-----------|---------|-------|-------|
| Cobertura de tests | 3 | 1 | — |
| Código legado / duplicado | — | 2 | — |
| Imports / variables no usados | — | — | 7 |
| Demasiados argumentos | — | 2 | 4 |
| Atributos fuera de `__init__` | — | 1 | — |
| `pass` innecesarios | — | — | 3 |
| Error E1101 pyqtgraph | — | 1 | — |
| Docstrings faltantes | — | — | 2 |
| **TOTAL** | **3** | **7** | **16** |

Las métricas automáticas (Pylint 9.52/10, CC 1.36, MI 70.10) cumplen los quality gates. Las no-conformidades identificadas son en su mayoría problemas de diseño y deuda técnica que las métricas agregadas no detectan.

---

## Severidad: CRÍTICA

### NC-ST-001 — `coordinator.py` sin cobertura de tests (0%)

**Archivo:** `app/coordinator.py`
**Líneas:** 7–182 (79 líneas ejecutables)
**Incumplimiento:** Quality gate: cobertura ≥ 95%

`SimuladorCoordinator` es la clase que orquesta todas las señales entre componentes (dominio, comunicación, presentación). Es el corazón de la arquitectura pero **no tiene ningún test unitario**. Una regresión en el coordinator podría romper el flujo completo de la aplicación sin que los tests lo detecten.

```
app/coordinator.py    79     79     0%   7-182
```

**Acción recomendada:** Crear `tests/test_coordinator.py` con fixtures que usen mocks de los 4 controladores y el generador, verificando que las señales se conectan y propagan correctamente.

---

### NC-ST-002 — `factory.py` sin cobertura de tests (0%)

**Archivo:** `app/factory.py`
**Líneas:** 7–161 (31 líneas ejecutables reportadas)
**Incumplimiento:** Quality gate: cobertura ≥ 95%

`ComponenteFactory` centraliza la creación de todos los componentes con configuración consistente. Con 0% de cobertura, no hay garantía de que los componentes se instancien correctamente ni que los parámetros de configuración se apliquen bien.

```
app/factory.py        31     31     0%   7-161
```

**Acción recomendada:** Crear `tests/test_factory.py` verificando que cada método `crear_*` retorna el tipo correcto y aplica la configuración recibida.

---

### NC-ST-003 — Cobertura total por debajo del objetivo (89% vs ≥95%)

**Incumplimiento:** Quality gate: cobertura ≥ 95%

La cobertura total del módulo `app/` es **89%**, seis puntos por debajo del objetivo. Los principales contribuyentes al déficit:

| Archivo | Cobertura | Líneas sin cubrir |
|---------|-----------|-------------------|
| `app/coordinator.py` | 0% | 79 |
| `app/factory.py` | 0% | 31 |
| `app/presentacion/ui_compositor.py` | 46% | 29 |
| `app/presentacion/ui_principal.py` | 89% | 18 |
| `app/presentacion/paneles/grafico/vista.py` | 90% | 7 |

**Acción recomendada:** Atacar NC-ST-001 y NC-ST-002 primero (recupera ~11 puntos de coverage). Luego cubrir las ramas faltantes de `ui_compositor.py`.

---

## Severidad: MAYOR

### NC-ST-004 — Tres archivos legado coexisten con la arquitectura MVC

**Archivos:**
- `app/presentacion/control_temperatura.py` (~340 líneas)
- `app/presentacion/grafico_temperatura.py` (~200 líneas)
- `app/presentacion/ui_principal.py` (~400 líneas)

Estos archivos contienen implementaciones anteriores a la refactorización MVC. Ninguno de ellos es referenciado por `run.py` ni por `ui_compositor.py` en la ruta de ejecución real. Sin embargo siguen presentes en el módulo y son cubiertos por sus propios tests (`test_control_temperatura.py`, `test_grafico_temperatura.py`, `test_ui_principal.py`).

**Problemas derivados:**
- Pylint detecta código duplicado entre el legado y el nuevo MVC (ver NC-ST-005).
- Confusión para futuros desarrolladores sobre cuál es la implementación activa.
- Tests de código inactivo inflan artificialmente el número de tests (distorsionan métricas).
- Mantener código muerto es deuda técnica que crece con cada cambio.

**Acción recomendada:** Si los archivos legacy ya no son usados, eliminarlos junto con sus tests correspondientes. Si todavía sirven como referencia, moverlos a un directorio `_legacy/` o documentar explícitamente su estado en el archivo.

---

### NC-ST-005 — Código duplicado entre legacy y MVC (R0801)

**Pylint:** R0801 (duplicate-code)

Pylint detectó dos bloques de código sustancialmente idénticos:

**Bloque 1 — `SliderConValor`:**
- `app/presentacion/control_temperatura.py:38-103` (legacy)
- `app/presentacion/paneles/control_temperatura/vista.py:24-88` (MVC)

La clase `SliderConValor` está implementada dos veces con código casi idéntico. Cualquier corrección de bug o mejora debe hacerse en ambos lugares.

**Bloque 2 — Buffer temporal del gráfico:**
- `app/presentacion/grafico_temperatura.py:138-147` (legacy)
- `app/presentacion/paneles/grafico/modelo.py:63-70` (MVC)

**Acción recomendada:** Resolver NC-ST-004 (eliminar código legacy) eliminará automáticamente esta duplicación.

---

### NC-ST-006 — Atributos `_linea_min` / `_linea_max` definidos fuera de `__init__`

**Archivo:** `app/presentacion/grafico_temperatura.py:190, 198`
**Pylint:** W0201 (attribute-defined-outside-init)

```python
# Línea 190: _linea_min se define en un método diferente a __init__
self._linea_min = self._plot_widget.plot(...)

# Línea 198: _linea_max ídem
self._linea_max = self._plot_widget.plot(...)
```

Inicializar atributos fuera del constructor viola el principio de construcción completa. Si el método que los inicializa no se llama antes de acceder a ellos, se produce `AttributeError` en tiempo de ejecución.

**Acción recomendada:** Inicializar `_linea_min` y `_linea_max` a `None` en `__init__`, luego asignarlos en el método correspondiente. Este issue pertenece al archivo legacy; si se elimina NC-ST-004, desaparece solo.

---

### NC-ST-007 — Error E1101: `pyqtgraph.Qt.QtCore` no tiene miembro `Qt`

**Archivos:**
- `app/presentacion/grafico_temperatura.py:125` (legacy)
- `app/presentacion/paneles/grafico/vista.py:91` (MVC activo)

**Pylint:** E1101 (no-member)

```python
# En grafico/vista.py:91
pg.Qt.QtCore.Qt.PenStyle  # E1101: Module has no 'Qt' member
```

Este es un **error potencial en tiempo de ejecución**. La API de pyqtgraph en la versión instalada no expone `Qt` como atributo de `pyqtgraph.Qt.QtCore`. Si esta línea se ejecuta (depende del branch de código activo), podría lanzar `AttributeError`.

**Acción recomendada:** Verificar cómo se accede al estilo de línea en la versión actual de pyqtgraph e importar directamente desde `PyQt6.QtCore import Qt`.

---

### NC-ST-008 — `ui_compositor.py` con 46% de cobertura

**Archivo:** `app/presentacion/ui_compositor.py`
**Líneas sin cubrir:** 60-69, 73-118, 125, 130, 135, 140

El método `_setup_ui()` que construye el layout de la ventana principal (la composición real de paneles) no está siendo testeado. Esto incluye toda la lógica de creación de widgets y layouts.

**Acción recomendada:** En `tests/test_ui_principal.py` existe cobertura para la clase legacy `UIPrincipal`, pero falta un test equivalente para `UIPrincipalCompositor`. Agregar un test que instancie el compositor con controladores mock y verifique el layout resultante.

---

## Severidad: MENOR

### NC-ST-009 — Imports no utilizados (W0611)

| Archivo | Línea | Import no usado |
|---------|-------|----------------|
| `app/coordinator.py` | 8 | `Callable` de `typing` |
| `paneles/conexion/controlador.py` | 13 | `ConfigPanelConexionVista` |
| `paneles/conexion/vista.py` | 14 | `EstadoConexion` |
| `paneles/control_temperatura/controlador.py` | 12 | `ModoOperacion` |
| `paneles/control_temperatura/vista.py` | 6 | `dataclass` de `dataclasses` |
| `paneles/control_temperatura/vista.py` | 22 | `ModoOperacion` |

Imports no usados aumentan el tiempo de carga y crean confusión sobre qué dependencias son reales.

**Acción recomendada:** Eliminar los imports listados.

---

### NC-ST-010 — Variable `tiempo_relativo` calculada y descartada

**Archivo:** `app/presentacion/paneles/grafico/controlador.py:65`
**Pylint:** W0612 (unused-variable)

```python
tiempo_relativo = self._modelo.agregar_punto(temperatura, timestamp)
# tiempo_relativo nunca se usa después
self._actualizar_vista()
self.punto_agregado.emit(timestamp, temperatura)
```

El valor de retorno de `agregar_punto()` (el tiempo relativo) se recibe en una variable que luego se ignora. Esto podría ser intencional (se emite `timestamp` absoluto en la señal), pero resulta confuso.

**Acción recomendada:** Si el tiempo relativo no se necesita, reemplazar por `self._modelo.agregar_punto(temperatura, timestamp)` sin asignación. Si se necesita, usarlo en `punto_agregado.emit()`.

---

### NC-ST-011 — `pass` innecesarios en métodos con docstring (W0107)

**Archivos y líneas:**

| Archivo | Línea | Contexto |
|---------|-------|---------|
| `paneles/base.py` | 25, 31, 56, 62, 112 | Clases base abstractas |
| `paneles/estado/controlador.py` | 57 | `_conectar_signals` |
| `paneles/grafico/controlador.py` | 51 | `_conectar_signals` |

En Python, un método abstracto con docstring no necesita `pass`. El `pass` es redundante cuando ya hay otro cuerpo de statement (la docstring).

```python
# Actual (redundante)
@abstractmethod
def actualizar(self, modelo: ModeloBase) -> None:
    """Actualiza la vista con datos del modelo."""
    pass  # ← innecesario

# Correcto
@abstractmethod
def actualizar(self, modelo: ModeloBase) -> None:
    """Actualiza la vista con datos del modelo."""
```

**Acción recomendada:** Eliminar los `pass` en métodos que ya tienen docstring.

---

### NC-ST-012 — Demasiados argumentos en constructores (R0913/R0917)

Los siguientes constructores superan el límite de 5 argumentos posicionales que establece pylint:

| Archivo | Línea | Args | Contexto |
|---------|-------|------|---------|
| `coordinator.py` | 40 | 6+self=7 | `SimuladorCoordinator.__init__` |
| `ui_compositor.py` | 41 | 6+self=7 | `UIPrincipalCompositor.__init__` |
| `paneles/conexion/controlador.py` | 36 | 5+self=6 | `PanelConexionControlador.__init__` |
| `paneles/control_temperatura/vista.py` | 30 | 7+self=8 | `SliderConValor.__init__` |
| `presentacion/ui_principal.py` | 203 | 7+self=8 | Legacy |
| `presentacion/control_temperatura.py` | 44 | 7+self=8 | Legacy |

Los casos en código MVC activo (`coordinator.py`, `ui_compositor.py`) tienen justificación arquitectónica (los coordinadores deben recibir todos los controladores). Sin embargo, podrían refactorizarse agrupando los controladores en un dataclass `Controladores`.

**Acción recomendada (MVC activo):** Considerar introducir un dataclass contenedor:
```python
@dataclass
class Controladores:
    estado: PanelEstadoControlador
    control: ControlTemperaturaControlador
    grafico: GraficoControlador
    conexion: PanelConexionControlador
```
Los casos en código legacy desaparecerán al resolver NC-ST-004.

---

### NC-ST-013 — Docstrings faltantes en métodos públicos (C0116)

**Archivos:**
- `app/presentacion/control_temperatura.py`: 9 métodos sin docstring (legacy)
- `app/presentacion/paneles/control_temperatura/vista.py:79, 82, 220–236`: 7 métodos sin docstring (MVC activo)

Los métodos públicos de `ControlTemperaturaVista` carecen de docstring, lo que dificulta entender su contrato sin leer la implementación.

**Acción recomendada:** Agregar docstrings a los métodos públicos de `paneles/control_temperatura/vista.py`. Los del archivo legacy se resolverán con NC-ST-004.

---

## No-Conformidades por Archivo (resumen)

```
app/coordinator.py                → NC-ST-001, NC-ST-003, NC-ST-009, NC-ST-012
app/factory.py                    → NC-ST-002, NC-ST-003
app/presentacion/control_temperatura.py  → NC-ST-004, NC-ST-005, NC-ST-012, NC-ST-013 (legacy)
app/presentacion/grafico_temperatura.py  → NC-ST-004, NC-ST-005, NC-ST-006, NC-ST-007 (legacy)
app/presentacion/ui_principal.py         → NC-ST-004, NC-ST-012 (legacy)
app/presentacion/ui_compositor.py        → NC-ST-003, NC-ST-008, NC-ST-012
app/presentacion/paneles/base.py         → NC-ST-011
app/presentacion/paneles/grafico/controlador.py  → NC-ST-010, NC-ST-011
app/presentacion/paneles/grafico/vista.py        → NC-ST-007
app/presentacion/paneles/conexion/controlador.py → NC-ST-009, NC-ST-012
app/presentacion/paneles/conexion/vista.py       → NC-ST-009
app/presentacion/paneles/control_temperatura/controlador.py → NC-ST-009
app/presentacion/paneles/control_temperatura/vista.py → NC-ST-009, NC-ST-012, NC-ST-013
```

---

## Plan de Acción Sugerido

### Prioridad 1 — Cobertura (Crítico)
1. Crear `tests/test_factory.py` → resuelve NC-ST-002
2. Crear `tests/test_coordinator.py` → resuelve NC-ST-001
3. Extender `test_ui_principal.py` para `UIPrincipalCompositor` → resuelve NC-ST-008
4. Verificar cobertura total ≥ 95% → resuelve NC-ST-003

### Prioridad 2 — Deuda técnica (Mayor)
5. Eliminar archivos legacy (`control_temperatura.py`, `grafico_temperatura.py`, `ui_principal.py`) y sus tests → resuelve NC-ST-004, NC-ST-005, NC-ST-006, NC-ST-012 (parcial), NC-ST-013 (parcial)
6. Corregir acceso a `pyqtgraph.Qt.QtCore.Qt` en `paneles/grafico/vista.py:91` → resuelve NC-ST-007

### Prioridad 3 — Limpieza (Menor)
7. Eliminar imports no usados → resuelve NC-ST-009
8. Eliminar `pass` redundantes → resuelve NC-ST-011
9. Renombrar o eliminar `tiempo_relativo` → resuelve NC-ST-010
10. Agregar docstrings en `paneles/control_temperatura/vista.py` → resuelve NC-ST-013 (parcial)
11. Evaluar dataclass `Controladores` para reducir argumentos → resuelve NC-ST-012 (parcial)
