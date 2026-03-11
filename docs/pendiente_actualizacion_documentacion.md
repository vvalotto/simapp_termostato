# Pendiente: Actualización de Documentación

Cambios de documentación identificados tras completar Fases 3 y 4 de calidad.
Generado el 2026-03-11. Ejecutar en una sesión dedicada.

---

## 1. `ux_termostato/docs/arquitectura.md`

### 1.1 Árbol de estructura — agregar `interfaces.py`

En la sección del árbol de directorios, bajo `app/comunicacion/`, agregar:
```
├── interfaces.py       # IServidorEstado, IClienteComandos (typing.Protocol)
```

### 1.2 Sección nueva: Interfaces de comunicación

Agregar sección después de la descripción de `ServidorEstado` / `ClienteComandos`:

```markdown
### Interfaces de comunicación (`interfaces.py`)

Define contratos estructurales usando `typing.Protocol` con `@runtime_checkable`.
Se usa `Protocol` (no ABC) para evitar conflictos de metaclase con `QObject`.

- `IServidorEstado` — contrato para el servidor de estado TCP
  - `iniciar() -> bool`
  - `detener() -> None`
  - `esta_activo() -> bool`
- `IClienteComandos` — contrato para el cliente de comandos TCP
  - `enviar_comando(cmd: ComandoTermostato) -> bool`

`ComponenteFactoryUX.crear_servidor_estado()` y `crear_cliente_comandos()`
retornan estos tipos, permitiendo sustitución por mocks en tests.
```

### 1.3 Sección nueva: `pyproject.toml` — umbrales de calidad

Agregar sección de configuración de calidad:

```markdown
## Configuración de calidad (`pyproject.toml`)

Umbrales calibrados para DesignReviewer:

```toml
[tool.designreviewer]
max_cbo = 10           # vistas PyQt acoplan widgets inevitablemente
max_method_lines = 50  # _setup_ui es proceduralmente largo por naturaleza
max_lcom = 3           # clases MVC tienen grupos de métodos naturalmente separados
```

Justificación de valores:
- **CBO ≤ 10**: Las vistas PyQt heredan de QWidget y usan múltiples widgets hijos.
- **method_lines ≤ 50**: Los métodos `_setup_ui` y `_ensamblar_layout` son
  proceduralmente largos por diseño (construcción declarativa de UI).
- **LCOM ≤ 3**: Las clases MVC separan naturalmente grupos de métodos
  (modelo, vista, señales). La herencia PyQt infla el LCOM.
```

### 1.4 Refactoring `VentanaPrincipalUX` — facade de lifecycle

En la sección que describe `ui_principal.py`, actualizar descripción:

**Antes:**
> `ui_principal.py` — Ventana principal (~300 líneas): lifecycle, layout, coordinator

**Después:**
> `ui_principal.py` — Ventana principal (~100 líneas): **facade de lifecycle** puro.
> Delega: creación de componentes → `ComponenteFactoryUX`, coordinación de señales →
> `UXCoordinator`, composición de UI → `UICompositor`. Métodos públicos: `iniciar()`,
> `cerrar()`. Reduce 307 → 100 líneas (ISS-10).

### 1.5 Panel Power deshabilitado

En la descripción de `UICompositor` o en la lista de paneles, agregar nota:

> **Nota:** El panel `power` está incluido en los componentes pero **no se renderiza**
> en el layout (comentado en `UICompositor.crear_layout()`), ya que
> ISSE_Termostato no expone endpoint de encendido/apagado en la versión actual.

---

## 2. `simulador_bateria/docs/arquitectura.md`

### 2.1 Árbol de estructura — agregar `interfaces.py`

Bajo `app/comunicacion/`, agregar:
```
├── interfaces.py       # IClienteBateria (typing.Protocol)
```

### 2.2 Sección nueva: Interfaz `IClienteBateria`

```markdown
### Interfaz de comunicación (`interfaces.py`)

Define `IClienteBateria` como `typing.Protocol` con `@runtime_checkable`:

- `enviar_voltaje(voltaje: float) -> bool`
- `enviar_estado(estado: EstadoBateria) -> bool`

`ComponenteFactory.crear_cliente()` retorna `IClienteBateria`, permitiendo
sustitución transparente en tests sin herencia explícita (`ClienteBateria`
cumple el protocolo por duck typing).
```

### 2.3 Sección nueva: `pyproject.toml`

```markdown
## Configuración de calidad (`pyproject.toml`)

```toml
[tool.designreviewer]
max_cbo = 10
max_method_lines = 50
max_lcom = 3
```

Justificación idéntica a `ux_termostato` (ver arriba). LCOM=3 en `ClienteBateria`
es intencional: agrupa métodos por protocolo (envío de voltaje vs. envío de estado).
```

---

## 3. `simulador_temperatura/docs/arquitectura.md`

### 3.1 Árbol de estructura — agregar `interfaces.py`

Bajo `app/comunicacion/`, agregar:
```
├── interfaces.py       # IClienteTemperatura (typing.Protocol)
```

### 3.2 Sección nueva: Interfaz `IClienteTemperatura`

```markdown
### Interfaz de comunicación (`interfaces.py`)

Define `IClienteTemperatura` como `typing.Protocol` con `@runtime_checkable`:

- `enviar_temperatura(temperatura: float) -> bool`
- `enviar_estado(estado: EstadoTemperatura) -> bool`

`ComponenteFactory.crear_cliente()` retorna `IClienteTemperatura`.
```

### 3.3 Sección nueva: `pyproject.toml`

Mismo contenido que `simulador_bateria` (adaptar justificación si es necesario).

---

## 4. `compartido/docs/arquitectura.md` (si existe)

### 4.1 Estrategia de interfaces locales

Agregar nota sobre el patrón de interfaces adoptado:

```markdown
## Estrategia de interfaces

Cada producto define sus propias interfaces en `app/comunicacion/interfaces.py`
usando `typing.Protocol`. Se usa `Protocol` (no ABC) para evitar conflictos de
metaclase entre `ABCMeta` y la metaclase interna de `QObject` (PyQt6).

Las interfaces no viven en `compartido/` porque son específicas al dominio
de cada producto (voltaje de batería ≠ temperatura ≠ comandos UX).
```

---

## 5. `ux_termostato/docs/informes/informe_calidad_final.md`

### 5.1 Agregar sección: Refactoring ISS-10 (VentanaPrincipalUX)

```markdown
### ISS-10: VentanaPrincipalUX — Reducción a facade de lifecycle

**Problema:** God Object de 307 líneas con responsabilidades mezcladas
(creación de componentes, coordinación de señales, composición de UI, lifecycle).

**Solución:** Delegación total:
- Creación → `ComponenteFactoryUX`
- Coordinación → `UXCoordinator`
- Composición → `UICompositor`
- `VentanaPrincipalUX` retiene solo: `__init__`, `iniciar()`, `cerrar()`, `closeEvent()`

**Resultado:** 307 → ~100 líneas. LCOM reducido a 1 (una sola responsabilidad).
```

### 5.2 Agregar sección: Fix `IndicadoresVista`

```markdown
### Fix: IndicadoresVista — comportamiento LED correcto

**Bug:** La vista mostraba LED verde cuando el sensor estaba OK (incorrecto).
El diseño original especifica: LED apagado (gris) = OK, LED rojo/amarillo = alerta.

**Fix en `actualizar()`:**
```python
# Antes (incorrecto):
self.alert_sensor.led.set_color(LEDColor.GREEN)
self.alert_sensor.set_estado(activo=True, pulsar=False)

# Después (correcto):
self.alert_sensor.set_estado(activo=False, pulsar=False)
```
```

### 5.3 Agregar sección: Interfaces de comunicación (ISS-16)

```markdown
### ISS-16: Interfaces ABC en capa de comunicación

Implementadas como `typing.Protocol` (no ABC) para compatibilidad con PyQt6.
Ver sección de arquitectura para detalles.
```

### 5.4 Actualizar métricas finales

Actualizar tabla de métricas con valores post-refactoring:
- `VentanaPrincipalUX`: líneas 307 → ~100
- Tests: 735 passed, 0 failures (resueltos 56 fallos pre-existentes)

---

## 6. `simulador_bateria/docs/informes/informe_calidad_final.md`

### 6.1 ISS-11: Decisión LCOM=3 en `ClienteBateria`

```markdown
### ISS-11: ClienteBateria — LCOM=3 (decisión de diseño documentada)

`ClienteBateria` presenta LCOM=3 por agrupación intencional de métodos:
- Grupo 1: envío de voltaje raw (`enviar_voltaje`)
- Grupo 2: envío de estado completo (`enviar_estado`)
- Grupo 3: configuración de conexión (compartida)

**Decisión:** No refactorizar. La separación refleja dos protocolos distintos
de envío. Documentado en docstring de la clase. (ISS-11)
```

### 6.2 ISS-16: IClienteBateria

Agregar nota sobre implementación de interfaz Protocol.

---

## 7. `simulador_temperatura/docs/informes/informe_calidad_final.md`

### 7.1 ISS-16: IClienteTemperatura

Similar a simulador_bateria. Agregar nota sobre implementación.

---

## 8. Reportes de calidad (`quality/reports/quality_*.json` o similares)

Si los reportes son generados automáticamente, **no modificar manualmente**.
Si hay sección de notas/decisiones manuales, agregar:

- Decisión LCOM=3 `ClienteBateria` (ISS-11)
- Decisión LCOM=6 `ServidorEstado` (ISS-12, herencia PyQt + señales class-level)
- `pyproject.toml` como fuente de umbrales calibrados (ISS-13/14/15)

---

## Orden de ejecución sugerido

1. Leer cada archivo antes de editar (obligatorio por política de Claude Code)
2. Editar en este orden para mantener coherencia:
   1. `ux_termostato/docs/arquitectura.md` (más cambios)
   2. `simulador_bateria/docs/arquitectura.md`
   3. `simulador_temperatura/docs/arquitectura.md`
   4. `compartido/docs/arquitectura.md` (verificar si existe primero)
   5. Los tres `informe_calidad_final.md`
3. Verificar que los árboles de directorios en los `.md` coincidan con la estructura real
4. Commit final: `docs: actualizar documentación post-Fases-3-4 [ISS-10..16]`
