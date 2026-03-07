# Reporte de Calidad - UX Termostato

**Fecha:** 2026-03-07
**Herramienta:** software_limpio v0.3.0 (CodeGuard + DesignReviewer + ArchitectAnalyst)
**Fuente analizada:** `ux_termostato/app/`

---

## 1. CodeGuard

Análisis de calidad de código: complejidad ciclomática, PEP8, seguridad, imports.

| Paquete        | Errores | Warnings | Info |
|----------------|---------|----------|------|
| comunicacion   | 0       | **2**    | 7    |
| configuracion  | 0       | 0        | 6    |
| dominio        | 0       | 0        | 9    |
| presentacion   | 0       | **24**   | 98   |

### 1.1 Detalle de warnings — comunicacion

| Archivo               | Codigo | Detalle |
|-----------------------|--------|---------|
| `servidor_estado.py`  | B104   | **Security:** Posible binding a todas las interfaces (0.0.0.0). |
| `cliente_comandos.py` | F401   | `json` importado pero no usado. |

**Nota sobre B104:** El servidor TCP escucha en todas las interfaces de red. En un entorno HIL de laboratorio esto es intencional (escucha conexiones desde la RPi), pero es una superficie de exposicion que merece documentarse explicitamente.

### 1.2 Detalle de warnings — presentacion

| Archivo                    | Codigo | Detalle |
|----------------------------|--------|---------|
| `ui_principal.py`          | E402   | 4 imports a nivel de modulo fuera del encabezado |
| `ui_principal.py`          | F401   | `UXCoordinator` importado pero no usado (linea 24) |
| `ui_principal.py`          | F811   | Redefinicion de `UXCoordinator` (import duplicado) |
| `ui_compositor.py`         | F401   | `QSize` importado pero no usado |
| `controlador.py` (display) | E128   | 8 lineas con indentacion de continuacion incorrecta |
| `controlador.py` (display) | F841   | Variable `comando` asignada pero nunca usada |
| `controlador.py` (display) | E501   | 2 lineas demasiado largas (117 y 118 caracteres, umbral 100) |
| `vista.py` (control_temp)  | F401   | `QHBoxLayout` importado pero no usado |
| `vista.py` (control_temp)  | F401   | `Qt` importado pero no usado |
| `vista.py` (control_temp)  | E128   | 1 linea con indentacion de continuacion incorrecta |

---

## 2. DesignReviewer

Análisis de calidad de diseño: acoplamiento (CBO), cohesión (LCOM), complejidad (WMC), métodos largos, code smells.

### 2.1 Por paquete

| Paquete        | Critical | Warnings |
|----------------|----------|----------|
| configuracion  | 0        | 2        |
| dominio        | 0        | 2        |
| comunicacion   | 0        | 7        |
| presentacion   | **7**    | 62       |

### 2.2 Detalle de hallazgos

**configuracion**

| Clase     | Tipo | Metrica    | Valor | Umbral | Detalle |
|-----------|------|------------|-------|--------|---------|
| ConfigUX  | WARN | LongMethod | 40    | 20     | `__post_init__` demasiado largo |
| ConfigUX  | WARN | LongMethod | 32    | 20     | `from_dict` demasiado largo |

**dominio**

| Clase            | Tipo | Metrica    | Valor | Umbral | Detalle |
|------------------|------|------------|-------|--------|---------|
| EstadoTermostato | WARN | LongMethod | 36    | 20     | `__post_init__` demasiado largo |
| EstadoTermostato | WARN | LongMethod | 30    | 20     | `from_json` demasiado largo |

**comunicacion**

| Clase              | Tipo | Metrica    | Valor | Umbral | Detalle |
|--------------------|------|------------|-------|--------|---------|
| ServidorEstado     | WARN | LCOM       | 6     | 1      | 6 grupos de métodos sin atributos compartidos |
| ServidorEstado     | WARN | LongMethod | 26    | 20     | `__init__` demasiado largo |
| ServidorEstado     | WARN | LongMethod | 21    | 20     | `iniciar` demasiado largo |
| ServidorEstado     | WARN | LongMethod | 50    | 20     | `_procesar_mensaje` demasiado largo |
| ClienteComandos    | WARN | LongMethod | 27    | 20     | `__init__` demasiado largo |
| ClienteComandos    | WARN | LongMethod | 74    | 20     | `enviar_comando` demasiado largo |
| ClienteComandos    | WARN | LongMethod | 39    | 20     | `_adaptar_comando_a_texto` demasiado largo |

**presentacion**

| Clase                    | Tipo     | Metrica    | Valor | Umbral | Detalle |
|--------------------------|----------|------------|-------|--------|---------|
| VentanaPrincipalUX       | CRITICAL | GodObject  | 307   | 300    | Clase dios: acumula demasiadas responsabilidades |
| VentanaPrincipalUX       | WARN     | LCOM       | 5     | 1      | 5 grupos de métodos sin atributos compartidos |
| VentanaPrincipalUX       | WARN     | LongMethod | 28    | 20     | `_configurar_ventana` demasiado largo |
| VentanaPrincipalUX       | WARN     | LongMethod | 36    | 20     | `_crear_componentes` demasiado largo |
| VentanaPrincipalUX       | WARN     | LongMethod | 35    | 20     | `_crear_coordinator` demasiado largo |
| VentanaPrincipalUX       | WARN     | LongMethod | 59    | 20     | `_crear_ui` demasiado largo |
| VentanaPrincipalUX       | WARN     | LongMethod | 43    | 20     | `iniciar` demasiado largo |
| VentanaPrincipalUX       | WARN     | LongMethod | 26    | 20     | `cerrar` demasiado largo |
| UICompositor             | WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| UICompositor             | WARN     | LongMethod | 28    | 20     | `__init__` demasiado largo |
| UICompositor             | WARN     | LongMethod | 21    | 20     | `_validar_paneles` demasiado largo |
| UICompositor             | WARN     | LongMethod | 22    | 20     | `_extraer_vista` demasiado largo |
| UICompositor             | WARN     | LongMethod | 56    | 20     | `crear_layout` demasiado largo |
| UICompositor             | WARN     | LongMethod | 25    | 20     | `_crear_header` demasiado largo |
| PowerControlador         | WARN     | LongMethod | 25    | 20     | `cambiar_estado` demasiado largo |
| PowerVista               | WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| PowerVista               | WARN     | LongMethod | 28    | 20     | `_setup_ui` demasiado largo |
| PowerVista               | WARN     | LongMethod | 22    | 20     | `_aplicar_estilo_apagado` demasiado largo |
| PowerVista               | WARN     | LongMethod | 22    | 20     | `_aplicar_estilo_encendido` demasiado largo |
| ControlTempModelo        | WARN     | LongMethod | 23    | 20     | `to_dict` demasiado largo |
| ControlTempControlador   | WARN     | LongMethod | 47    | 20     | `aumentar_temperatura` demasiado largo |
| ControlTempControlador   | WARN     | LongMethod | 44    | 20     | `disminuir_temperatura` demasiado largo |
| ControlTempControlador   | WARN     | LongMethod | 27    | 20     | `set_temperatura_actual` demasiado largo |
| ControlTempControlador   | WARN     | LongMethod | 24    | 20     | `_generar_comando_temperatura` demasiado largo |
| ControlTempVista         | CRITICAL | CBO        | 7     | 5      | Acoplado a: ControlTempModelo, QFont, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget |
| ControlTempVista         | WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ControlTempVista         | WARN     | LongMethod | 68    | 20     | `_setup_ui` demasiado largo |
| ControlTempVista         | WARN     | LongMethod | 48    | 20     | `_aplicar_estilo_subir` demasiado largo |
| ControlTempVista         | WARN     | LongMethod | 48    | 20     | `_aplicar_estilo_bajar` demasiado largo |
| ControlTempVista         | WARN     | LongMethod | 25    | 20     | `actualizar` demasiado largo |
| ClimatizadorControlador  | WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ClimatizadorControlador  | WARN     | LongMethod | 23    | 20     | `actualizar_estado` demasiado largo |
| ClimatizadorControlador  | WARN     | LongMethod | 22    | 20     | `actualizar_desde_estado` demasiado largo |
| ClimatizadorVista        | CRITICAL | CBO        | 7     | 5      | Acoplado a: ClimatizadorModelo, QFont, QHBoxLayout, QLabel, QPropertyAnimation, QVBoxLayout, QWidget |
| ClimatizadorVista        | WARN     | LCOM       | 4     | 1      | 4 grupos de métodos sin atributos compartidos |
| ClimatizadorVista        | WARN     | LongMethod | 45    | 20     | `_crear_indicador` demasiado largo |
| ClimatizadorVista        | WARN     | LongMethod | 45    | 20     | `_aplicar_estilos` demasiado largo |
| ClimatizadorVista        | WARN     | LongMethod | 36    | 20     | `_set_indicador_activo` demasiado largo |
| ClimatizadorVista        | WARN     | LongMethod | 21    | 20     | `_iniciar_animacion` demasiado largo |
| ConexionModelo           | WARN     | LongMethod | 33    | 20     | `validar_ip` demasiado largo |
| ConexionControlador      | WARN     | LongMethod | 22    | 20     | `__init__` demasiado largo |
| ConexionControlador      | WARN     | LongMethod | 21    | 20     | `_on_ip_changed` demasiado largo |
| ConexionVista            | CRITICAL | CBO        | 8     | 5      | Acoplado a: ConexionModelo, QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget |
| ConexionVista            | WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| ConexionVista            | WARN     | LongMethod | 115   | 20     | `_inicializar_ui` con **115 lineas** — el metodo mas largo del proyecto |
| ConexionVista            | WARN     | LongMethod | 29    | 20     | `actualizar` demasiado largo |
| IndicadoresControlador   | CRITICAL | WMC        | 22    | 20     | Complejidad total de métodos excesiva |
| IndicadoresControlador   | WARN     | LongMethod | 21    | 20     | `actualizar_falla_sensor` demasiado largo |
| IndicadoresControlador   | WARN     | LongMethod | 21    | 20     | `actualizar_bateria_baja` demasiado largo |
| IndicadoresControlador   | WARN     | LongMethod | 35    | 20     | `actualizar_desde_estado` demasiado largo |
| AlertLED                 | CRITICAL | CBO        | 7     | 5      | Acoplado a: LEDColor, LEDIndicator, QFont, QLabel, QTimer, QVBoxLayout, QWidget |
| AlertLED                 | WARN     | LongMethod | 39    | 20     | `__init__` demasiado largo |
| IndicadoresVista         | WARN     | LCOM       | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| IndicadoresVista         | WARN     | LongMethod | 28    | 20     | `actualizar` demasiado largo |
| SelectorVistaControlador | WARN     | LongMethod | 22    | 20     | `__init__` demasiado largo |
| SelectorVistaVista       | CRITICAL | CBO        | 6     | 5      | Acoplado a: QButtonGroup, QHBoxLayout, QLabel, QPushButton, QWidget, SelectorVistaModelo |
| SelectorVistaVista       | WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| SelectorVistaVista       | WARN     | LongMethod | 32    | 20     | `_inicializar_ui` demasiado largo |
| SelectorVistaVista       | WARN     | LongMethod | 53    | 20     | `_aplicar_estilos` demasiado largo |
| DisplayControlador       | WARN     | FeatureEnvy| —     | —      | `actualizar_desde_estado` accede 6 veces a `estado_termostato` vs 5 a self |
| DisplayControlador       | WARN     | LongMethod | 21    | 20     | `cambiar_modo_vista` demasiado largo |
| DisplayControlador       | WARN     | LongMethod | 32    | 20     | `actualizar_desde_estado` demasiado largo |
| DisplayVista             | WARN     | LCOM       | 3     | 1      | 3 grupos de métodos sin atributos compartidos |
| DisplayVista             | WARN     | LongMethod | 59    | 20     | `_setup_ui` demasiado largo |
| DisplayVista             | WARN     | LongMethod | 39    | 20     | `_aplicar_estilos` demasiado largo |
| DisplayVista             | WARN     | LongMethod | 43    | 20     | `actualizar` demasiado largo |
| EstadoConexionControlador| WARN     | LCOM       | 2     | 1      | 2 grupos de métodos sin atributos compartidos |
| EstadoConexionVista      | CRITICAL | CBO        | 6     | 5      | Acoplado a: EstadoConexionModelo, LEDIndicator, QHBoxLayout, QLabel, QTimer, QWidget |
| EstadoConexionVista      | WARN     | LongMethod | 22    | 20     | `_inicializar_ui` demasiado largo |
| EstadoConexionVista      | WARN     | LongMethod | 27    | 20     | `actualizar` demasiado largo |

### 2.3 Análisis de los hallazgos

**VentanaPrincipalUX — God Object (CRITICAL):** Con 307 líneas es el único hallazgo genuino de God Object en todo el proyecto. Concentra la creacion de componentes, coordinacion de signals, configuracion de ventana, lifecycle de inicio y cierre. Es el punto de entrada de la aplicacion y fue creciendo iterativamente. Este si es un candidato real para refactorizar.

**CBO elevado en vistas (CRITICAL):** Mismo patron que los simuladores — acoplamiento a widgets PyQt inevitable. No representa un problema real para el contexto del proyecto.

**ClienteComandos.enviar_comando — 74 lineas (WARN):** El metodo mas largo de la capa de comunicacion. Maneja la logica de envio TCP, reintentos y errores. Candidato para extraer submétodos por responsabilidad.

**ConexionVista._inicializar_ui — 115 lineas (WARN):** El metodo mas largo de todo el proyecto. Construye un formulario complejo de configuracion de IP/puerto con validacion visual. Refactorizable en submétodos por seccion del formulario.

**ServidorEstado — LCOM=6 (WARN):** 6 grupos de métodos independientes es el valor mas alto de LCOM encontrado en el proyecto. Indica que `ServidorEstado` acumula responsabilidades de threading, parsing, callbacks y estado de conexion. Candidato para descomposicion.

**FeatureEnvy y LCOM en controladores MVC:** Mismo analisis que los simuladores — artefactos del patron MVC, no defectos reales.

---

## 3. ArchitectAnalyst

Análisis de métricas de Martin (Ca, Ce, I, A, D) y ciclos de dependencias.

| Metrica           | Critical | Warnings | Info |
|-------------------|----------|----------|------|
| D (Distancia)     | 33       | 0        | 33   |

**Todos los modulos tienen D=1.00** salvo `dominio/comandos` con **D=0.83 (A=0.17)** — tiene una clase parcialmente abstracta, lo que lo ubica levemente mejor en la Main Sequence. Es el unico modulo del proyecto con alguna abstraccion.

No se detectaron ciclos de dependencias. La arquitectura es coherente.

---

## 4. Conclusiones

| Herramienta        | Estado | Observacion |
|--------------------|--------|-------------|
| CodeGuard          | ATENC. | 26 warnings: imports residuales, PEP8 y un warning de seguridad (B104) |
| DesignReviewer     | ATENC. | 7 criticos: God Object en VentanaPrincipalUX + CBO en vistas PyQt |
| ArchitectAnalyst   | ATENC. | 33 criticos D=1.00 — mismo patron que los simuladores |

El UX es el producto con mayor superficie de hallazgos, consistente con ser el mas complejo funcionalmente (8 paneles, comunicacion bidireccional, lifecycle completo). El hallazgo mas relevante y accionable es el **God Object en `VentanaPrincipalUX`**, que concentra demasiadas responsabilidades en un solo archivo. Los imports residuales y la variable muerta son limpieza inmediata.

**Comparativa entre los tres productos:**

| Producto              | CodeGuard Warns | Design Critical | Arch Critical |
|-----------------------|-----------------|-----------------|---------------|
| simulador_bateria     | 0               | 3               | 17            |
| simulador_temperatura | 6               | 13              | 24            |
| ux_termostato         | **26**          | 7               | 33            |

---

## 5. Lista de mejoras recomendadas

### Prioridad alta

**M1 — Eliminar imports no usados y limpiar PEP8**
Limpieza inmediata sin riesgo en `ui_principal.py`, `ui_compositor.py`, `cliente_comandos.py` y los controladores/vistas de `presentacion`:
- Eliminar import duplicado de `UXCoordinator` en `ui_principal.py` (F401 + F811)
- Mover imports fuera del cuerpo de funciones en `ui_principal.py` (E402)
- Eliminar `json` de `cliente_comandos.py` (F401)
- Eliminar `QSize`, `QHBoxLayout`, `Qt` no usados en vistas (F401)
- Eliminar o usar variable `comando` en `display/controlador.py` (F841)
- Corregir indentacion de continuacion en `display/controlador.py` (E128)

**M2 — Documentar explicitamente el binding a todas las interfaces (B104)**
El servidor TCP en `servidor_estado.py` escucha en 0.0.0.0 de forma intencional para recibir datos de la RPi. Agregar un comentario que documente esta decision y agregar `# noqa: B104` para suprimir el warning con contexto.

### Prioridad media

**M3 — Refactorizar VentanaPrincipalUX (God Object)**
Con 307 lineas y LCOM=5, esta clase concentra cinco responsabilidades distintas. Separar en:
- Mantener `VentanaPrincipalUX` como facade liviano (lifecycle)
- Delegar creacion de componentes al `ComponenteFactoryUX` existente
- Delegar coordinacion de signals al `UXCoordinator` existente
El factory y coordinator ya existen — la ventana deberia solo orquestarlos, no implementarlos.

**M4 — Refactorizar `ConexionVista._inicializar_ui` (115 lineas)**
El metodo mas largo del proyecto. Dividir en submétodos por seccion:
- `_crear_grupo_conexion()` — inputs de IP y puerto
- `_crear_grupo_estado()` — indicador LED y etiquetas
- `_crear_botones()` — botones conectar/desconectar
- `_aplicar_estilos()` — estilos visuales

**M5 — Refactorizar `ClienteComandos.enviar_comando` (74 lineas)**
Extraer la logica de preparacion del comando, el envio TCP y el manejo de errores en metodos privados separados.

**M6 — Revisar cohesion de ServidorEstado (LCOM=6)**
El valor mas alto de LCOM en el proyecto. Evaluar si las responsabilidades de threading, parsing de mensajes, gestion de callbacks y estado de conexion pueden separarse en colaboradores especializados.

### Prioridad baja

**M7 — Ajustar umbrales en pyproject.toml**
Igual que los simuladores, crear `pyproject.toml` con umbrales calibrados para PyQt:
```toml
[tool.designreviewer]
max_cbo = 10
max_method_lines = 50
max_lcom = 3
```

**M8 — Introducir interfaces en capa de comunicacion (opcional)**
Mismo hallazgo que los simuladores. Solo recomendado si el sistema escala.
