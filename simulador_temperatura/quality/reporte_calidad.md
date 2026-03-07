# Reporte de Calidad - Simulador Temperatura

**Fecha:** 2026-03-07
**Herramienta:** software_limpio v0.3.0 (CodeGuard + DesignReviewer + ArchitectAnalyst)
**Fuente analizada:** `simulador_temperatura/app/`

---

## 1. CodeGuard

Análisis de calidad de código: complejidad ciclomática, PEP8, seguridad, imports.

| Paquete        | Errores | Warnings | Info |
|----------------|---------|----------|------|
| comunicacion   | 0       | 0        | 9    |
| configuracion  | 0       | 0        | 9    |
| dominio        | 0       | 0        | 12   |
| presentacion   | 0       | **6**    | 64   |

### 1.1 Detalle de warnings — presentacion

Todos son imports no usados (F401) y una variable asignada pero nunca usada (F841):

| Archivo | Codigo | Detalle |
|---------|--------|---------|
| `paneles/conexion/controlador.py` | F401 | `ConfigPanelConexionVista` importado pero no usado |
| `paneles/conexion/vista.py` | F401 | `EstadoConexion` importado pero no usado |
| `paneles/control_temperatura/controlador.py` | F401 | `ModoOperacion` importado pero no usado |
| `paneles/control_temperatura/vista.py` | F401 | `dataclasses.dataclass` importado pero no usado |
| `paneles/control_temperatura/vista.py` | F401 | `ModoOperacion` importado pero no usado |
| `paneles/grafico/controlador.py` | F841 | variable `tiempo_relativo` asignada pero nunca usada |

**Conclusion:** 6 warnings reales y accionables. Son imports residuales de refactorizaciones anteriores y una variable muerta. No afectan el comportamiento pero ensucian el codigo.

---

## 2. DesignReviewer

Análisis de calidad de diseño: acoplamiento (CBO), cohesión (LCOM), complejidad de clase (WMC), métodos largos, code smells.

### 2.1 Por paquete

| Paquete        | Critical | Warnings |
|----------------|----------|----------|
| configuracion  | 0        | 1        |
| dominio        | 0        | 2        |
| comunicacion   | 0        | 4        |
| presentacion   | **13**   | 35       |

### 2.2 Detalle de hallazgos

**configuracion**

| Clase         | Tipo | Metrica    | Valor | Umbral | Detalle |
|---------------|------|------------|-------|--------|---------|
| ConfigManager | WARN | LongMethod | 23    | 20     | `_cargar_desde_archivo` demasiado largo |

**dominio**

| Clase               | Tipo | Metrica    | Valor | Umbral | Detalle |
|---------------------|------|------------|-------|--------|---------|
| GeneradorTemperatura| WARN | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| GeneradorTemperatura| WARN | LongMethod | 27    | 20     | `__init__` demasiado largo |

**comunicacion**

| Clase                   | Tipo | Metrica    | Valor | Umbral | Detalle |
|-------------------------|------|------------|-------|--------|---------|
| ClienteTemperatura      | WARN | LCOM       | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| ClienteTemperatura      | WARN | LongMethod | 27    | 20     | `__init__` demasiado largo |
| ServicioEnvioTemperatura| WARN | LCOM       | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| ServicioEnvioTemperatura| WARN | LongMethod | 22    | 20     | `__init__` demasiado largo |

**presentacion**

| Clase                      | Tipo     | Metrica           | Valor | Umbral | Detalle |
|----------------------------|----------|-------------------|-------|--------|---------|
| GraficoTemperatura         | CRITICAL | CBO               | 6     | 5      | Acoplado a: ConfigGrafico, InfiniteLine, PlotWidget, QVBoxLayout, QWidget, deque |
| GraficoTemperatura         | CRITICAL | WMC               | 22    | 20     | Complejidad total de métodos excesiva |
| GraficoTemperatura         | WARN     | LongMethod        | 26    | 20     | `__init__` demasiado largo |
| GraficoTemperatura         | WARN     | LongMethod        | 45    | 20     | `_setup_ui` demasiado largo |
| GraficoTemperatura         | WARN     | LongMethod        | 21    | 20     | `add_punto` demasiado largo |
| GraficoTemperatura         | WARN     | LongMethod        | 26    | 20     | `set_limites_referencia` demasiado largo |
| PanelEstado                | CRITICAL | CBO               | 6     | 5      | Acoplado a: ConfigPanelEstado, QFont, QFrame, QLabel, QVBoxLayout, QWidget |
| PanelEstado                | WARN     | LongMethod        | 44    | 20     | `_setup_ui` demasiado largo |
| UIPrincipal                | CRITICAL | CBO               | 15    | 5      | Acoplado a 15 clases (widgets + configs + componentes) |
| UIPrincipal                | CRITICAL | WMC               | 21    | 20     | Complejidad total de métodos excesiva |
| UIPrincipal                | WARN     | LongMethod        | 31    | 20     | `__init__` demasiado largo |
| UIPrincipal                | WARN     | LongMethod        | 64    | 20     | `_setup_ui` demasiado largo |
| UIPrincipal                | WARN     | LongParameterList | 7     | 5      | `__init__` con demasiados parámetros |
| PanelParametrosSenoidal    | CRITICAL | CBO               | 6     | 5      | Acoplado a: ParametrosSenoidal, QGroupBox, QVBoxLayout, QWidget, RangosControl, SliderConValor |
| ControlTemperatura         | CRITICAL | CBO               | 10    | 5      | Acoplado a: PanelParametrosSenoidal, PanelTemperaturaManual, ParametrosSenoidal, QComboBox, ... |
| SliderConValor             | WARN     | LongParameterList | 7     | 5      | `__init__` con 7 parámetros |
| SliderConValor             | WARN     | DataClump         | —     | —      | `{label, max_val, min_val, valor_inicial}` aparecen juntos en 2 funciones |
| PanelParametrosSenoidal    | WARN     | LCOM              | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| PanelTemperaturaManual     | WARN     | LCOM              | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| PanelParametrosSenoidal    | WARN     | LongMethod        | 32    | 20     | `_setup_ui` demasiado largo |
| ControlTemperatura         | WARN     | LongMethod        | 28    | 20     | `_setup_ui` demasiado largo |
| ControlTemperatura         | WARN     | DataClump         | —     | —      | `{parent, rangos, temperatura_inicial}` aparecen juntos en 2 funciones |
| UIPrincipalCompositor      | CRITICAL | CBO               | 9     | 5      | Acoplado a: 4 controladores + 4 clases Qt |
| UIPrincipalCompositor      | WARN     | LongMethod        | 29    | 20     | `__init__` demasiado largo |
| UIPrincipalCompositor      | WARN     | LongMethod        | 48    | 20     | `_setup_ui` demasiado largo |
| UIPrincipalCompositor      | WARN     | LongParameterList | 6     | 5      | `__init__` con 6 parámetros |
| PanelEstadoVista           | CRITICAL | CBO               | 6     | 5      | Acoplado a: ConfigPanelEstadoVista, ModeloBase, QFont, QFrame, QLabel, QVBoxLayout |
| PanelEstadoVista           | WARN     | LongMethod        | 46    | 20     | `_setup_ui` demasiado largo |
| PanelEstadoVista           | WARN     | LongMethod        | 28    | 20     | `actualizar` demasiado largo |
| ConfiguracionConexion      | WARN     | LCOM              | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| PanelConexionControlador   | WARN     | LCOM              | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| PanelConexionControlador   | WARN     | LongMethod        | 27    | 20     | `__init__` demasiado largo |
| PanelConexionVista         | CRITICAL | CBO               | 6     | 5      | Acoplado a: ConfigPanel, ConfigPanelConexionVista, ConfigPanelLabels, ModeloBase, QVBoxLayout, QWidget |
| PanelConexionVista         | WARN     | LongMethod        | 21    | 20     | `__init__` demasiado largo |
| ParametrosControl          | WARN     | LCOM              | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ControlTemperaturaControlador | CRITICAL | WMC            | 21    | 20     | Complejidad total de métodos excesiva |
| ControlTemperaturaControlador | WARN   | LCOM             | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ControlTemperaturaControlador | WARN   | LongMethod       | 21    | 20     | `__init__` demasiado largo |
| ControlTemperaturaVista    | CRITICAL | CBO               | 10    | 5      | Acoplado a: 10 clases (widgets Qt + componentes propios) |
| ControlTemperaturaVista    | WARN     | LongMethod        | 67    | 20     | `_setup_ui` demasiado largo |
| ControlTemperaturaVista    | WARN     | LongParameterList | 7     | 5      | `SliderConValor.__init__` con 7 parámetros |
| ControlTemperaturaVista    | WARN     | DataClump         | —     | —      | `{label, max_val, min_val, valor_inicial}` aparecen juntos |
| GraficoTemperaturaVista    | CRITICAL | CBO               | 6     | 5      | Acoplado a: ConfigGrafico, InfiniteLine, ModeloBase, PlotWidget, QVBoxLayout, QWidget |
| GraficoTemperaturaVista    | WARN     | FeatureEnvy       | —     | —      | `actualizar` accede 5 veces a `modelo` vs 4 a self |
| GraficoTemperaturaVista    | WARN     | LongMethod        | 33    | 20     | `_setup_ui` demasiado largo |
| GraficoTemperaturaVista    | WARN     | LongMethod        | 23    | 20     | `actualizar` demasiado largo |

### 2.3 Análisis de los hallazgos

**CBO elevado en vistas (CRITICAL):** Mismo patrón que simulador_bateria — las vistas PyQt necesariamente acoplan widgets del framework. El umbral de 5 no es adecuado para proyectos de UI. No representa un problema real.

**UIPrincipal: CBO=15 (CRITICAL):** Este sí merece atención. `UIPrincipal` es la ventana principal heredada del periodo previo a la arquitectura MVC+Compositor. Concentra demasiadas responsabilidades: importa 7 clases de configuración, 3 componentes de UI y 5 widgets Qt. El `UIPrincipalCompositor` fue creado precisamente para reemplazarla. Verificar si `UIPrincipal` sigue siendo necesaria o puede eliminarse.

**WMC elevado (CRITICAL):** `GraficoTemperatura`, `UIPrincipal` y `ControlTemperaturaControlador` superan el WMC=20. Refleja clases con muchos métodos de mediana complejidad. Relacionado directamente con la mayor funcionalidad de este simulador (modo automático senoidal + panel gráfico).

**DataClump en SliderConValor:** Los parámetros `{label, max_val, min_val, valor_inicial}` viajan juntos en múltiples funciones. Candidato claro para encapsular en un dataclass `ConfigSlider`.

**LongParameterList en SliderConValor (7 parámetros):** Consistente con el hallazgo de Data Clump anterior.

**LCOM en clases MVC y FeatureEnvy:** Misma interpretacion que simulador_bateria — son artefactos del patron, no defectos reales.

---

## 3. ArchitectAnalyst

Análisis de métricas de Martin (Ca, Ce, I, A, D) y ciclos de dependencias.

| Metrica           | Critical | Warnings | Info |
|-------------------|----------|----------|------|
| D (Distancia)     | 24       | 0        | 25   |

**Todos los modulos tienen D=1.00** (A=0.00, I=0.00): mismo patron que simulador_bateria. El numero es mayor (24 vs 17) por los módulos adicionales del simulador de temperatura (panel gráfico, modo senoidal, `variacion_senoidal`, `ui_principal`).

No se detectaron ciclos de dependencias. La arquitectura es coherente.

---

## 4. Conclusiones

| Herramienta        | Estado | Observacion |
|--------------------|--------|-------------|
| CodeGuard          | ATENC. | 6 warnings reales: imports no usados y variable muerta en presentacion |
| DesignReviewer     | ATENC. | 13 criticos en presentacion (CBO/WMC). UIPrincipal con CBO=15 merece revision |
| ArchitectAnalyst   | ATENC. | 24 criticos D=1.00 — misma decision de diseño que simulador_bateria |

En comparacion con simulador_bateria, este simulador tiene mayor superficie de hallazgos por su mayor complejidad funcional (modo automático senoidal, panel gráfico pyqtgraph). Los hallazgos mas relevantes son los imports no usados (accionables de inmediato) y el Data Clump en `SliderConValor`.

---

## 5. Lista de mejoras recomendadas

### Prioridad alta

**M1 — Eliminar imports no usados y variable muerta**
6 hallazgos directos de CodeGuard. Limpieza inmediata sin riesgo:
- Eliminar `ConfigPanelConexionVista` de `paneles/conexion/controlador.py`
- Eliminar `EstadoConexion` de `paneles/conexion/vista.py`
- Eliminar `ModoOperacion` de `paneles/control_temperatura/controlador.py`
- Eliminar `dataclasses.dataclass` y `ModoOperacion` de `paneles/control_temperatura/vista.py`
- Eliminar o usar variable `tiempo_relativo` en `paneles/grafico/controlador.py`

**M2 — Encapsular parámetros de SliderConValor en un dataclass**
Data Clump confirmado: `{label, max_val, min_val, valor_inicial}` aparecen juntos en múltiples firmas. Crear `ConfigSlider` reduce los 7 parámetros del constructor a 2-3 y elimina la duplicación:
```python
@dataclass
class ConfigSlider:
    label: str
    min_val: float
    max_val: float
    valor_inicial: float
```

### Prioridad media

**M3 — Revisar si UIPrincipal puede eliminarse**
`UIPrincipal` (CBO=15, WMC=21) fue la ventana principal original. El `UIPrincipalCompositor` fue creado para reemplazarla con mejor separacion de responsabilidades. Si `UIPrincipal` ya no es el punto de entrada, eliminarla reduce la deuda de diseño significativamente.

**M4 — Refactorizar `_setup_ui` en submétodos privados**
Mismo hallazgo que simulador_bateria. Aplicar en `GraficoTemperatura`, `ControlTemperaturaVista`, `UIPrincipalCompositor` y `PanelEstadoVista`. Dividir en `_crear_widgets()`, `_configurar_estilos()`, `_ensamblar_layout()`.

**M5 — Ajustar umbrales en pyproject.toml**
Igual que simulador_bateria, crear `pyproject.toml` con umbrales calibrados para PyQt:
```toml
[tool.designreviewer]
max_cbo = 10
max_method_lines = 50
max_lcom = 3
```

### Prioridad baja

**M6 — Introducir interfaces en capa de comunicacion (opcional)**
Mismo hallazgo que simulador_bateria. Solo recomendado si el sistema escala.
