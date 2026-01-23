# Historias de Usuario - UX Termostato Desktop

## Información del Documento

**Proyecto:** ISSE_Simuladores - UX Termostato Desktop
**Fecha Inicial:** 2026-01-16
**Última Actualización:** 2026-01-23
**Autor:** Victor Valotto
**Versión:** 2.2
**Branch:** main (US-020, US-021 merged)

---

## ⚠️ IMPORTANTE: Replanificación y Progreso

**Replanificación 2026-01-23:**
1. Completar 7 historias de paneles individuales (25 pts)
2. Desestimar 10 historias redundantes o fuera de alcance (28 pts)
3. Refactorizar arquitectura para alinear con simuladores de referencia
4. Definir 6 nuevas historias de integración/arquitectura (28 pts)

**Progreso actual (2026-01-23):**
- ✅ 9 historias completadas (35 pts) - 57% del proyecto
- 🔲 7 historias pendientes (26 pts) - 43% restante
- Sprint 1 (Arquitectura Base): ✅ COMPLETADO (US-020 + US-021)

**Nuevo alcance:** 16 historias - 61 puntos total

---

## Tabla de Contenidos

1. [✅ Historias Completadas](#-historias-completadas)
2. [❌ Historias Desestimadas](#-historias-desestimadas)
3. [🔲 Paneles Pendientes](#-paneles-pendientes)
4. [⭐ Nuevas Historias - Arquitectura](#-nuevas-historias---arquitectura)
5. [📊 Resumen y Planificación](#-resumen-y-planificación)

---

# ✅ HISTORIAS COMPLETADAS

## Épica 1: Visualización de Estado

### US-001: Ver temperatura ambiente actual ✅

**Puntos:** 3 | **Panel:** `app/presentacion/paneles/display/`
**Coverage:** 100% | **Pylint:** 10.00/10 | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** ver la temperatura ambiente actual en un display grande y claro
**Para** conocer en todo momento las condiciones de mi hogar

**Implementación:**
- Display LCD con temperatura en formato X.X °C
- Fuente grande y clara, fondo LCD verde oscuro
- Actualización automática desde JSON
- Manejo de desconexión (muestra "---")
- Patrón MVC completo: modelo, vista, controlador

---

### US-002: Ver estado del climatizador ✅

**Puntos:** 5 | **Panel:** `app/presentacion/paneles/climatizador/`
**Coverage:** 100% | **Pylint:** 10.00/10 | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** ver el estado actual del climatizador (calentando, enfriando, reposo)
**Para** saber si el sistema está actuando para alcanzar la temperatura deseada

**Implementación:**
- 3 indicadores: Calor 🔥 (naranja), Reposo 🌬️ (verde), Frío ❄️ (azul)
- Solo un indicador activo a la vez
- Animaciones pulsantes para calor y frío
- Actualización en tiempo real desde JSON
- Colores apropiados por estado

---

### US-003: Ver indicadores de alerta ✅

**Puntos:** 2 | **Panel:** `app/presentacion/paneles/indicadores/`
**Coverage:** 99% | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** ver indicadores LED que me alerten sobre fallas del sensor o batería baja
**Para** tomar acción cuando haya problemas con el sistema

**Implementación:**
- LED sensor: rojo pulsante cuando `falla_sensor=true`
- LED batería: amarillo pulsante cuando `bateria_baja=true`
- Componente `LedIndicator` de compartido/widgets
- Señales PyQt: `alerta_activada`, `alerta_desactivada`
- Actualización desde JSON del RPi

---

## Épica 2: Control de Temperatura

### US-004: Aumentar temperatura deseada ✅

**Puntos:** 3 | **Panel:** `app/presentacion/paneles/control_temp/`
**Coverage:** 100% | **Pylint:** 10.00/10 | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** poder aumentar la temperatura deseada presionando un botón
**Para** ajustar la climatización de mi hogar según mis necesidades

**Implementación:**
- Botón SUBIR (▲) en color rojo
- Incremento de 0.5°C por click
- Rango máximo: 35°C
- Validación de rango
- Envío de comando JSON al RPi (puerto 14000)
- Solo activo cuando termostato encendido

---

### US-005: Disminuir temperatura deseada ✅

**Puntos:** 3 | **Panel:** `app/presentacion/paneles/control_temp/`
**Coverage:** 100% | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** poder disminuir la temperatura deseada presionando un botón
**Para** reducir la climatización cuando hace demasiado calor o frío

**Implementación:**
- Botón BAJAR (▼) en color azul
- Decremento de 0.5°C por click
- Rango mínimo: 15°C
- Botones SUBIR y BAJAR lado a lado
- Mismo patrón que US-004

---

## Épica 3: Encendido y Apagado

### US-007: Encender el termostato ✅

**Puntos:** 3 | **Panel:** `app/presentacion/paneles/power/`
**Coverage:** 100% | **Pylint:** 10.00/10 | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** poder encender el sistema con un botón
**Para** activar la climatización cuando lo necesite

**Implementación:**
- Botón ENCENDER (⚡) en verde
- Al encender:
  - Display muestra temperatura
  - Controles se habilitan
  - Climatizador comienza a actualizarse
- Envía comando: `{"comando": "power", "estado": "on"}`
- Señal PyQt: `encendido_cambiado(bool)`

---

### US-008: Apagar el termostato ✅

**Puntos:** 2 | **Panel:** `app/presentacion/paneles/power/`
**Coverage:** 100% | **Estado:** COMPLETADA

**Como** usuario del termostato
**Quiero** poder apagar el sistema con un botón
**Para** detener la climatización cuando no la necesite

**Implementación:**
- Botón APAGAR (gris) integrado con US-007
- Al apagar:
  - Display muestra "---"
  - Controles se deshabilitan
  - Climatizador muestra estado apagado
- Envía comando: `{"comando": "power", "estado": "off"}`
- Toggle funcional on/off

**Total Completadas:** 7 historias - 25 puntos (61% del proyecto)

---

# ❌ HISTORIAS DESESTIMADAS

Las siguientes historias fueron desestimadas por las razones indicadas:

## Desestimadas por Redundancia

**US-009: Recibir alerta de falla del sensor** (2 pts)
**Razón:** US-003 ya implementa el LED rojo de alerta. Mostrar "ERROR" en el display agrega complejidad sin valor significativo. El LED es suficiente alerta visual.

**US-010: Recibir alerta de batería baja** (2 pts)
**Razón:** US-003 ya implementa el LED amarillo de alerta. El nivel de batería en footer no es crítico para una aplicación desktop que no depende de batería física.

**US-012: Ver modo actual en el footer** (1 pt)
**Razón:** El estado on/off ya es visible en el botón power. Redundante con otros indicadores existentes.

## Desestimadas por Baja Prioridad / Innecesarias

**US-006: Ver diferencia entre temperatura actual y deseada** (2 pts)
**Razón:** Funcionalidad "nice to have" que no aporta valor crítico. El panel climatizador ya indica si está calentando/enfriando.

**US-014: Configurar puertos de comunicación** (2 pts)
**Razón:** Configuración avanzada innecesaria para usuarios típicos. Los puertos se definen en .env/config.json.

**US-016: Reconectar manualmente al Raspberry Pi** (2 pts)
**Razón:** La reconexión automática es mejor UX. Un botón manual es redundante si la lógica de reconexión automática está bien implementada.

**US-017: Ver información de estado en tiempo real** (3 pts)
**Razón:** Parcialmente cubierta por US-002 (estado climatizador). El "tiempo en estado" es información secundaria sin valor crítico.

## Desestimadas por Responsabilidad del RPi

**US-018: Persistir configuración entre sesiones** (2 pts)
**Razón:** La UX Desktop es un cliente sin estado. El estado del termostato (temperatura deseada, modos) debe persistir en el Raspberry Pi, no en el cliente. La única config local necesaria es IP/puertos en .env.

**US-019: Ver historial de temperatura** (8 pts)
**Razón:** El almacenamiento y análisis de datos históricos es responsabilidad del Raspberry Pi. Si el RPi provee un endpoint de historial, el cliente puede consumirlo. Pero el cliente no debe almacenar datos históricos.

**Total Desestimadas:** 10 historias - 28 puntos

**Principio arquitectónico:** La UX Desktop es un **cliente de visualización y control**, no debe tener lógica de persistencia de estado ni almacenamiento de datos históricos.

---

# 🔲 PANELES PENDIENTES

## Épica 5: Modos de Visualización

### US-011: Cambiar entre vista de temperatura ambiente y deseada

**Prioridad:** Alta | **Puntos:** 3 | **Estado:** PENDIENTE
**Panel:** `app/presentacion/paneles/selector_vista/`

**Como** usuario del termostato
**Quiero** alternar entre ver temperatura ambiente y deseada
**Para** comparar ambos valores fácilmente

**Criterios de Aceptación:**
- [ ] Botón toggle "Ambiente" / "Deseada"
- [ ] Display cambia su label según modo:
  - "Temperatura Ambiente" en modo ambiente
  - "Temperatura Deseada" en modo deseada
- [ ] Cambio instantáneo (sin delay)
- [ ] Envía comando al RPi: `{"comando": "set_modo_display", "modo": "ambiente|deseada"}`
- [ ] Puerto de envío: 14000
- [ ] Solo activo cuando termostato está encendido
- [ ] Optimistic update (cambia local primero)

**Componentes MVC:**
- **Modelo:** `SelectorVistaModelo(modo: str)`
  - `modo` puede ser "ambiente" o "deseada"
  - Validación de valores permitidos

- **Vista:** `SelectorVistaVista`
  - Botón toggle con 2 estados
  - Feedback visual del modo actual
  - Estilos consistentes con otros paneles

- **Controlador:** `SelectorVistaControlador`
  - Señal: `modo_cambiado(str)` - emitida al cambiar modo
  - Conecta con Display para actualizar label
  - Conecta con ClienteComandos para enviar al RPi

**Definición de Hecho:**
- [ ] Panel MVC implementado
- [ ] Tests unitarios (100% coverage)
- [ ] Integración con panel Display
- [ ] Comando JSON enviado correctamente
- [ ] Tests de ambos modos (ambiente/deseada)
- [ ] Pylint ≥ 8.0

---

## Épica 6: Configuración y Conectividad

### US-013: Configurar dirección IP del Raspberry Pi

**Prioridad:** Alta | **Puntos:** 3 | **Estado:** PENDIENTE
**Panel:** `app/presentacion/paneles/conexion/`

**Como** usuario del termostato
**Quiero** configurar la IP del Raspberry Pi
**Para** conectarme al sistema en mi red local

**Criterios de Aceptación:**
- [ ] Campo de texto para IP (formato xxx.xxx.xxx.xxx)
- [ ] Validación de formato IP con regex
- [ ] Feedback visual:
  - Borde verde si válido
  - Borde rojo si inválido
  - Mensaje de error descriptivo
- [ ] Botón "Aplicar" para guardar configuración
- [ ] IP se persiste en config.json
- [ ] IP se carga al iniciar la aplicación
- [ ] Al cambiar IP, se reconecta automáticamente
- [ ] Campos para puertos recv/send (read-only)

**Validación de IP:**
```python
# Regex: ^(\d{1,3}\.){3}\d{1,3}$
# Rango: 0-255 por octeto
# Ejemplos válidos: 192.168.1.50, 127.0.0.1, 10.0.0.1
# Ejemplos inválidos: 999.999.999.999, abc.def.ghi.jkl, 192.168.1
```

**Componentes MVC:**
- **Modelo:** `ConexionModelo(ip: str, puerto_recv: int, puerto_send: int, valido: bool)`
  - Validación de IP en el modelo
  - Puertos por defecto: 14001 (recv), 14000 (send)

- **Vista:** `ConexionVista`
  - Usa `ConfigPanel` de compartido/widgets (si existe)
  - Layout vertical: IP, puertos, botón Aplicar
  - Feedback visual con `ValidationFeedback`

- **Controlador:** `ConexionControlador`
  - Señal: `ip_cambiada(str)` - emitida al aplicar nueva IP
  - Valida formato antes de aceptar
  - Integra con ConfigManager para persistencia

**Definición de Hecho:**
- [ ] Panel MVC implementado
- [ ] Validación de IP robusta
- [ ] Tests unitarios (100% coverage)
- [ ] Integración con ConfigManager
- [ ] Persistencia en config.json funciona
- [ ] Reconexión automática funcional
- [ ] Pylint ≥ 8.0

---

### US-015: Ver estado de conexión con el Raspberry Pi

**Prioridad:** Alta | **Puntos:** 2 | **Estado:** PENDIENTE
**Componente:** Header de `ui_principal.py`

**Como** usuario del termostato
**Quiero** ver si hay conexión activa con el RPi
**Para** saber si los datos son actuales

**Criterios de Aceptación:**
- [ ] Indicador en header: "Estado: ● Conectado"
- [ ] 3 estados posibles:
  - **Conectado:** LED verde, texto "Conectado"
  - **Desconectado:** LED rojo, texto "Desconectado"
  - **Conectando:** LED amarillo pulsante, texto "Conectando..."
- [ ] Actualización en tiempo real
- [ ] Timeout: 10 segundos sin datos = estado "Desconectado"
- [ ] Detección automática de reconexión

**Componentes:**
- **Widget:** `EstadoConexionWidget`
  - Usa `StatusIndicator` de compartido/widgets
  - Layout horizontal: LED + texto
  - Estados sincronizados con ServidorEstado

- **Integración:**
  - Conectado en `ui_principal.py` como parte del header
  - Recibe señales de ServidorEstado:
    - `conexion_establecida` → estado "Conectado"
    - `conexion_perdida` → estado "Desconectado"
    - `conectando` → estado "Conectando"

**Definición de Hecho:**
- [ ] Widget implementado
- [ ] 3 estados funcionan correctamente
- [ ] Detección de timeout implementada
- [ ] Tests de cambios de estado
- [ ] Integración en UI principal
- [ ] Animación pulsante en estado "Conectando"

**Total Paneles Pendientes:** 3 historias - 8 puntos

---

# ⭐ NUEVAS HISTORIAS - ARQUITECTURA

## Épica 8: Arquitectura e Integración (NUEVA)

### US-020: Implementar capa de Dominio

**Prioridad:** CRÍTICA | **Puntos:** 5 | **Estado:** ✅ COMPLETADA
**Componente:** `app/dominio/`
**Branch:** development/simulador-ux-US-020 (merged)
**Coverage:** 100% | **Pylint:** 10.00/10

**Como** desarrollador del sistema
**Quiero** implementar la capa de lógica de negocio
**Para** centralizar el estado del termostato y validación de comandos

**Criterios de Aceptación:**

#### 1. EstadoTermostato (estado_termostato.py) ✅

- [x] Dataclass inmutable (`@dataclass(frozen=True)`)
- [x] Atributos completos del estado:
  ```python
  @dataclass(frozen=True)
  class EstadoTermostato:
      temperatura_actual: float
      temperatura_deseada: float
      modo_climatizador: str  # "calentando", "enfriando", "reposo", "apagado"
      falla_sensor: bool
      bateria_baja: bool
      encendido: bool
      modo_display: str  # "ambiente", "deseada"
      timestamp: datetime
  ```
- [x] Método `from_json(data: dict) -> EstadoTermostato`
  - Parsea JSON del RPi a objeto tipado
  - Manejo de campos opcionales
  - Validación de tipos
- [x] Método `to_dict() -> dict`
  - Serialización para logging/debugging
- [x] Validaciones de rangos:
  - `temperatura_actual`: -40°C a 85°C
  - `temperatura_deseada`: 15°C a 35°C
  - `modo_climatizador`: valores permitidos
  - `modo_display`: valores permitidos
- [x] Validación de tipos (type hints + runtime checks)

#### 2. Comandos (comandos.py) ✅

- [x] Clase base abstracta `ComandoTermostato`:
  ```python
  @dataclass(frozen=True)
  class ComandoTermostato(ABC):
      timestamp: datetime = field(default_factory=datetime.now)

      @abstractmethod
      def to_json(self) -> dict:
          pass
  ```

- [x] `ComandoPower(estado: bool)`
  - Comando de encendido/apagado
  - JSON: `{"comando": "power", "estado": "on"|"off", "timestamp": ...}`

- [x] `ComandoSetTemp(valor: float)`
  - Comando de ajuste de temperatura deseada
  - Validación: 15°C ≤ valor ≤ 35°C
  - JSON: `{"comando": "set_temp_deseada", "valor": X, "timestamp": ...}`

- [x] `ComandoSetModoDisplay(modo: str)`
  - Comando de cambio de modo display
  - Validación: modo in ["ambiente", "deseada"]
  - JSON: `{"comando": "set_modo_display", "modo": "...", "timestamp": ...}`

- [x] Método `to_json()` en cada comando
  - Serialización consistente
  - Formato esperado por RPi

- [x] Validación de comandos:
  - Rangos de valores
  - Tipos correctos
  - Campos requeridos

**Definición de Hecho:**
- [x] EstadoTermostato completo con todos los métodos
- [x] Todos los comandos implementados
- [x] Tests unitarios (100% coverage)
  - Tests de validación de rangos
  - Tests de serialización/deserialización
  - Tests de casos inválidos
- [x] Documentación de API (docstrings)
- [x] Type hints completos
- [x] Pylint ≥ 8.0 (obtuvo 10.00/10)

**Dependencias:** Ninguna (capa base)

**Implementación:**
- `app/dominio/estado_termostato.py`: 131 líneas
- `app/dominio/comandos.py`: 146 líneas
- `tests/test_estado_termostato.py`: Tests completos
- `tests/test_comandos.py`: Tests completos
- Coverage: 100%
- Pylint: 10.00/10

---

### US-021: Implementar capa de Comunicación ✅

**Puntos:** 5 | **Componente:** `app/comunicacion/`
**Coverage:** 95% | **Pylint:** 10.00/10 | **Estado:** COMPLETADA
**Branch:** development/simulador-ux-US-021 (merged)

**Como** desarrollador del sistema
**Quiero** implementar clientes y servidores TCP
**Para** comunicarme bidireccionalmente con el Raspberry Pi

**Criterios de Aceptación:**

#### 1. ServidorEstado (servidor_estado.py)

- [x] Hereda de `BaseSocketServer` (compartido/networking)
- [x] Configuración:
  - Puerto por defecto: 14001
  - IP bind: 0.0.0.0 (escucha todas las interfaces)
- [x] Manejo de conexiones:
  - Acepta una conexión del RPi
  - Recibe JSON en cada mensaje
  - Thread-safe para PyQt
- [x] Procesamiento de mensajes:
  - Parsea JSON → dict
  - Valida estructura del JSON
  - Crea `EstadoTermostato` via `from_json()`
  - Emite señal PyQt: `estado_recibido(EstadoTermostato)`
- [x] Manejo de errores:
  - JSON malformado → emite `error_parsing` signal
  - Validación fallida → emite `error_parsing` signal
  - Conexión establecida → emite `conexion_establecida`
  - Conexión perdida → emite `conexion_perdida`
- [x] Logging:
  - Log cada mensaje recibido (nivel DEBUG)
  - Log errores de parsing (nivel ERROR)
  - Log conexión establecida/perdida (nivel INFO)

**Protocolo esperado del RPi:**
```json
{
  "temperatura_actual": 22.5,
  "temperatura_deseada": 24.0,
  "modo_climatizador": "calentando",
  "falla_sensor": false,
  "bateria_baja": false,
  "encendido": true,
  "modo_display": "ambiente",
  "timestamp": "2026-01-23T10:30:00Z"
}
```

#### 2. ClienteComandos (cliente_comandos.py)

- [x] Usa `EphemeralSocketClient` (compartido/networking)
  - Patrón: conectar → enviar → cerrar
  - No mantiene conexión persistente
- [x] Configuración:
  - Puerto destino por defecto: 14000
  - IP destino: configurable (host en constructor)
  - Timeout: configurado en EphemeralSocketClient
- [x] Método `enviar_comando(cmd: ComandoTermostato) -> bool`:
  - Serializa comando → JSON via `cmd.to_json()`
  - Conecta al RPi
  - Envía JSON + newline
  - Cierra conexión
  - Retorna True si éxito, False si error
  - Fire-and-forget (no espera respuesta)
- [x] Manejo de errores:
  - Timeout de conexión → log error, retorna False
  - Error de envío → log error, retorna False
  - No lanza excepciones (las captura internamente)
- [x] Logging:
  - Log cada comando enviado (nivel INFO)
  - Log errores de conexión/envío (nivel ERROR)

**Ejemplo de uso:**
```python
cliente = ClienteComandos(ip="192.168.1.50", puerto=14000)
cmd = ComandoPower(estado=True)
exito = cliente.enviar_comando(cmd)
```

**Definición de Hecho:**
- [x] ServidorEstado funcional
  - Recibe JSON del RPi
  - Emite señales PyQt correctamente
  - Manejo robusto de errores
- [x] ClienteComandos funcional
  - Envía comandos al RPi
  - Fire-and-forget implementado
  - Logging apropiado
- [x] Tests unitarios (34 tests, 95% coverage):
  - Mock de EphemeralSocketClient para tests
  - Tests de parsing JSON (válido, malformado, campos faltantes)
  - Tests de manejo de errores (JSON, validación, conexión)
  - Tests de señales PyQt (qtbot.waitSignal)
- [x] Integración con dominio/ (usa EstadoTermostato y comandos)
- [x] Documentación en plan US-021-plan.md
- [x] Pylint 10.00/10 ✅

**Implementación:**
- `servidor_estado.py`: 207 líneas, 18 tests
- `cliente_comandos.py`: 140 líneas, 17 tests (con mocking)
- CC promedio: 1.85 (excelente)
- MI promedio: 96.00 (excelente)
- Análisis de diseño: 9.8/10 (cohesión alta, acoplamiento bajo, SOLID completo)

**Dependencias:** US-020 (necesita EstadoTermostato y comandos)

---

### US-022: Implementar Factory y Coordinator

**Prioridad:** CRÍTICA | **Puntos:** 5 | **Estado:** PENDIENTE
**Componentes:** `factory.py`, `coordinator.py`

**Como** desarrollador del sistema
**Quiero** implementar patrones Factory y Coordinator
**Para** crear componentes consistentemente y conectar señales sin acoplamiento

**Criterios de Aceptación:**

#### 1. ComponenteFactoryUX (factory.py)

- [ ] Recibe configuración en `__init__(config: ConfigManager)`
- [ ] Almacena config como atributo privado
- [ ] Lazy initialization donde sea necesario

**Métodos de creación de paneles:**
- [ ] `crear_panel_display() -> tuple[DisplayModelo, DisplayVista, DisplayControlador]`
  - Crea modelo con estado inicial
  - Crea vista con estilos consistentes
  - Crea controlador conectando modelo↔vista
  - Retorna tupla (modelo, vista, controlador)

- [ ] `crear_panel_climatizador() -> tuple[..., ..., ...]`
- [ ] `crear_panel_indicadores() -> tuple[..., ..., ...]`
- [ ] `crear_panel_power() -> tuple[..., ..., ...]`
- [ ] `crear_panel_control_temp() -> tuple[..., ..., ...]`
- [ ] `crear_panel_selector_vista() -> tuple[..., ..., ...]` (cuando US-011)
- [ ] `crear_panel_conexion() -> tuple[..., ..., ...]` (cuando US-013)

**Métodos de creación de servicios:**
- [ ] `crear_servidor_estado() -> ServidorEstado`
  - Lee puerto de config
  - Crea servidor con config apropiada
  - No inicia el servidor (lazy)

- [ ] `crear_cliente_comandos() -> ClienteComandos`
  - Lee IP y puerto de config
  - Crea cliente configurado

**Métodos de creación de UI:**
- [ ] `crear_ui_compositor(paneles: dict) -> UICompositor`
  - Recibe dict con todos los paneles creados
  - Retorna compositor configurado

**Consistencia:**
- [ ] Todos los componentes creados con misma config
- [ ] Estilos consistentes (vía ThemeProvider)
- [ ] Logging de creación de componentes

#### 2. UXCoordinator (coordinator.py)

- [ ] Recibe todos los componentes en `__init__`:
  ```python
  def __init__(
      self,
      paneles: dict,  # {"display": ctrl, "power": ctrl, ...}
      servidor_estado: ServidorEstado,
      cliente_comandos: ClienteComandos
  ):
  ```

- [ ] Método `conectar_signals()` - conecta todas las señales:

**Flujo: Power → Controles**
- [ ] `power.encendido_cambiado(bool) → control_temp.setEnabled(bool)`
- [ ] `power.encendido_cambiado(bool) → selector_vista.setEnabled(bool)` (US-011)

**Flujo: Control Temp → Cliente**
- [ ] `control_temp.comando_generado(ComandoSetTemp) → cliente_comandos.enviar_comando()`

**Flujo: Selector Vista → Display + Cliente**
- [ ] `selector_vista.modo_cambiado(str) → display.cambiar_modo(str)` (US-011)
- [ ] `selector_vista.modo_cambiado(str) → cliente_comandos.enviar_comando(ComandoSetModoDisplay)` (US-011)

**Flujo: Servidor → Paneles**
- [ ] `servidor_estado.estado_recibido(EstadoTermostato) → display.actualizar()`
- [ ] `servidor_estado.estado_recibido(EstadoTermostato) → climatizador.actualizar()`
- [ ] `servidor_estado.estado_recibido(EstadoTermostato) → indicadores.actualizar()`
- [ ] `servidor_estado.estado_recibido(EstadoTermostato) → power.sincronizar_estado()`

**Flujo: Conexión → Servidor/Cliente**
- [ ] `conexion.ip_cambiada(str) → reconectar_servicios()` (US-013)

- [ ] Sin dependencias circulares
- [ ] Desacoplamiento total entre paneles
- [ ] Logging de conexiones realizadas

**Definición de Hecho:**
- [ ] Factory crea todos los componentes existentes
- [ ] Factory crea servicios de comunicación
- [ ] Coordinator conecta todas las señales
- [ ] Tests unitarios de factory
  - Verifica que crea componentes válidos
  - Verifica uso de config
- [ ] Tests de integración de señales
  - Mock de señales PyQt
  - Verifica flujo completo de señales
- [ ] Documentación del flujo de señales (diagrama ASCII)
- [ ] Sin dependencias circulares (verificar imports)
- [ ] Pylint ≥ 8.0

**Dependencias:** US-020, US-021, paneles completados

---

### US-023: Implementar UICompositor

**Prioridad:** Alta | **Puntos:** 3 | **Estado:** PENDIENTE
**Componente:** `app/presentacion/ui_compositor.py`

**Como** desarrollador del sistema
**Quiero** ensamblar todos los paneles en un layout coherente
**Para** tener la UI completa del termostato

**Criterios de Aceptación:**

- [ ] Clase `UICompositor` recibe dict de paneles:
  ```python
  def __init__(self, paneles: dict[str, QWidget]):
      # paneles = {
      #     "display": display_vista,
      #     "climatizador": climatizador_vista,
      #     "indicadores": indicadores_vista,
      #     "power": power_vista,
      #     "control_temp": control_temp_vista,
      #     "selector_vista": selector_vista_vista,  # US-011
      #     "conexion": conexion_vista,  # US-013
      #     "estado_conexion": estado_conexion_widget  # US-015
      # }
  ```

- [ ] Método `crear_layout() -> QWidget`:
  - Retorna un QWidget con layout completo
  - Layout vertical principal (QVBoxLayout)

**Estructura del layout:**
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

**Detalles de layout:**
- [ ] Header horizontal (QHBoxLayout):
  - EstadoConexion (izquierda)
  - Stretch
  - Indicadores (derecha)
- [ ] Espaciado entre secciones: 10-15px
- [ ] Márgenes del widget principal: 15px
- [ ] Responsive:
  - Tamaño mínimo: 500x700
  - Tamaño preferido: 600x800
- [ ] Todos los widgets con tamaño apropiado
- [ ] Sin lógica de negocio (solo layout)
- [ ] Uso de `addWidget`, `addLayout`, `addStretch`

**Definición de Hecho:**
- [ ] Layout completo funcional
- [ ] Todos los paneles visibles en orden correcto
- [ ] Espaciado y márgenes consistentes
- [ ] Tamaño responsive funciona
- [ ] Tests visuales (manual)
- [ ] Sin warnings de Qt en consola
- [ ] Estética consistente con tema oscuro

**Dependencias:** Todos los paneles implementados

---

### US-024: Implementar Ventana Principal

**Prioridad:** CRÍTICA | **Puntos:** 5 | **Estado:** PENDIENTE
**Componente:** `app/presentacion/ui_principal.py`

**Como** desarrollador del sistema
**Quiero** implementar la ventana principal de la aplicación
**Para** tener un punto de entrada único que coordine todo

**Criterios de Aceptación:**

- [ ] Clase `VentanaPrincipalUX` hereda de `QMainWindow`
- [ ] Constructor recibe Factory:
  ```python
  def __init__(self, factory: ComponenteFactoryUX):
      super().__init__()
      self._factory = factory
      self._componentes = {}
      self._coordinator = None
      self._inicializar()
  ```

**Ciclo de vida completo:**

1. **`_inicializar()`** - orquesta todo el setup
   - Llama a `_configurar_ventana()`
   - Llama a `_crear_componentes()`
   - Llama a `_crear_coordinator()`
   - Llama a `_crear_ui()`

2. **`_configurar_ventana()`**
   - [ ] Título: "UX Termostato Desktop"
   - [ ] Tamaño inicial: 600x800
   - [ ] Tamaño mínimo: 500x700
   - [ ] Posición centrada en pantalla
   - [ ] Icono de ventana (si existe)
   - [ ] Aplica tema oscuro (ThemeProvider de compartido/estilos)

3. **`_crear_componentes()`**
   - [ ] Crea todos los paneles via Factory
   - [ ] Almacena en `self._componentes`:
     ```python
     self._componentes = {
         "display": (modelo, vista, ctrl),
         "climatizador": (modelo, vista, ctrl),
         # ... etc
     }
     ```
   - [ ] Crea ServidorEstado via Factory
   - [ ] Crea ClienteComandos via Factory
   - [ ] Logging de componentes creados

4. **`_crear_coordinator()`**
   - [ ] Extrae controladores de `self._componentes`
   - [ ] Crea UXCoordinator con todos los componentes
   - [ ] Llama a `coordinator.conectar_signals()`
   - [ ] Almacena en `self._coordinator`

5. **`_crear_ui()`**
   - [ ] Extrae vistas de `self._componentes`
   - [ ] Crea UICompositor con las vistas
   - [ ] Obtiene widget central via `compositor.crear_layout()`
   - [ ] Establece como central widget: `self.setCentralWidget(widget)`

6. **`iniciar()`** - método público
   - [ ] Inicia ServidorEstado (comienza a escuchar puerto 14001)
   - [ ] Muestra ventana: `self.show()`
   - [ ] Logging: "Aplicación iniciada"
   - [ ] Retorna self (para chaining)

7. **`cerrar()`** - cleanup
   - [ ] Detiene ServidorEstado
   - [ ] Cierra conexiones activas
   - [ ] Guarda config (via ConfigManager)
   - [ ] Logging: "Aplicación cerrada"
   - [ ] Llama a `super().close()`

8. **`closeEvent(event)`** - override de QMainWindow
   - [ ] Llama a `self.cerrar()`
   - [ ] Acepta el evento: `event.accept()`

**Manejo de errores:**
- [ ] Try/catch en `_crear_componentes()`
  - Si falla creación de panel → log error, continúa
- [ ] Try/catch en `iniciar()`
  - Si falla inicio de servidor → muestra diálogo error
- [ ] QMessageBox para errores críticos

**Definición de Hecho:**
- [ ] Ventana se muestra correctamente
- [ ] Todos los paneles visibles y funcionales
- [ ] Lifecycle completo implementado (iniciar → cerrar)
- [ ] Tests de integración:
  - Verifica que ventana se crea
  - Verifica que componentes se crean
  - Verifica que señales se conectan
- [ ] Manejo de cierre limpio (Ctrl+C, cerrar ventana)
- [ ] Logging apropiado en cada fase
- [ ] Tema oscuro aplicado correctamente
- [ ] Sin memory leaks (verificar destrucción de objetos)

**Dependencias:** US-022 (Factory, Coordinator), US-023 (UICompositor)

---

### US-025: Integración Final - run.py

**Prioridad:** CRÍTICA | **Puntos:** 2 | **Estado:** PENDIENTE
**Componente:** `run.py` (raíz de ux_termostato)

**Como** usuario final
**Quiero** ejecutar `python run.py`
**Para** iniciar la aplicación UX Desktop completa

**Criterios de Aceptación:**

- [ ] Clase `AplicacionUX` (similar a `AplicacionSimulador` de los simuladores)
- [ ] Método `main()`:

**1. Setup de logging**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**2. Carga de configuración**
- [ ] Crea `ConfigManager`
- [ ] Lee `config.json` (root del proyecto)
- [ ] Sobrescribe con variables de .env si existen
- [ ] Valida configuración mínima requerida
- [ ] Si falla: usa valores por defecto + log warning

**3. Creación de QApplication**
- [ ] Verifica si ya existe: `QApplication.instance()`
- [ ] Si no existe: `app = QApplication(sys.argv)`
- [ ] Configura nombre de aplicación: `app.setApplicationName("UX Termostato")`
- [ ] Configura organización: `app.setOrganizationName("ISSE")`

**4. Creación de componentes**
- [ ] Crea `ComponenteFactoryUX(config)`
- [ ] Crea `VentanaPrincipalUX(factory)`
- [ ] Llama a `ventana.iniciar()`

**5. Ejecución**
- [ ] Ejecuta event loop: `sys.exit(app.exec())`

**Manejo de excepciones:**
- [ ] Try/catch global:
  ```python
  try:
      main()
  except KeyboardInterrupt:
      logger.info("Aplicación interrumpida por usuario")
      sys.exit(0)
  except Exception as e:
      logger.error(f"Error fatal: {e}", exc_info=True)
      sys.exit(1)
  ```

**Exit codes:**
- [ ] 0: éxito
- [ ] 1: error fatal
- [ ] 130: interrupción por usuario (Ctrl+C)

**Logging:**
- [ ] Log de inicio: versión, PID, config cargada
- [ ] Log de componentes creados
- [ ] Log de ventana mostrada
- [ ] Log de evento loop iniciado
- [ ] Log de cierre

**Ejemplo de output esperado:**
```
2026-01-23 10:30:00 - __main__ - INFO - Iniciando UX Termostato Desktop v1.0
2026-01-23 10:30:00 - __main__ - INFO - Config cargada: IP=192.168.1.50, Puerto=14001
2026-01-23 10:30:00 - __main__ - INFO - Componentes creados correctamente
2026-01-23 10:30:00 - __main__ - INFO - Ventana principal mostrada
2026-01-23 10:30:00 - __main__ - INFO - Event loop iniciado
```

**Definición de Hecho:**
- [ ] `python run.py` inicia la aplicación
- [ ] Ventana se muestra correctamente
- [ ] Todos los paneles operativos
- [ ] Conexión al RPi funciona (si RPi está disponible)
- [ ] Cierre limpio con Ctrl+C
- [ ] Cierre limpio con botón cerrar ventana
- [ ] Exit codes apropiados
- [ ] Logging completo y útil
- [ ] Manejo robusto de errores
- [ ] Tests de inicio/cierre

**Dependencias:** US-024 (VentanaPrincipalUX), US-022 (Factory)

**Total Arquitectura:** 6 historias - 28 puntos

---

# 📊 RESUMEN Y PLANIFICACIÓN

## Estado Actual del Proyecto

```
┌─────────────────────────────────────────────────┐
│  PROYECTO: UX TERMOSTATO DESKTOP                │
│  Branch: main (US-020, US-021 merged)           │
│  Fecha: 2026-01-23                              │
└─────────────────────────────────────────────────┘

COMPLETADAS:           9 historias - 35 puntos (57% del proyecto)
DESESTIMADAS:         10 historias - 28 puntos (reducción de alcance)
PANELES PENDIENTES:    3 historias -  8 puntos (31% del pendiente)
ARQUITECTURA NUEVA:    4 historias - 18 puntos (69% del pendiente)
────────────────────────────────────────────────────────────────
TOTAL PROYECTO:       16 historias - 61 puntos
TRABAJO RESTANTE:      7 historias - 26 puntos (43%)
```

## Distribución por Épica

| Épica | Historias | Puntos | Completado | Pendiente |
|-------|-----------|--------|------------|-----------|
| Épica 1: Visualización | 3 | 10 | 100% | 0% |
| Épica 2: Control Temp | 2 | 6 | 100% | 0% |
| Épica 3: Power | 2 | 5 | 100% | 0% |
| Épica 4: Alertas | 1 | 2 | 100% | 0% (US-009/010 desestimadas) |
| Épica 5: Modos Vista | 1 | 3 | 0% | 100% (US-011) |
| Épica 6: Configuración | 2 | 5 | 0% | 100% (US-013, US-015) |
| **Épica 8: Arquitectura** | **6** | **28** | **36%** | **64%** (US-022 a US-025) |

---

## Plan de Implementación Propuesto

### Sprint 1: Arquitectura Base ✅ COMPLETADO

**Historias:**
- ✅ US-020: Capa Dominio (5 pts) - **COMPLETADA**
  - EstadoTermostato implementado
  - Comandos implementados (ComandoPower, ComandoSetTemp, ComandoSetModoDisplay)
  - Validaciones completas
  - Coverage: 100%, Pylint: 10.00/10

- ✅ US-021: Capa Comunicación (5 pts) - **COMPLETADA**
  - ServidorEstado (recibe JSON del RPi, puerto 14001)
  - ClienteComandos (envía comandos al RPi, puerto 14000)
  - Comunicación bidireccional TCP
  - Coverage: 95%, Pylint: 10.00/10, CC: 1.85, MI: 96.00
  - Análisis de diseño: 9.8/10

**Entregable:** ✅ Dominio + Comunicación funcionales con tests completos

**Próximo Sprint:** Sprint 2 - Arquitectura e Integración

---

### Sprint 2: Arquitectura e Integración (13 puntos - 1.5 semanas)
**Objetivo:** Factory + Coordinator + Compositor + Ventana Principal

**Historias:**
- US-022: Factory + Coordinator (5 pts) - **PRIMERO**
  - ComponenteFactoryUX
  - UXCoordinator
  - Conexión de señales entre dominio, comunicación y presentación

- US-023: UICompositor (3 pts) - **SEGUNDO**
  - Layout assembly
  - Integración visual de paneles existentes

- US-024: VentanaPrincipal (5 pts) - **TERCERO**
  - Solo con paneles existentes (sin US-011, US-013, US-015)
  - Lifecycle básico (iniciar/detener servidor)
  - Menú de aplicación

**Entregable:** Arquitectura completa con comunicación bidireccional

**Criterio de éxito:**
- ✅ ServidorEstado recibe JSON del RPi (ya completado)
- ✅ ClienteComandos envía comandos al RPi (ya completado)
- Factory crea todos los componentes
- Coordinator conecta señales
- `python run.py` inicia con interfaz funcional

---

### Sprint 3: Paneles Finales + Integración Total (10 puntos - 1 semana)
**Objetivo:** Completar paneles pendientes y finalizar

**Historias:**
- US-011: Selector Vista (3 pts) - **QUINTO**
- US-013: Config IP (3 pts) - **SEXTO**
- US-015: Estado Conexión (2 pts) - **SÉPTIMO**
- US-025: run.py (2 pts) - **OCTAVO (FINAL)**

**Entregable:** ✅ UX Desktop 100% funcional

**Criterio de éxito:**
- Todos los paneles implementados
- Conexión real con Raspberry Pi funciona
- Tests de integración end-to-end pasan
- Coverage ≥ 95%
- Pylint ≥ 8.0 en todo el proyecto

---

## Dependencias Críticas

### Cadena de Dependencias

```
✅ US-020 (Dominio) - COMPLETADA
    ↓
✅ US-021 (Comunicación) - COMPLETADA
    ↓
US-022 (Factory + Coordinator) ← SIGUIENTE
    ↓
US-023 (UICompositor)
    ↓
US-024 (VentanaPrincipal)
    ↓
┌───────────────────┬──────────────────────┐
│                   │                      │
US-011            US-013              US-015
(Selector Vista)  (Config IP)     (Estado Conexión)
│                   │                      │
└───────────────────┴──────────────────────┘
                    ↓
            US-025 (run.py - FINAL)
```

### Notas sobre Dependencias

- ✅ **US-020 completada** - Capa de dominio (EstadoTermostato y Comandos)
- ✅ **US-021 completada** - Capa de comunicación (ServidorEstado y ClienteComandos)
- **US-022 es siguiente** - Factory + Coordinator (conecta dominio, comunicación y presentación)
- **US-022 a US-024 secuenciales** (arquitectura)
- **US-011, US-013, US-015 pueden hacerse en paralelo** después de US-024
- **US-025 es la última** - integración final (run.py)

---

## Métricas de Calidad

Objetivo para cada historia:

| Métrica | Objetivo | Crítico |
|---------|----------|---------|
| **Coverage** | ≥ 95% | ✅ Obligatorio |
| **Pylint** | ≥ 8.0 | ✅ Obligatorio |
| **CC (Complejidad)** | ≤ 10 promedio | ⚠️ Recomendado |
| **MI (Mantenibilidad)** | > 20 | ⚠️ Recomendado |

---

## Testing por Tipo

| Tipo de Test | Responsable | Cobertura Esperada |
|--------------|-------------|--------------------|
| **Tests Unitarios** | Por componente MVC | Modelo: 100%, Vista: 90%, Ctrl: 95% |
| **Tests de Integración** | Por historia | Flujo completo de señales |
| **Tests de Comunicación** | US-021 | Protocolo TCP (con mocks) |
| **Tests End-to-End** | US-025 | Aplicación completa |

---

## Criterios de Aceptación del Proyecto

El proyecto se considerará completo cuando:

- [ ] ✅ Todas las 16 historias implementadas
- [ ] ✅ Coverage global ≥ 95%
- [ ] ✅ Pylint global ≥ 8.0
- [ ] ✅ `python run.py` inicia aplicación sin errores
- [ ] ✅ Conexión real con Raspberry Pi funciona
- [ ] ✅ Todos los paneles operativos
- [ ] ✅ Señales PyQt fluyen correctamente
- [ ] ✅ Manejo robusto de errores
- [ ] ✅ Documentación completa (README, docstrings)
- [ ] ✅ Arquitectura alineada con simuladores de referencia

---

**Versión:** 2.2
**Fecha:** 2026-01-23
**Estado:** Sprint 1 Completado - US-020, US-021 merged a main
**Total de Historias Activas:** 16 (9 completadas, 7 pendientes)
**Puntos Totales:** 61 (26 puntos restantes - ~8 días de desarrollo)
**Próxima US:** US-022 - Factory + Coordinator
