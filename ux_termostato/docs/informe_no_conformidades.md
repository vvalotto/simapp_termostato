# Informe de No-Conformidades — UX Termostato

**Fecha:** 2026-02-23
**Revisor:** Claude Code (claude-sonnet-4-6)
**Versión analizada:** branch `main`, commit `c287b05`
**Herramientas:** pylint 3.x, pytest-cov, inspección manual de código

---

## Resumen Ejecutivo

| Categoría | Crítica | Mayor | Menor |
|-----------|---------|-------|-------|
| Configuración de tests | 1 | — | — |
| Tests en rojo | 1 | — | — |
| Cobertura | — | 1 | — |
| Tests desactualizados vs implementación | — | 4 | 3 |
| Imports / argumentos no usados | — | — | 3 |
| TODO sin implementar | — | — | 1 |
| Emojis en logs | — | — | 1 |
| **TOTAL** | **2** | **5** | **8** |

`ux_termostato` es el producto con mayor volumen de código y funcionalidad (8 paneles, comunicación bidireccional, 731 tests). Sin embargo, presenta el mayor nivel de deuda técnica en tests: **40 fallos y 16 errores** que imposibilitan validar el 7.8% de la suite. Las métricas de Pylint (9.91/10) son correctas, pero la brecha entre tests e implementación es significativa.

---

## Severidad: CRÍTICA

### NC-UX-001 — Tests no ejecutables con el comando documentado (`pytest`)

**Archivo:** `tests/conftest.py`

Ejecutar `pytest` desde `ux_termostato/` (como indica el CLAUDE.md) falla inmediatamente:

```
ImportError while loading conftest 'tests/conftest.py'
tests/conftest.py:11: in <module>
    from app.presentacion.paneles.display.modelo import DisplayModelo
E   ModuleNotFoundError: No module named 'app'
```

La causa raíz es que `compartido/` no está en `sys.path`. A diferencia de `simulador_bateria`, cuyo `conftest.py` agrega el directorio raíz explícitamente:

```python
# simulador_bateria/tests/conftest.py (CORRECTO)
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
```

`ux_termostato/tests/conftest.py` no tiene ningún ajuste de `sys.path`. Los tests solo corren con el workaround `PYTHONPATH=".." python -m pytest`, que no está documentado ni es el comando estándar del proyecto.

**Acción recomendada (opción A — conftest.py):**
```python
# Agregar al inicio de ux_termostato/tests/conftest.py
import sys
from pathlib import Path
_root = Path(__file__).parent.parent.parent  # simapp_termostato/
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
```

**Acción recomendada (opción B — pytest.ini):**
```ini
[pytest]
pythonpath = ..
```

---

### NC-UX-002 — 40 tests fallan y 16 tienen errores (7.8% de la suite)

Con `PYTHONPATH` configurado correctamente, la suite reporta:

```
40 failed, 675 passed, 16 errors in ~12s
```

Esto incumple el estándar del proyecto (todos los tests deben pasar). Los fallos afectan a **12 archivos de test** y están agrupados en 5 causas raíz distintas (ver NC-UX-004 a NC-UX-008). La cobertura reportada como "96%" es engañosa porque incluye líneas alcanzadas por tests que fallan en assertion, no en ejecución.

| Archivo de tests | Fallos | Errores | Causa |
|-----------------|--------|---------|-------|
| `test_cliente_comandos.py` | 11 | — | Protocolo cambió (ver NC-UX-004) |
| `test_coordinator.py` | 2 | 16 | Mock sin señal `accion_temperatura` (ver NC-UX-005) |
| `test_display_controlador.py` | 3 | — | Mock genérico con format string (ver NC-UX-006) |
| `test_bdd_us001.py` | 5 | — | Mock genérico con format string (ver NC-UX-006) |
| `test_display_integracion.py` | 3 | — | Mock genérico con format string (ver NC-UX-006) |
| `test_control_temp_controlador.py` | 6 | — | Señal deprecada en tests (ver NC-UX-009) |
| `test_indicadores_vista.py` | 3 | — | Estado inicial LED (ver NC-UX-007) |
| `test_power_controlador.py` | 1 | — | Expectativa de señal incorrecta (ver NC-UX-008) |
| `test_power_integracion.py` | 1 | — | Expectativa de señal incorrecta (ver NC-UX-008) |
| `test_ui_compositor.py` | 4 | — | Layout desactualizado (ver NC-UX-010) |
| `test_ui_principal.py` | 1 | — | Layout desactualizado (ver NC-UX-010) |
| `test_indicadores_integracion.py` | 1 | — | Estado inicial LED (ver NC-UX-007) |

---

## Severidad: MAYOR

### NC-UX-003 — `coordinator.py` con 61% de cobertura

**Archivo:** `app/coordinator.py`
**Líneas sin cubrir:** 165–192, 202–210, 219–236, 249, 258, 268, 278, 288–296, 310–311 (42 líneas)

```
app/coordinator.py    109     42    61%
```

Las líneas no cubiertas corresponden a los handlers de señales (`_on_estado_recibido`, `_on_power_cambiado`, `_on_accion_temperatura`, `_on_modo_vista_cambiado`, etc.) — exactamente las partes que los tests del coordinator intentan ejercer pero no pueden porque los mocks están desactualizados (NC-UX-005). El coordinator es la pieza de integración más importante del sistema y tiene la peor cobertura.

**Acción recomendada:** Resolver NC-UX-005 (actualizar los mocks del coordinator) desbloqueará la cobertura de estas líneas.

---

### NC-UX-004 — Tests de `ClienteComandos` desactualizados respecto al protocolo (11 fallos)

**Archivo:** `tests/test_cliente_comandos.py`

Los tests `TestEnvioComandos` y `TestSerializacionJSON` esperan que `ComandoPower` se envíe exitosamente y que el protocolo sea JSON. La implementación actual de `ClienteComandos` usa **protocolo texto plano** (no JSON) y **no soporta `ComandoPower`**:

```python
# cliente_comandos.py:183-187
# Comando 'power' NO soportado (ISSE_Termostato no tiene endpoint)
if tipo_comando == "power":
    return (None, 0)   # ← retorna None, enviar_comando() devuelve False
```

Los tests de serialización JSON también fallan porque el protocolo ya no envía JSON — serializa pero luego convierte a texto plano.

La señal `comando_enviado` en `ControlTempControlador` está marcada como `# (deprecado)` en el código, pero los tests de `TestComandoJSON` siguen usando esa señal, que ya no se emite en el flujo principal.

**Acción recomendada:** Actualizar `TestEnvioComandos` para verificar que `ComandoPower` retorna `False` (comportamiento intencional). Actualizar `TestSerializacionJSON` para verificar el formato texto plano real. Eliminar o marcar tests de JSON serialization que ya no aplican.

---

### NC-UX-005 — Tests del coordinator usan `MockControlador` sin señal `accion_temperatura` (2 fallos, 16 errores)

**Archivo:** `tests/test_coordinator.py`

El `MockControlador` genérico no tiene la señal `accion_temperatura` que el coordinator intenta conectar:

```python
# coordinator.py:117
ctrl_control_temp.accion_temperatura.connect(self._on_accion_temperatura)
# ↑ AttributeError: 'MockControlador' object has no attribute 'accion_temperatura'
```

Cuando `UXCoordinator.__init__` falla al conectar señales, la fixture `coordinator` no puede crearse, cascadeando a 16 tests que dependen de ella (ERROR en setup).

El `MockControlador` fue creado antes de que `ControlTempControlador` incorporara la señal `accion_temperatura`. No se actualizó cuando se refactorizó el controlador.

**Acción recomendada:** Actualizar `MockControlador` en `test_coordinator.py` para incluir `accion_temperatura = pyqtSignal(str)` y las señales `power_cambiado = pyqtSignal(bool)`. Alternativamente, usar `spec=ControlTempControlador` en el mock.

---

### NC-UX-006 — Tests de display/BDD usan `Mock()` genérico que falla con format strings (11 fallos)

**Archivos:** `tests/test_display_controlador.py`, `tests/test_bdd_us001.py`, `tests/test_display_integracion.py`

El controlador del display llama:
```python
# display/vista.py:172
self.label_temp.setText(f"{modelo.temperatura:.1f}")
```

Cuando los tests pasan un `Mock()` como modelo, `modelo.temperatura` devuelve otro `Mock`, y `f"{Mock():.1f}"` lanza:
```
TypeError: unsupported format string passed to Mock.__format__
```

El problema está en los tests que crean mocks para `EstadoTermostato` usando `Mock()` puro en lugar de `Mock(spec=EstadoTermostato)` o valores concretos.

**Acción recomendada:** Reemplazar `Mock()` para modelos de display por `spec=EstadoTermostato` con atributos concretos, o usar directamente instancias de `EstadoTermostato`.

---

### NC-UX-007 — Estado inicial de LEDs en `IndicadoresVista` no coincide con tests (4 fallos)

**Archivos:** `tests/test_indicadores_vista.py`, `tests/test_indicadores_integracion.py`

Los tests esperan que los LEDs de alerta inicien en `state=False` (sin alerta), pero `LEDIndicator` de `compartido/widgets` inicializa con `state=True`:

```python
# test_indicadores_vista.py:
assert vista.alert_sensor.led.state is False  # ← FALLA: state es True
```

Hay dos lecturas posibles:
1. **Bug en `IndicadoresVista`**: no inicializa los LEDs en estado apagado (sin alerta) al crear la vista.
2. **Test incorrecto**: los tests asumen un estado inicial que no corresponde al contrato del `LEDIndicator`.

Si el comportamiento correcto es que los LEDs empiecen apagados (sin alerta), `IndicadoresVista` debe llamar `set_state(False)` en su `__init__` después de crear los LEDs.

**Acción recomendada:** Verificar el contrato de `LEDIndicator`. Si debe iniciar en `False`, agregar inicialización en `IndicadoresVista.__init__`. Si debe iniciar en `True`, corregir los tests.

---

### NC-UX-008 — Tests esperan señal de `PowerControlador.actualizar_modelo()` que intencionalmente no se emite (2 fallos)

**Archivos:** `tests/test_power_controlador.py`, `tests/test_power_integracion.py`

El controlador documenta explícitamente que `actualizar_modelo()` no emite señales:
```python
# power/controlador.py:96-102
def actualizar_modelo(self, encendido: bool):
    """
    Actualiza el modelo con un nuevo estado SIN emitir señales.
    ...NO emitir señal para evitar enviar comando de vuelta al RPi
    """
    self._modelo = replace(self._modelo, encendido=encendido)
    self._vista.actualizar(self._modelo)
    # NO emitir señal para evitar enviar comando de vuelta al RPi
```

Los tests verifican que `power_cambiado` SÍ se emite al llamar `actualizar_modelo()`, contradiciendo el diseño:
```python
# test_power_controlador.py:262
with qtbot.waitSignal(controlador.power_cambiado, timeout=1000):
    controlador.actualizar_modelo(True)  # ← TimeoutError: señal nunca emitida
```

Este no es un bug de implementación sino un test que no refleja el diseño intencional.

**Acción recomendada:** Actualizar los tests para verificar que `actualizar_modelo()` NO emite `power_cambiado` (que es el comportamiento correcto). Renombrar el test para reflejar la invariante real.

---

### NC-UX-009 — Tests de `ControlTempControlador` usan señal deprecada `comando_enviado` (6 fallos)

**Archivo:** `tests/test_control_temp_controlador.py`

`ControlTempControlador` ahora emite `accion_temperatura` como señal principal y marca `comando_enviado` como deprecated:
```python
accion_temperatura = pyqtSignal(str)  # Acción a enviar al RPi: "aumentar" | "disminuir"
comando_enviado = pyqtSignal(dict)    # Comando JSON para el RPi (deprecado)
```

Los tests observan `comando_enviado` con `QSignalSpy`, que nunca recibe nada porque el controlador ya no la emite:
```python
# test_control_temp_controlador.py:293
spy = QSignalSpy(controlador.comando_enviado)
controlador.aumentar_temperatura()
comando = spy[0][0]  # ← IndexError: spy está vacío
```

**Acción recomendada:** Actualizar los tests para usar `accion_temperatura` en lugar de `comando_enviado`. Los tests de estructura JSON ya no aplican (el protocolo es texto plano). Eliminar o adaptar `TestComandoJSON`.

---

## Severidad: MENOR

### NC-UX-010 — Tests de `UICompositor` y `UIPrincipal` con valores desactualizados (5 fallos)

**Archivos:** `tests/test_ui_compositor.py`, `tests/test_ui_principal.py`

Los tests tienen expectativas que no coinciden con la implementación actual:

| Test | Esperado | Real | Error |
|------|----------|------|-------|
| `test_layout_contiene_todos_paneles` | 7 widgets | 6 widgets | `assert 6 >= 7` |
| `test_widget_tiene_tamano_minimo` | alto=700 | alto=0 | `assert 0 == 700` |
| `test_widget_tiene_tamano_inicial` | ancho=600 | ancho=640 | `assert 640 == 600` |
| `test_orden_paneles_en_layout` | panel en pos X | panel ausente | `assert None is not None` |
| `test_central_widget_tiene_layout` | layout específico | diferente | estructura diferente |

Estos fallos sugieren que el `UICompositor` fue refactorizado (cambios en número de paneles, tamaño de ventana) sin actualizar los tests correspondientes.

**Acción recomendada:** Revisar el `UICompositor` actual y actualizar las constantes de los tests para reflejar el número real de paneles y dimensiones de ventana.

---

### NC-UX-011 — Imports no usados en 3 archivos (W0611)

| Archivo | Línea | Import no usado |
|---------|-------|----------------|
| `app/coordinator.py` | 14 | `ComandoSetTemp` de `dominio` |
| `app/comunicacion/cliente_comandos.py` | 7 | módulo `json` |
| `app/presentacion/ui_compositor.py` | 10 | `QSize` de `PyQt6.QtCore` |

**Acción recomendada:** Eliminar los tres imports.

---

### NC-UX-012 — Argumento `temperatura` no usado en `coordinator.py:238` (W0613)

**Archivo:** `app/coordinator.py:238`

```python
def _on_estado_recibido(self, temperatura, ...):
    # temperatura se recibe pero nunca se usa en el cuerpo
```

El argumento `temperatura` es recibido en el handler pero ignorado, con los datos del estado siendo extraídos por otra vía. Pylint W0613.

**Acción recomendada:** Prefixar con `_` (`_temperatura`) para indicar que es intencionalmente no usado, o revisar si debería usarse.

---

### NC-UX-013 — TODO sin implementar en `coordinator.py:315` (W0511)

**Archivo:** `app/coordinator.py:315`

```python
# TODO US-013: Implementar persistencia y reconexión
```

Pylint W0511. El TODO referencia una historia de usuario (US-013) que está en el backlog sin fecha de implementación.

**Acción recomendada:** Crear un issue o tarea formal para US-013. Si no tiene plan de implementación, convertir el comentario en documentación de la limitación conocida sin el prefijo TODO.

---

### NC-UX-014 — Emojis en mensajes de log

**Archivos:**
- `app/presentacion/paneles/control_temp/controlador.py:82, 85, 97, 110, 130, 133, 145, 155`
- `app/coordinator.py` (algunos)

```python
logger.info("🔼 Botón SUBIR presionado")
logger.warning("❌ No se puede aumentar: ...")
logger.info("✅ Aumentando temperatura: ...")
logger.info("📡 Emitiendo señales: ...")
```

Los emojis en logs son inconsistentes con el estilo del resto del proyecto (simuladores y compartido usan logs en texto plano). Pueden causar problemas en terminales sin soporte Unicode (consolas CI/CD, logging a fichero en sistemas sin UTF-8, etc.).

**Acción recomendada:** Reemplazar emojis por prefijos de texto: `[SUBIR]`, `[ERROR]`, `[OK]`, `[SEÑAL]`, o simplemente eliminarlos.

---

## Comparativa entre los tres productos

| Aspecto | simulador_temperatura | simulador_bateria | ux_termostato |
|---------|----------------------|-------------------|---------------|
| Pylint Score | 9.52 | **9.94** | 9.91 |
| Tests ejecutables directamente | ✅ | ✅ | ❌ |
| Tests en verde | ✅ | ✅ | ❌ (40 fallos) |
| Cobertura total | 89% ❌ | **96%** | 96%\* |
| Cobertura coordinator | 0% ❌ | **100%** | 61% ❌ |
| Código legacy | 3 archivos ❌ | **Ninguno** | **Ninguno** |
| Imports no usados | 6 | 0 | 3 |
| `except Exception` genérico | 0 | 3 | 1 (con disable) |

\* El 96% de cobertura se reporta con tests que fallan; líneas alcanzadas por assertions que fallan se marcan como cubiertas.

---

## Plan de Acción Sugerido

### Prioridad 1 — Habilitar ejecución de tests (Crítico)
1. Agregar `sys.path` setup a `conftest.py` o `pythonpath = ..` en `pytest.ini` → resuelve NC-UX-001

### Prioridad 2 — Poner la suite en verde (Crítico/Mayor)
2. Actualizar `MockControlador` en `test_coordinator.py` con señal `accion_temperatura` → resuelve NC-UX-005 (desbloquea 16 errores + 2 fallos)
3. Reemplazar mocks genéricos por `spec=EstadoTermostato` en tests de display → resuelve NC-UX-006 (11 fallos)
4. Corregir tests de `ClienteComandos` para el protocolo actual → resuelve NC-UX-004 (11 fallos)
5. Actualizar tests de `ControlTempControlador` para usar `accion_temperatura` → resuelve NC-UX-009 (6 fallos)
6. Investigar estado inicial de `LEDIndicator` y alinear tests → resuelve NC-UX-007 (4 fallos)
7. Invertir expectativa de `actualizar_modelo()` en tests de Power → resuelve NC-UX-008 (2 fallos)
8. Actualizar constantes de `UICompositor` en tests → resuelve NC-UX-010 (5 fallos)

### Prioridad 3 — Cobertura y calidad (Mayor/Menor)
9. Resolver NC-UX-005 desbloqueará automáticamente cobertura de `coordinator.py` → resuelve NC-UX-003
10. Eliminar imports no usados → resuelve NC-UX-011
11. Prefijar argumento no usado con `_` → resuelve NC-UX-012
12. Convertir TODO a documentación formal → resuelve NC-UX-013
13. Reemplazar emojis en logs → resuelve NC-UX-014
