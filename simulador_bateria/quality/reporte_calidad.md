# Reporte de Calidad - Simulador Batería

**Fecha:** 2026-03-07
**Herramienta:** software_limpio v0.3.0 (CodeGuard + DesignReviewer + ArchitectAnalyst)
**Fuente analizada:** `simulador_bateria/app/`

---

## 1. CodeGuard

Análisis de calidad de código: complejidad ciclomática, PEP8, seguridad, imports.

| Paquete        | Errores | Warnings | Info |
|----------------|---------|----------|------|
| comunicacion   | 0       | 0        | 9    |
| configuracion  | 0       | 0        | 9    |
| dominio        | 0       | 0        | 9    |
| presentacion   | 0       | 0        | 48   |

**Conclusion:** El codigo pasa todos los controles sin errores ni advertencias. PEP8 cumplido, sin vulnerabilidades de seguridad, complejidad ciclomática dentro del umbral (≤10) en todas las funciones.

---

## 2. DesignReviewer

Análisis de calidad de diseño: acoplamiento (CBO), cohesión (LCOM), métodos largos, code smells.

### 2.1 Por paquete

| Paquete        | Critical | Warnings |
|----------------|----------|----------|
| configuracion  | 0        | 0        |
| dominio        | 0        | 1        |
| comunicacion   | 0        | 5        |
| presentacion   | 3        | 14       |

### 2.2 Detalle de hallazgos

**configuracion** — Sin hallazgos.

**dominio**

| Clase            | Tipo   | Metrica | Valor | Umbral | Detalle |
|------------------|--------|---------|-------|--------|---------|
| GeneradorBateria | WARN   | LCOM    | 2     | 1      | 2 grupos de métodos sin atributos compartidos |

**comunicacion**

| Clase               | Tipo | Metrica     | Valor | Umbral | Detalle |
|---------------------|------|-------------|-------|--------|---------|
| ClienteBateria      | WARN | LCOM        | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| ClienteBateria      | WARN | LongMethod  | 27    | 20     | `__init__` demasiado largo |
| ClienteBateria      | WARN | LongMethod  | 22    | 20     | `enviar_voltaje` demasiado largo |
| ServicioEnvioBateria| WARN | LCOM        | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ServicioEnvioBateria| WARN | LongMethod  | 22    | 20     | `__init__` demasiado largo |

**presentacion**

| Clase                 | Tipo     | Metrica     | Valor | Umbral | Detalle |
|-----------------------|----------|-------------|-------|--------|---------|
| UIPrincipalCompositor | WARN     | LongMethod  | 21    | 20     | `__init__` demasiado largo |
| UIPrincipalCompositor | WARN     | LongMethod  | 21    | 20     | `_setup_ui` demasiado largo |
| EstadoBateriaPanelModelo | WARN  | LCOM        | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| PanelEstadoVista      | CRITICAL | CBO         | 6     | 5      | Acoplado a: ConfigPanelEstadoVista, ModeloBase, QFont, QFrame, QLabel, QVBoxLayout |
| PanelEstadoVista      | WARN     | LongMethod  | 55    | 20     | `_setup_ui` demasiado largo |
| PanelEstadoVista      | WARN     | LongMethod  | 31    | 20     | `actualizar` demasiado largo |
| ConexionPanelModelo   | WARN     | LCOM        | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| ConexionPanelControlador | WARN  | LCOM        | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ConexionPanelVista    | CRITICAL | CBO         | 9     | 5      | Acoplado a: ConfigConexionPanelVista, ConfigPanel, ConfigPanelLabels, LEDStatusIndicator, ModeloBase, QFont, QFrame, QLabel, QVBoxLayout |
| ConexionPanelVista    | WARN     | FeatureEnvy | —     | —      | `actualizar` accede más a `modelo` que a `self` |
| ConexionPanelVista    | WARN     | LCOM        | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| ConexionPanelVista    | WARN     | LongMethod  | 71    | 20     | `_setup_ui` demasiado largo |
| ControlPanelControlador | WARN  | LCOM        | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ControlPanelVista     | CRITICAL | CBO         | 8     | 5      | Acoplado a: ConfigControlPanelVista, ModeloBase, QFont, QFrame, QHBoxLayout, QLabel, QSlider, QVBoxLayout |
| ControlPanelVista     | WARN     | LCOM        | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ControlPanelVista     | WARN     | LongMethod  | 70    | 20     | `_setup_ui` demasiado largo |
| ControlPanelVista     | WARN     | LongMethod  | 21    | 20     | `actualizar` demasiado largo |

### 2.3 Análisis de los hallazgos

**CBO elevado en vistas (CRITICAL):** Las tres vistas acopladas a widgets Qt nativos (QLabel, QFrame, QVBoxLayout, etc.) superan el umbral de 5. Este acoplamiento es estructuralmente inevitable en PyQt6: una vista necesita importar los componentes del framework para construir la UI. El umbral de 5 no contempla frameworks de UI. No representa un problema real de diseño.

**LCOM en clases MVC:** Los valores LCOM=2-3 en modelos y controladores MVC son una consecuencia del patron, no un defecto. Un modelo con getters para distintos campos de datos naturalmente tiene grupos de metodos sin atributos compartidos. El umbral de 1 es apropiado para clases de dominio puro, no para clases MVC.

**LongMethod en `_setup_ui`:** Los metodos `_setup_ui` de 55-71 lineas son procedurales por la naturaleza de PyQt (crear widget, configurar propiedades, agregar al layout, repetir). Son legibles y tienen una unica responsabilidad. Sin embargo, existe margen para mejorar la organizacion interna extrayendo grupos logicos en metodos privados.

**Feature Envy en `ConexionPanelVista.actualizar`:** El metodo accede mas veces al objeto `modelo` que a `self`. En el patron MVC esto es esperado: el controlador/vista actualiza su estado leyendo el modelo. No es feature envy genuino.

---

## 3. ArchitectAnalyst

Análisis de métricas de Martin (Ca, Ce, I, A, D) y ciclos de dependencias.

| Metrica           | Critical | Warnings | Info |
|-------------------|----------|----------|------|
| D (Distancia)     | 17       | 0        | 18   |

**Todos los modulos tienen D=1.00** (A=0.00, I=0.00): son modulos estables y concretos, sin clases abstractas ni dependencias externas al proyecto.

Modulos afectados: `comunicacion/cliente_bateria`, `comunicacion/servicio_envio`, `configuracion/config`, `coordinator`, `dominio/estado_bateria`, `dominio/generador_bateria`, `factory`, y todos los MVC de presentacion.

**Análisis:** La metrica D de Martin penaliza los modulos que no usan abstracciones (interfaces, ABCs) cuando son estables. El proyecto adopta una arquitectura de implementaciones concretas de forma intencional — decision valida para el alcance y tamaño del sistema. No hay ciclos de dependencias detectados, lo que confirma que la arquitectura es coherente.

---

## 4. Conclusiones

| Herramienta        | Estado | Observacion |
|--------------------|--------|-------------|
| CodeGuard          | OK     | Sin errores ni warnings en ningun paquete |
| DesignReviewer     | ATENC. | 3 criticos por CBO en vistas PyQt (umbral conservador para UI) |
| ArchitectAnalyst   | ATENC. | 17 criticos por ausencia de abstracciones (decision de diseño) |

El simulador tiene **buena calidad de código** y **arquitectura coherente sin ciclos**. Los hallazgos criticos son consecuencia de umbrales calibrados para sistemas con inversion de dependencias explicita, no para aplicaciones de escritorio PyQt.

---

## 5. Lista de mejoras recomendadas

### Prioridad alta

**M1 — Ajustar umbrales en pyproject.toml**
Los umbrales default no contemplan proyectos PyQt. Crear `pyproject.toml` por producto con:
```toml
[tool.designreviewer]
max_cbo = 10           # vistas PyQt acoplan widgets inevitablemente
max_method_lines = 50  # _setup_ui es proceduralmen largo por naturaleza
max_lcom = 3           # clases MVC tienen grupos de metodos naturalmente separados
```

### Prioridad media

**M2 — Refactorizar `_setup_ui` en submétodos privados**
Los metodos `_setup_ui` de 55-71 lineas en `ConexionPanelVista`, `ControlPanelVista` y `PanelEstadoVista` pueden organizarse en submétodos privados que agrupen responsabilidades logicas:
- `_crear_widgets()` — instanciacion de widgets
- `_configurar_estilos()` — fuentes, colores, frames
- `_ensamblar_layout()` — composicion del layout

Esto no cambia el comportamiento pero mejora la legibilidad y reduce el LongMethod warning.

**M3 — Revisar cohesion de `ClienteBateria`**
LCOM=3 indica que `ClienteBateria` tiene 3 grupos de metodos independientes. Verificar si agrupa responsabilidades que podrian separarse (configuracion de conexion vs logica de envio vs manejo de errores).

### Prioridad baja

**M4 — Introducir interfaces en capa de comunicacion (opcional)**
Para resolver las violaciones de Distancia de Martin, introducir ABCs en `comunicacion` (`IClienteBateria`) y `dominio` (`IGeneradorBateria`). Permite testear con mocks tipados y elimina la dependencia directa a implementaciones concretas. Solo recomendado si el sistema escala o requiere multiples implementaciones.
