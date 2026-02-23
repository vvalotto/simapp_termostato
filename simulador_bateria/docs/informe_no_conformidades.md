# Informe de No-Conformidades — Simulador de Batería

**Fecha:** 2026-02-23
**Revisor:** Claude Code (claude-sonnet-4-6)
**Versión analizada:** branch `main`, commit `c287b05`
**Herramientas:** pylint 3.x, pytest-cov, radon, inspección manual de código

---

## Resumen Ejecutivo

| Categoría | Crítica | Mayor | Menor |
|-----------|---------|-------|-------|
| Cobertura de tests | — | 1 | 2 |
| Manejo de excepciones | — | 2 | — |
| Código duplicado | — | — | 1 |
| Contrato de tipos en vistas | — | — | 2 |
| **TOTAL** | **0** | **3** | **5** |

El simulador de batería es el más maduro de los tres productos. Cumple todos los quality gates (Pylint 9.94/10, CC ≤ 10, MI > 20, cobertura 96%). No existen archivos legacy ni código muerto. Las no-conformidades encontradas son problemas focalizados de diseño en la capa de comunicación y de cobertura en el compositor de UI.

Diferencias positivas notables respecto a `simulador_temperatura`:
- `coordinator.py` y `factory.py` tienen 100% de cobertura.
- No hay código legacy en `app/presentacion/`.
- `paneles/base.py` no contiene `pass` redundantes ni imports no usados.

---

## Severidad: MAYOR

### NC-SB-001 — `ui_compositor.py` con 24% de cobertura

**Archivo:** `app/presentacion/ui_compositor.py`
**Líneas sin cubrir:** 55–60, 64–82

La clase `UIPrincipalCompositor` tiene su método de construcción de layout (`_setup_ui`) sin ninguna cobertura de tests. Esto incluye la creación del widget central, el layout vertical y la adición de las tres vistas de paneles.

```
app/presentacion/ui_compositor.py    21     16    24%   55-60, 64-82
```

A diferencia de `coordinator.py` y `factory.py` que sí tienen tests completos, el compositor de UI no es ejercido por la suite. Dado que el compositor es el responsable de armar la ventana final, un defecto en la composición de paneles no sería detectado.

**Acción recomendada:** Agregar un test de integración que instancie `UIPrincipalCompositor` con los tres controladores y verifique que la ventana se construye correctamente (título, tamaño mínimo, widgets hijos presentes).

---

### NC-SB-002 — `except Exception` demasiado genérico en capa de comunicación (W0718)

**Archivos y líneas:**
- `app/comunicacion/cliente_bateria.py:92` — método `enviar_voltaje()`
- `app/comunicacion/cliente_bateria.py:112` — método `enviar_voltaje_async()`
- `app/comunicacion/servicio_envio.py:113` — método `_on_valor_generado()`

**Pylint:** W0718 (broad-exception-caught)

Los tres bloques capturan `Exception` base en lugar de las excepciones específicas que puede lanzar el socket:

```python
# cliente_bateria.py:86-95
try:
    self._ultimo_valor = voltaje
    mensaje = f"{voltaje:.2f}"
    return self._cliente.send(mensaje)
except Exception as e:          # ← demasiado genérico
    logger.error(...)
    self.error_conexion.emit(str(e))
    return False
```

`EphemeralSocketClient.send()` puede lanzar `ConnectionRefusedError`, `TimeoutError`, `OSError` u otras subclases de `socket.error`. Capturar `Exception` oculta bugs inesperados (errores de programación, `TypeError`, `AttributeError`) que deberían propagarse.

**Acción recomendada:** Reemplazar `except Exception` por `except OSError` (que cubre todas las excepciones de red en Python: `ConnectionRefusedError`, `TimeoutError`, `BrokenPipeError`, etc.).

---

### NC-SB-003 — Bloque `except` inalcanzable en `ServicioEnvioBateria._on_valor_generado`

**Archivo:** `app/comunicacion/servicio_envio.py:109–115`
**Líneas sin cubrir:** 113–115

```python
def _on_valor_generado(self, estado: EstadoBateria) -> None:
    """Callback cuando el generador produce un nuevo valor."""
    try:
        self._cliente.enviar_estado_async(estado)
    except Exception as e:                              # ← nunca se ejecuta
        logger.error("Error al procesar valor generado: %s", str(e))
        self.envio_fallido.emit(str(e))
```

`enviar_estado_async()` llama a `enviar_voltaje_async()`, que internamente ya captura todas sus excepciones con su propio `try/except` y nunca relanza. Por tanto, el bloque `except` de `_on_valor_generado` es **código muerto**: no puede ejecutarse en ninguna condición normal ni de error.

Este es un double-wrapping de manejo de errores que:
1. Crea falsa sensación de seguridad.
2. Hace imposible alcanzar 100% de cobertura en este método sin mocks artificiales.
3. Confunde el modelo mental de qué capa maneja los errores.

**Acción recomendada:** Eliminar el `try/except` de `_on_valor_generado`. Si se quiere protección adicional, mover la responsabilidad de manejo de error a `enviar_voltaje_async()` y propagarla via señal, no via excepción.

---

## Severidad: MENOR

### NC-SB-004 — Cobertura parcial de `_buscar_config_json` (88% en config.py)

**Archivo:** `app/configuracion/config.py:98–104`
**Líneas sin cubrir:** 98–104 (cuerpo de `_buscar_config_json`)

```
app/configuracion/config.py    59      7    88%   98-104
```

El método `_buscar_config_json()` que escala directorios buscando `config.json` no está cubierto. Los tests siempre llaman a `cargar(ruta_config=Path(...))` con ruta explícita, evitando la rama de búsqueda automática.

La búsqueda automática es el comportamiento que se activa en producción (cuando el simulador se ejecuta con `python run.py` sin parámetros). Que no esté testeada significa que un cambio en la lógica de búsqueda podría pasar desapercibido.

**Acción recomendada:** Agregar un test que llame a `cargar()` sin argumentos desde un directorio donde `config.json` existe en algún nivel superior, usando `tmp_path` de pytest para crear una estructura de directorios controlada.

---

### NC-SB-005 — Callback `_on_error` de `ClienteBateria` sin cobertura

**Archivo:** `app/comunicacion/cliente_bateria.py:148–153`
**Líneas sin cubrir:** 149–153

```python
def _on_error(self, mensaje: str) -> None:
    """Callback interno cuando ocurre un error de conexión."""
    logger.error(                      # ← sin cubrir
        "Error de conexión con %s:%d - %s",
        self._host, self._port, mensaje
    )
    self.error_conexion.emit(mensaje)  # ← sin cubrir
```

Este callback se activa cuando `EphemeralSocketClient` emite su señal `error_occurred`. Los tests actuales mockean `EphemeralSocketClient.send` pero no simulan la emisión de `error_occurred` directamente desde el cliente interno. Como resultado, el flujo de error end-to-end no está cubierto: si el socket falla, `_on_error` se dispara y re-emite `error_conexion`, pero ese camino no tiene tests.

**Acción recomendada:** En `test_cliente_bateria.py`, agregar un test que conecte directamente al `_cliente` interno del `ClienteBateria` y emita `error_occurred` con un mensaje, verificando que `ClienteBateria.error_conexion` re-emite el mensaje correctamente.

---

### NC-SB-006 — CSS de panel duplicado entre vistas (R0801)

**Pylint:** R0801 (duplicate-code)
**Archivos:**
- `app/presentacion/paneles/estado/vista.py:63–73`
- `app/presentacion/paneles/conexion/vista.py:76–86`

El bloque de configuración inicial de `_setup_ui` (frame style + stylesheet con `QFrame` y `QLabel`) es idéntico en ambas vistas:

```python
self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
self.setStyleSheet(f"""
    QFrame {{
        background-color: {self._config.color_fondo};
        border-radius: 8px;
        padding: 10px;
    }}
    QLabel {{
        color: {self._config.color_texto};
    }}
""")
```

Esta duplicación implica que si se cambia el tema visual, el cambio debe aplicarse en múltiples lugares. El panel de `control/vista.py` probablemente tenga el mismo patrón.

**Acción recomendada:** Extraer este bloque a una función helper en `compartido/estilos/` o crear una clase base de panel `PanelBase(QFrame)` que aplique el estilo en su `__init__` dado `color_fondo` y `color_texto`. Esto ya existe para otras cosas en `compartido/widgets/` — la consistencia invita a usar ese patrón.

---

### NC-SB-007 — Firma de `actualizar()` debilita el contrato de tipos

**Archivos:**
- `app/presentacion/paneles/estado/vista.py:117` — `def actualizar(self, modelo: ModeloBase) -> None`
- `app/presentacion/paneles/conexion/vista.py:154` — `def actualizar(self, modelo: ModeloBase) -> None`

Ambas vistas declaran recibir `ModeloBase` pero inmediatamente hacen un isinstance check para descartar tipos incorrectos:

```python
def actualizar(self, modelo: ModeloBase) -> None:
    if not isinstance(modelo, EstadoBateriaPanelModelo):
        return                        # ← falla silenciosa
    # ... actualización real
```

Problemas de este patrón:
1. **Contrato débil:** La firma promete aceptar cualquier `ModeloBase`, pero en realidad solo funciona con un tipo específico. Un llamador que pase un modelo diferente no recibirá error sino comportamiento silencioso.
2. **Falla silenciosa:** Si se pasa el modelo equivocado por error (p.ej. en el coordinator), la vista simplemente no se actualiza, sin ninguna excepción ni log.
3. **Bypasa el sistema de tipos:** mypy o pyright no detectarán el bug si el coordinator pasa el tipo incorrecto.

La firma correcta según el contrato real sería:
```python
def actualizar(self, modelo: EstadoBateriaPanelModelo) -> None:
```

**Acción recomendada:** Actualizar la firma para usar el tipo concreto. Si se quiere mantener la flexibilidad de `VistaBase`, parametrizar la clase base con el tipo de modelo usando Generic: `class VistaBase(QWidget, Generic[M])`.

---

## Comparativa con `simulador_temperatura`

| Aspecto | simulador_bateria | simulador_temperatura |
|---------|-------------------|----------------------|
| Pylint Score | **9.94** | 9.52 |
| Cobertura total | **96%** | 89% |
| Cobertura coordinator | **100%** | 0% ❌ |
| Cobertura factory | **100%** | 0% ❌ |
| Cobertura ui_compositor | 24% ⚠️ | 46% ⚠️ |
| Código legacy | **Ninguno** | 3 archivos |
| `pass` redundantes | **Ninguno** | 7 instancias |
| `except Exception` genérico | 3 instancias ⚠️ | 0 |
| Código duplicado entre paneles | CSS boilerplate | `SliderConValor` |

---

## Plan de Acción Sugerido

### Prioridad 1 — Diseño (Mayor)
1. Eliminar `try/except` inalcanzable en `_on_valor_generado` → resuelve NC-SB-003
2. Reemplazar `except Exception` por `except OSError` en `cliente_bateria.py` → resuelve NC-SB-002

### Prioridad 2 — Cobertura (Mayor/Menor)
3. Agregar test de `UIPrincipalCompositor` → resuelve NC-SB-001
4. Agregar test de `_on_error` via señal del cliente interno → resuelve NC-SB-005
5. Agregar test de `_buscar_config_json` con directorio temporal → resuelve NC-SB-004

### Prioridad 3 — Diseño (Menor)
6. Parametrizar firma de `actualizar()` con tipo concreto → resuelve NC-SB-007
7. Extraer CSS boilerplate de paneles a helper compartido → resuelve NC-SB-006
