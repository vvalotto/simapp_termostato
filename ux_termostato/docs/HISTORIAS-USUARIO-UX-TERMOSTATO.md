# Historias de Usuario - UX Termostato Desktop

## Información del Documento

**Proyecto:** ISSE_Simuladores - UX Termostato Desktop
**Fecha:** 2026-01-16
**Autor:** Victor Valotto
**Objetivo:** Definir historias de usuario para la implementación del simulador UX del termostato

---

## Tabla de Contenidos

1. [Épica 1: Visualización de Estado](#épica-1-visualización-de-estado)
2. [Épica 2: Control de Temperatura](#épica-2-control-de-temperatura)
3. [Épica 3: Encendido y Apagado](#épica-3-encendido-y-apagado)
4. [Épica 4: Alertas y Notificaciones](#épica-4-alertas-y-notificaciones)
5. [Épica 5: Modos de Visualización](#épica-5-modos-de-visualización)
6. [Épica 6: Configuración y Conectividad](#épica-6-configuración-y-conectividad)
7. [Épica 7: Monitoreo del Sistema](#épica-7-monitoreo-del-sistema)

---

## Convenciones

**Formato de Historia:**
```
US-XXX: Título descriptivo
Prioridad: Alta | Media | Baja
Puntos: 1, 2, 3, 5, 8, 13
```

**Prioridades:**
- **Alta (Must Have):** Funcionalidad crítica para MVP
- **Media (Should Have):** Funcionalidad importante pero no bloqueante
- **Baja (Nice to Have):** Mejoras deseables

**Estimación (Puntos de Historia):**
- 1 punto: < 2 horas
- 2 puntos: 2-4 horas
- 3 puntos: 4-8 horas
- 5 puntos: 1-2 días
- 8 puntos: 2-3 días
- 13 puntos: > 3 días (considerar dividir)

---

# Épica 1: Visualización de Estado

## US-001: Ver temperatura ambiente actual

**Prioridad:** Alta
**Puntos:** 3

**Como** usuario del termostato
**Quiero** ver la temperatura ambiente actual en un display grande y claro
**Para** conocer en todo momento las condiciones de mi hogar

### Criterios de Aceptación

- [ ] El display muestra la temperatura actual con formato X.X °C
- [ ] La temperatura se actualiza automáticamente cuando llega nueva información del sistema
- [ ] El display usa fuente grande y clara (mínimo 48px)
- [ ] El fondo del display simula un LCD verde oscuro
- [ ] El label superior indica "Temperatura Ambiente"
- [ ] Cuando no hay conexión, el display muestra "---"

### Notas Técnicas

- Componente: Panel Display (MVC)
- Recibe datos de: ServidorEstado (puerto 14001)
- Actualización: En tiempo real al recibir JSON del RPi

### Definición de Hecho

- [ ] Tests unitarios del panel Display pasan
- [ ] UI muestra temperatura correctamente
- [ ] Manejo de errores implementado
- [ ] Documentación actualizada

---

## US-002: Ver estado del climatizador

**Prioridad:** Alta
**Puntos:** 5

**Como** usuario del termostato
**Quiero** ver el estado actual del climatizador (calentando, enfriando, reposo)
**Para** saber si el sistema está actuando para alcanzar la temperatura deseada

### Criterios de Aceptación

- [ ] El panel muestra 3 indicadores visuales: Calor (🔥), Reposo (🌬️), Frío (❄️)
- [ ] Solo un indicador está activo a la vez
- [ ] El indicador activo se destaca con:
  - Borde de color (naranja para calor, verde para reposo, azul para frío)
  - Animación pulsante (calor y frío)
  - Icono en color brillante
- [ ] Los indicadores inactivos aparecen en gris apagado
- [ ] El estado se actualiza en tiempo real

### Criterios de Diseño

- [ ] Calefacción: Fondo naranja/20%, borde naranja-500, animación pulse
- [ ] Reposo: Fondo verde/20%, borde verde-500, sin animación
- [ ] Refrigeración: Fondo azul/20%, borde azul-500, animación pulse
- [ ] Inactivo: Fondo slate-700/30%, borde slate-700

### Definición de Hecho

- [ ] Panel Climatizador implementado (MVC)
- [ ] Tests con los 4 estados (calentando, enfriando, reposo, apagado)
- [ ] Animaciones CSS funcionando
- [ ] Actualización desde JSON del RPi

---

## US-003: Ver indicadores de alerta

**Prioridad:** Alta
**Puntos:** 2

**Como** usuario del termostato
**Quiero** ver indicadores LED que me alerten sobre fallas del sensor o batería baja
**Para** tomar acción cuando haya problemas con el sistema

### Criterios de Aceptación

- [ ] LED izquierdo indica estado del sensor:
  - Gris apagado: sensor normal
  - Rojo pulsante: falla del sensor
- [ ] LED derecho indica estado de batería:
  - Gris apagado: batería normal
  - Amarillo pulsante: batería baja (<30%)
- [ ] Los LEDs están en la parte superior de la UI
- [ ] Los LEDs tienen labels: "Sensor" y "Batería"
- [ ] La animación pulsante atrae la atención

### Notas de Implementación

- Usar componente `LedIndicator` de `compartido/widgets`
- Estados: "inactivo", "error", "warning"
- Actualización desde campo `falla_sensor` y `bateria_baja` del JSON

### Definición de Hecho

- [ ] Panel Indicadores implementado
- [ ] LEDs responden a cambios de estado
- [ ] Animación pulsante funciona
- [ ] Tests de los 4 estados posibles

---

# Épica 2: Control de Temperatura

## US-004: Aumentar temperatura deseada

**Prioridad:** Alta
**Puntos:** 3

**Como** usuario del termostato
**Quiero** poder aumentar la temperatura deseada presionando un botón
**Para** ajustar la climatización de mi hogar según mis necesidades

### Criterios de Aceptación

- [ ] Botón "SUBIR" con icono de flecha arriba (▲)
- [ ] Botón de color rojo (bg-red-600) para indicar calor
- [ ] Al presionar, la temperatura deseada aumenta en 0.5°C
- [ ] El rango máximo es 35°C
- [ ] Al alcanzar el máximo, el botón se deshabilita
- [ ] El botón solo está activo cuando el termostato está encendido
- [ ] Feedback visual al presionar (scale-95)
- [ ] El comando se envía inmediatamente al RPi

### Comportamiento del Sistema

- [ ] Envía comando JSON: `{"comando": "set_temp_deseada", "valor": X, "timestamp": T}`
- [ ] Puerto de envío: 14000
- [ ] No espera confirmación (fire and forget)
- [ ] Log de comando enviado

### Definición de Hecho

- [ ] Panel Control Temp implementado
- [ ] Botón responde al click
- [ ] Validación de rango funciona
- [ ] Comando enviado correctamente al RPi
- [ ] Tests unitarios pasan

---

## US-005: Disminuir temperatura deseada

**Prioridad:** Alta
**Puntos:** 3

**Como** usuario del termostato
**Quiero** poder disminuir la temperatura deseada presionando un botón
**Para** reducir la climatización cuando hace demasiado calor o frío

### Criterios de Aceptación

- [ ] Botón "BAJAR" con icono de flecha abajo (▼)
- [ ] Botón de color azul (bg-blue-600) para indicar enfriamiento
- [ ] Al presionar, la temperatura deseada disminuye en 0.5°C
- [ ] El rango mínimo es 15°C
- [ ] Al alcanzar el mínimo, el botón se deshabilita
- [ ] El botón solo está activo cuando el termostato está encendido
- [ ] Feedback visual al presionar (scale-95)
- [ ] El comando se envía inmediatamente al RPi

### Layout

- [ ] Botones SUBIR y BAJAR están uno al lado del otro
- [ ] Mismo tamaño y altura
- [ ] Espaciado consistente

### Definición de Hecho

- [ ] Botón funcional
- [ ] Validación de rango
- [ ] Comando JSON enviado
- [ ] Tests con casos límite (mínimo, máximo)

---

## US-006: Ver diferencia entre temperatura actual y deseada

**Prioridad:** Media
**Puntos:** 2

**Como** usuario del termostato
**Quiero** ver la diferencia entre la temperatura actual y la deseada
**Para** saber qué tan lejos estoy del objetivo

### Criterios de Aceptación

- [ ] El panel footer muestra: "Estado: Calentando" cuando temp_actual < temp_deseada
- [ ] Muestra: "Estado: Enfriando" cuando temp_actual > temp_deseada
- [ ] Muestra: "Estado: Estable" cuando la diferencia es < 0.3°C
- [ ] El texto usa color apropiado:
  - Naranja para "Calentando"
  - Azul para "Enfriando"
  - Verde para "Estable"

### Cálculo

```python
diff = temp_deseada - temp_actual
if abs(diff) < 0.3:
    estado = "Estable"
elif diff > 0:
    estado = "Calentando"
else:
    estado = "Enfriando"
```

### Definición de Hecho

- [ ] Panel Estado Footer implementado
- [ ] Cálculo correcto de diferencia
- [ ] Colores apropiados
- [ ] Actualización en tiempo real

---

# Épica 3: Encendido y Apagado

## US-007: Encender el termostato

**Prioridad:** Alta
**Puntos:** 3

**Como** usuario del termostato
**Quiero** poder encender el sistema con un botón
**Para** activar la climatización cuando lo necesite

### Criterios de Aceptación

- [ ] Botón "ENCENDER" con icono de power (⚡)
- [ ] Color verde (bg-green-600) cuando está apagado
- [ ] Al presionar, el termostato se enciende
- [ ] El display muestra la temperatura actual
- [ ] Los botones de control se habilitan
- [ ] El botón cambia a "APAGAR" y color diferente
- [ ] Envía comando al RPi: `{"comando": "power", "estado": "on"}`

### Cambios en la UI al Encender

- [ ] Display muestra temperatura (no "---")
- [ ] Botones SUBIR/BAJAR se habilitan
- [ ] Botón selector de vista se habilita
- [ ] Estado del climatizador comienza a actualizarse

### Definición de Hecho

- [ ] Panel Power implementado
- [ ] Toggle funciona correctamente
- [ ] Comando enviado al RPi
- [ ] UI actualiza todos los paneles
- [ ] Tests de encendido/apagado

---

## US-008: Apagar el termostato

**Prioridad:** Alta
**Puntos:** 2

**Como** usuario del termostato
**Quiero** poder apagar el sistema con un botón
**Para** detener la climatización cuando no la necesite

### Criterios de Aceptación

- [ ] Botón "APAGAR" con icono de power (⚡)
- [ ] Color gris (bg-slate-700) cuando está encendido
- [ ] Al presionar, el termostato se apaga
- [ ] El display muestra "---"
- [ ] Los botones de control se deshabilitan
- [ ] El botón cambia a "ENCENDER" y color verde
- [ ] Envía comando al RPi: `{"comando": "power", "estado": "off"}`

### Cambios en la UI al Apagar

- [ ] Display muestra "---" y label "APAGADO"
- [ ] Botones SUBIR/BAJAR se deshabilitan (apariencia gris)
- [ ] Botón selector de vista se deshabilita
- [ ] Estado del climatizador muestra "apagado" (todo gris)

### Definición de Hecho

- [ ] Apagado funciona correctamente
- [ ] UI refleja estado apagado
- [ ] Comando enviado al RPi
- [ ] Tests de transición on→off

---

# Épica 4: Alertas y Notificaciones

## US-009: Recibir alerta de falla del sensor

**Prioridad:** Alta
**Puntos:** 2

**Como** usuario del termostato
**Quiero** ser notificado visualmente cuando hay una falla del sensor de temperatura
**Para** saber que los datos mostrados pueden no ser confiables

### Criterios de Aceptación

- [ ] LED "Sensor" se enciende en rojo con animación pulsante
- [ ] El display principal muestra "ERROR" en lugar de temperatura
- [ ] Se muestra icono de alerta (⚠️) junto a "ERROR"
- [ ] El texto "ERROR" es de color rojo brillante
- [ ] El estado persiste hasta que el sensor se recupere
- [ ] La climatización se detiene automáticamente (si el RPi lo decide)

### Activación

- [ ] Se activa cuando `falla_sensor: true` en JSON del RPi
- [ ] Se desactiva cuando `falla_sensor: false`

### Definición de Hecho

- [ ] LED rojo funcionando
- [ ] Display muestra ERROR
- [ ] Respuesta a cambio de estado del JSON
- [ ] Tests de falla simulada

---

## US-010: Recibir alerta de batería baja

**Prioridad:** Media
**Puntos:** 2

**Como** usuario del termostato
**Quiero** ser alertado cuando la batería del sistema está baja
**Para** poder recargarla antes de que el sistema se apague

### Criterios de Aceptación

- [ ] LED "Batería" se enciende en amarillo con animación pulsante
- [ ] Se activa cuando `bateria_baja: true` en JSON del RPi
- [ ] El nivel de batería se muestra en el footer: "Batería: XX%"
- [ ] Color del texto cambia a amarillo cuando < 30%
- [ ] Color cambia a rojo cuando < 15%
- [ ] El sistema continúa operando normalmente

### Visual

- [ ] LED amarillo pulsante
- [ ] Footer muestra porcentaje
- [ ] Iconos de batería (■■■□□) si es posible

### Definición de Hecho

- [ ] LED amarillo funcional
- [ ] Footer muestra nivel de batería
- [ ] Colores según nivel
- [ ] Tests con diferentes niveles

---

# Épica 5: Modos de Visualización

## US-011: Cambiar entre vista de temperatura ambiente y deseada

**Prioridad:** Alta
**Puntos:** 3

**Como** usuario del termostato
**Quiero** poder alternar entre ver la temperatura ambiente actual y la temperatura deseada
**Para** comparar ambos valores fácilmente

### Criterios de Aceptación

- [ ] Botón "Ver Temperatura Deseada" cuando está en modo ambiente
- [ ] Botón "Ver Temperatura Ambiente" cuando está en modo deseada
- [ ] Al presionar, el display cambia a mostrar el otro valor
- [ ] El label del display cambia:
  - "Temperatura Ambiente" en modo ambiente
  - "Temperatura Deseada" en modo deseada
- [ ] El cambio es instantáneo (sin delay)
- [ ] El botón solo está activo cuando el termostato está encendido

### Comportamiento del Comando

- [ ] Envía comando al RPi: `{"comando": "set_modo_display", "modo": "ambiente|deseada"}`
- [ ] Puerto: 14000
- [ ] El cambio es local primero (optimistic update)

### Definición de Hecho

- [ ] Panel Selector Vista implementado
- [ ] Toggle entre modos funciona
- [ ] Display actualiza correctamente
- [ ] Comando enviado al RPi
- [ ] Tests de ambos modos

---

## US-012: Ver modo actual en el footer

**Prioridad:** Baja
**Puntos:** 1

**Como** usuario del termostato
**Quiero** ver en el footer si el sistema está activo o inactivo
**Para** tener confirmación rápida del estado general

### Criterios de Aceptación

- [ ] Footer muestra: "Modo: Activo" cuando está encendido
- [ ] Footer muestra: "Modo: Inactivo" cuando está apagado
- [ ] Texto en tamaño pequeño (xs)
- [ ] Color gris claro cuando activo
- [ ] Color gris oscuro cuando inactivo

### Definición de Hecho

- [ ] Footer actualiza según estado power
- [ ] Tests de visualización

---

# Épica 6: Configuración y Conectividad

## US-013: Configurar dirección IP del Raspberry Pi

**Prioridad:** Alta
**Puntos:** 3

**Como** usuario del termostato
**Quiero** poder configurar la dirección IP del Raspberry Pi
**Para** conectarme al sistema embebido en mi red local

### Criterios de Aceptación

- [ ] Panel de configuración con campo de texto para IP
- [ ] Validación de formato IP (xxx.xxx.xxx.xxx)
- [ ] Feedback visual si la IP es inválida (borde rojo)
- [ ] Botón "Aplicar" para guardar la configuración
- [ ] La IP se guarda en config.json
- [ ] La IP se carga al iniciar la aplicación
- [ ] Al cambiar la IP, el cliente se reconecta

### Validación

```python
# IP válida: 192.168.1.50
# IP inválida: 999.999.999.999
# IP inválida: abc.def.ghi.jkl
```

### Definición de Hecho

- [ ] Panel Conexión implementado
- [ ] Validación de IP funciona
- [ ] Configuración se persiste
- [ ] Reconexión automática
- [ ] Tests de validación

---

## US-014: Configurar puertos de comunicación

**Prioridad:** Media
**Puntos:** 2

**Como** usuario avanzado del termostato
**Quiero** poder configurar los puertos de recepción y envío
**Para** adaptar la aplicación a diferentes configuraciones de red

### Criterios de Aceptación

- [ ] Campos para puerto de recepción (default: 14001)
- [ ] Campo para puerto de envío (default: 14000)
- [ ] Validación: puerto entre 1024 y 65535
- [ ] Los puertos se guardan en config.json
- [ ] Al cambiar puertos, la aplicación se reconecta
- [ ] Botón "Restaurar valores por defecto"

### Validación

- [ ] Puerto válido: 1024-65535
- [ ] Puerto inválido: < 1024 o > 65535

### Definición de Hecho

- [ ] Campos de puerto funcionales
- [ ] Validación implementada
- [ ] Configuración persistente
- [ ] Tests de validación

---

## US-015: Ver estado de conexión con el Raspberry Pi

**Prioridad:** Alta
**Puntos:** 2

**Como** usuario del termostato
**Quiero** ver si hay conexión activa con el Raspberry Pi
**Para** saber si los datos mostrados son actuales

### Criterios de Aceptación

- [ ] Indicador visual en la parte superior: "Estado: ● Conectado"
- [ ] LED verde cuando hay conexión
- [ ] LED rojo cuando no hay conexión
- [ ] Texto cambia a "Desconectado" cuando no hay conexión
- [ ] El estado se actualiza en tiempo real
- [ ] Timeout de conexión: 10 segundos sin datos = desconectado

### Estados

- [ ] Conectado: LED verde, texto "Conectado"
- [ ] Desconectado: LED rojo, texto "Desconectado"
- [ ] Conectando: LED amarillo pulsante, texto "Conectando..."

### Definición de Hecho

- [ ] Indicador de conexión funcional
- [ ] Detección de desconexión
- [ ] Tests de estados de conexión

---

## US-016: Reconectar manualmente al Raspberry Pi

**Prioridad:** Media
**Puntos:** 2

**Como** usuario del termostato
**Quiero** poder forzar una reconexión al Raspberry Pi
**Para** restablecer la comunicación después de un problema de red

### Criterios de Aceptación

- [ ] Botón "Reconectar" en el panel de configuración
- [ ] Al presionar, cierra conexiones existentes
- [ ] Intenta establecer nueva conexión
- [ ] Muestra feedback visual durante reconexión
- [ ] Timeout de 5 segundos
- [ ] Mensaje de éxito o error después del intento

### Feedback

- [ ] Durante reconexión: spinner o texto "Reconectando..."
- [ ] Éxito: "Conectado exitosamente"
- [ ] Error: "No se pudo conectar. Verifique la IP y que el RPi esté encendido"

### Definición de Hecho

- [ ] Botón reconectar funcional
- [ ] Lógica de reconexión implementada
- [ ] Feedback apropiado
- [ ] Tests de reconexión

---

# Épica 7: Monitoreo del Sistema

## US-017: Ver información de estado en tiempo real

**Prioridad:** Media
**Puntos:** 3

**Como** usuario del termostato
**Quiero** ver información detallada del estado del sistema
**Para** monitorear su funcionamiento

### Criterios de Aceptación

- [ ] Panel footer muestra:
  - Modo: Activo/Inactivo
  - Estado: Calentando/Enfriando/Estable
  - (Opcional) Tiempo en estado actual
- [ ] La información se actualiza en tiempo real
- [ ] Formato de tiempo: "Tiempo: 2m 30s"
- [ ] Texto en tamaño pequeño (xs)
- [ ] Color gris claro (slate-500)

### Datos del JSON

```json
{
  "tiempo_en_estado": 150  // segundos
}
```

### Definición de Hecho

- [ ] Panel footer con toda la info
- [ ] Actualización en tiempo real
- [ ] Formato de tiempo legible
- [ ] Tests de actualización

---

## US-018: Persistir configuración entre sesiones

**Prioridad:** Media
**Puntos:** 2

**Como** usuario del termostato
**Quiero** que mis configuraciones (IP, puertos) se guarden
**Para** no tener que reconfigurar cada vez que abro la aplicación

### Criterios de Aceptación

- [ ] Al cerrar la aplicación, se guarda config.json
- [ ] Al abrir la aplicación, se carga config.json
- [ ] Si no existe config.json, se usan valores por defecto
- [ ] Configuración incluye:
  - IP del Raspberry Pi
  - Puerto de recepción
  - Puerto de envío
  - (Opcional) Última temperatura deseada

### Ubicación del archivo

- [ ] Linux/Mac: `~/.config/ux_termostato/config.json`
- [ ] Windows: `%APPDATA%\ux_termostato\config.json`

### Definición de Hecho

- [ ] ConfigManager implementado
- [ ] Carga y guardado funciona
- [ ] Valores por defecto correctos
- [ ] Tests de persistencia

---

## US-019: Ver historial de temperatura (Opcional - Fase 2)

**Prioridad:** Baja
**Puntos:** 8

**Como** usuario del termostato
**Quiero** ver un gráfico del historial de temperatura de las últimas horas
**Para** analizar tendencias y comportamiento del sistema

### Criterios de Aceptación

- [ ] Gráfico de línea con pyqtgraph
- [ ] Eje X: tiempo (últimos 10 minutos)
- [ ] Eje Y: temperatura (°C)
- [ ] Dos líneas:
  - Azul: temperatura ambiente
  - Roja: temperatura deseada
- [ ] El gráfico se actualiza en tiempo real
- [ ] Máximo 600 puntos de datos (para performance)

### Ubicación

- [ ] Panel nuevo debajo del display principal
- [ ] Colapsable (botón para mostrar/ocultar)

### Definición de Hecho

- [ ] Panel Gráfico implementado
- [ ] pyqtgraph configurado
- [ ] Datos históricos almacenados
- [ ] Actualización en tiempo real
- [ ] Tests de gráfico

**Nota:** Esta historia es opcional y puede implementarse en una fase posterior.

---

# Resumen de Prioridades

## Alta Prioridad (Must Have - MVP)

Total: 11 historias, 35 puntos (~7 días de desarrollo)

1. US-001: Ver temperatura ambiente (3 pts)
2. US-002: Ver estado climatizador (5 pts)
3. US-003: Ver indicadores de alerta (2 pts)
4. US-004: Aumentar temperatura (3 pts)
5. US-005: Disminuir temperatura (3 pts)
6. US-007: Encender termostato (3 pts)
7. US-008: Apagar termostato (2 pts)
8. US-009: Alerta falla sensor (2 pts)
9. US-011: Cambiar vista ambiente/deseada (3 pts)
10. US-013: Configurar IP (3 pts)
11. US-015: Ver estado conexión (2 pts)

## Media Prioridad (Should Have)

Total: 7 historias, 18 puntos (~3.5 días)

1. US-006: Ver diferencia temperatura (2 pts)
2. US-010: Alerta batería baja (2 pts)
3. US-014: Configurar puertos (2 pts)
4. US-016: Reconectar manualmente (2 pts)
5. US-017: Info estado en tiempo real (3 pts)
6. US-018: Persistir configuración (2 pts)

## Baja Prioridad (Nice to Have)

Total: 2 historias, 9 puntos (~2 días)

1. US-012: Ver modo en footer (1 pt)
2. US-019: Historial de temperatura (8 pts) - **Fase 2**

---

# Plan de Sprints

## Sprint 1: MVP Básico (35 puntos - 2 semanas)

**Objetivo:** Visualización básica y control esencial

### Semana 1
- US-001: Ver temperatura ambiente (3 pts)
- US-002: Ver estado climatizador (5 pts)
- US-003: Ver indicadores alerta (2 pts)
- US-007: Encender termostato (3 pts)
- US-008: Apagar termostato (2 pts)
- **Total:** 15 puntos

### Semana 2
- US-004: Aumentar temperatura (3 pts)
- US-005: Disminuir temperatura (3 pts)
- US-009: Alerta falla sensor (2 pts)
- US-011: Cambiar vista (3 pts)
- US-013: Configurar IP (3 pts)
- US-015: Estado conexión (2 pts)
- **Total:** 16 puntos

**Entregable Sprint 1:** UX Desktop funcional con todas las funciones críticas

---

## Sprint 2: Mejoras y Refinamiento (18 puntos - 1 semana)

**Objetivo:** Funcionalidades adicionales y polish

- US-006: Diferencia temperatura (2 pts)
- US-010: Alerta batería (2 pts)
- US-014: Configurar puertos (2 pts)
- US-016: Reconectar manual (2 pts)
- US-017: Info estado tiempo real (3 pts)
- US-018: Persistir config (2 pts)
- US-012: Modo en footer (1 pt)
- **Total:** 14 puntos

**Entregable Sprint 2:** UX Desktop completo y pulido

---

## Sprint 3 (Opcional - Fase 2): Gráfico Histórico (8 puntos - 1 semana)

- US-019: Historial temperatura (8 pts)

**Entregable Sprint 3:** UX Desktop con análisis de tendencias

---

# Formato para Jira

## Template de Historia

```
Título: [US-XXX] Título descriptivo

Tipo: Story
Prioridad: Alta/Media/Baja
Puntos: X
Sprint: Sprint X
Épica: [Nombre de la épica]

Descripción:
Como [rol]
Quiero [funcionalidad]
Para [beneficio]

Criterios de Aceptación:
[ ] Criterio 1
[ ] Criterio 2
...

Notas Técnicas:
- Componente: [Nombre del componente]
- Dependencias: [US-XXX, US-YYY]

Definición de Hecho:
[ ] Tests unitarios pasan
[ ] Código revisado
[ ] Documentación actualizada
[ ] Demo funcional
```

---

# Dependencias entre Historias

## Cadena Crítica (MVP)

```
US-013 (Configurar IP)
    ↓
US-015 (Estado conexión)
    ↓
US-001 (Ver temperatura)
    ↓
US-002 (Estado climatizador)
    ↓
US-003 (Indicadores)
    ↓
US-007/US-008 (Power)
    ↓
US-004/US-005 (Control temp)
    ↓
US-011 (Cambiar vista)
```

## Historias Independientes

Pueden desarrollarse en paralelo:
- US-009 (Alerta sensor)
- US-010 (Alerta batería)
- US-012 (Modo footer)
- US-014 (Config puertos)

---

# Validación y Testing

## Tests de Aceptación por Historia

Cada historia debe incluir:

1. **Tests Unitarios**
   - Modelo: validación de datos
   - Vista: renderizado correcto
   - Controlador: lógica de negocio

2. **Tests de Integración**
   - Comunicación servidor/cliente
   - Señales entre componentes
   - Actualización de UI

3. **Tests Manuales**
   - Checklist de criterios de aceptación
   - Prueba con Raspberry Pi real
   - Casos extremos (sin conexión, fallas, etc.)

## Coverage Objetivo

- Código: ≥ 95%
- Pylint: ≥ 8.0
- CC: ≤ 10 promedio
- MI: > 20

---

# Glosario

**RPi:** Raspberry Pi
**MVP:** Minimum Viable Product
**MVC:** Model-View-Controller
**LCD:** Liquid Crystal Display (simulado)
**LED:** Light Emitting Diode (simulado)
**TCP:** Transmission Control Protocol
**JSON:** JavaScript Object Notation

---

**Versión:** 1.0
**Fecha:** 2026-01-16
**Estado:** Listo para importar a Jira
**Total de Historias:** 19 (11 Alta, 7 Media, 1 Baja)
**Puntos Totales:** 62 (~12 días de desarrollo)
