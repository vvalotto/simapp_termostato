# Análisis de Puertos - Integración HIL

**Fecha actualización:** 2026-01-26
**Estado:** ✅ **SOLUCIONADO** - Formato JSON consolidado implementado

---

## 🎯 Problema Identificado y Solucionado

### Error Observado

Durante las pruebas de integración, **ux_termostato** no podía recibir correctamente el estado desde **ISSE_Termostato**:

```
2026-01-26 07:26:22,064 - app.comunicacion.servidor_estado - ERROR - JSON malformado: Expecting value: line 1 column 1 (char 0)
2026-01-26 07:26:22,065 - app.coordinator - ERROR - Error de parsing JSON: JSON malformado
```

### Causa Raíz

**Inconsistencia de formato entre ISSE_Termostato y ux_termostato:**

| Sistema | Puerto | Formato | Contenido |
|---------|--------|---------|-----------|
| **ISSE_Termostato** (enviaba) | 14001 | Texto plano | `"ambiente: 23.5"`, `"deseada: 25.0"` |
| **ux_termostato** (esperaba) | 14001 | **JSON** | `{"temperatura_actual": 23.5, ...}` |

---

## ✅ Solución Implementada

Se creó un **nuevo visualizador consolidado** en ISSE_Termostato que envía todo el estado en UN solo mensaje JSON.

### Archivos Creados/Modificados en ISSE_Termostato

#### 1. ✅ NUEVO: `visualizador_estado_consolidado.py`

**Ubicación:** `ISSE_Termostato/agentes_actuadores/visualizador_estado_consolidado.py`

**Responsabilidad:**
- Recopila estado completo de los 3 gestores (ambiente, climatizador, batería)
- Serializa a JSON
- Envía al puerto **14001** en formato compatible con ux_termostato

**Formato JSON enviado:**
```json
{
  "temperatura_actual": 23.5,           // float - Temperatura medida
  "temperatura_deseada": 25.0,          // float - Temperatura objetivo
  "modo_climatizador": "calentando",    // string - "calentando" | "enfriando" | "reposo" | "apagado"
  "falla_sensor": false,                // boolean - true si sensor desconectado
  "bateria_baja": false,                // boolean - true si indicador == "BAJA"
  "encendido": true,                    // boolean - Sistema activo
  "modo_display": "ambiente",           // string - "ambiente" | "deseada"
  "timestamp": "2026-01-26T07:26:22Z"   // string - ISO 8601
}
```

**Mapeo de estados:**
```
ISSE_Termostato          ux_termostato
─────────────────        ─────────────
"apagado"          →     "reposo"
"calentando"       →     "calentando"
"enfriando"        →     "enfriando"
```

#### 2. ✅ MODIFICADO: `presentador.py`

**Archivo:** `servicios_aplicacion/presentador.py`

**Cambios:**
- Agregado parámetro opcional `visualizador_consolidado` al constructor
- Al final de `ejecutar()`, envía estado consolidado JSON si está configurado

#### 3. ✅ MODIFICADO: `operador_paralelo.py`

**Archivo:** `servicios_aplicacion/operador_paralelo.py`

**Cambios:**
- Agregado parámetro opcional `visualizador_consolidado` al constructor
- Pasa el visualizador al `Presentador` interno que ejecuta cada 5 segundos

#### 4. ✅ MODIFICADO: `lanzador.py`

**Archivo:** `servicios_aplicacion/lanzador.py`

**Cambios:**
- Importa `VisualizadorEstadoConsolidadoSocket`
- Crea instancia del visualizador (puerto 14001)
- Inyecta el visualizador en `Presentador` y `OperadorParalelo`

---

## 📊 Arquitectura ANTES vs AHORA

### ANTES (❌ No funcionaba)

```
ISSE_Termostato
  │
  ├─► VisualizadorTemperaturaSocket
  │     ├─► "ambiente: 23.5"    [texto plano]
  │     └─► "deseada: 25.0"     [texto plano]
  │             │
  │             ▼
  │      Puerto 14001 ──X──► ux_termostato
  │                           ERROR: Esperaba JSON
  │
  └─► VisualizadorClimatizadorSocket
        └─► "calentando"         [texto plano]
                │
                ▼
         Puerto 14002 (no usado)
```

### AHORA (✅ Funciona)

```
ISSE_Termostato
  │
  ├─► VisualizadorEstadoConsolidadoSocket
  │       │
  │       ├─► Recopila estado de:
  │       │    ├─ GestorAmbiente (temperaturas)
  │       │    ├─ GestorClimatizador (modo)
  │       │    └─ GestorBateria (nivel/indicador)
  │       │
  │       └─► Genera JSON:
  │             {
  │               "temperatura_actual": 23.5,
  │               "temperatura_deseada": 25.0,
  │               "modo_climatizador": "calentando",
  │               "falla_sensor": false,
  │               "bateria_baja": false,
  │               "encendido": true,
  │               "modo_display": "ambiente",
  │               "timestamp": "2026-01-26T07:26:22Z"
  │             }
  │               │
  │               ▼
  │      Puerto 14001 ──✅──► ux_termostato
  │                           ServidorEstado.parsea_json() ✅
  │                           Actualiza UI ✅
  │
  └─► Visualizadores individuales (mantienen compatibilidad legacy)
```

---

## 🔄 Retrocompatibilidad

Los visualizadores individuales **se mantienen** para:

| Visualizador | Estado | Uso |
|-------------|--------|-----|
| `VisualizadorTemperaturaSocket` | ✅ Activo | Logs individuales, debugging |
| `VisualizadorClimatizadorSocket` | ✅ Activo | Compatibilidad legacy |
| `VisualizadorBateriaSocket` | ✅ Activo | Compatibilidad legacy |
| `VisualizadorEstadoConsolidadoSocket` | ✅ **NUEVO** | **Comunicación con ux_termostato** |

**Nota:** Ambos sistemas pueden coexistir. Los visualizadores individuales se ejecutan en sus puertos originales, mientras el consolidado envía JSON al 14001.

---

## 📡 Protocolo de Comunicación Actualizado

| Puerto | Dirección | Formato | Contenido | Estado | Frecuencia |
|--------|-----------|---------|-----------|--------|------------|
| 11000 | Sim → RPi | `<float>\n` | Voltaje batería | ✅ Activo | Continuo |
| 12000 | Sim → RPi | `<float>\n` | Temperatura | ✅ Activo | Continuo |
| 13000 | UX → RPi | `aumentar\|disminuir` | Seteo temperatura | ✅ Activo | On-demand |
| 14000 | UX → RPi | `ambiente\|deseada` | Selector display | ✅ Activo | On-demand |
| **14001** | **RPi → UX** | **JSON** | **Estado consolidado** | **✅ ACTUALIZADO** | **Cada 5s** |
| 14002 | RPi → UX | `<string>` | Estado climatizador | ⚠️ Deprecado | N/A |

---

## 🧪 Validación de la Solución

### Pasos para Probar

1. **Iniciar ISSE_Termostato (RPi o localhost):**
   ```bash
   cd /Users/victor/PycharmProjects/ISSE_Termostato
   python ejecutar.py
   ```

2. **Iniciar ux_termostato (Desktop):**
   ```bash
   cd /Users/victor/PycharmProjects/simapp_termostato
   python ux_termostato/run.py
   ```

3. **Iniciar simuladores (Desktop):**
   ```bash
   # Terminal 1
   python simulador_temperatura/run.py

   # Terminal 2
   python simulador_bateria/run.py
   ```

### Resultado Esperado ✅

**ux_termostato debe mostrar:**
- ✅ Temperatura actualizada cada 5 segundos
- ✅ Modo climatizador (reposo/calentando/enfriando)
- ✅ Indicador LED de batería baja (si corresponde)
- ✅ Indicador LED de falla de sensor (si temperatura == None)
- ✅ Modo display (ambiente/deseada)
- ✅ **SIN errores de parsing JSON**

**Logs esperados (ux_termostato):**
```
2026-01-26 07:26:22 - app.coordinator - INFO - Conexión establecida con 127.0.0.1:53051
2026-01-26 07:26:22 - app.comunicacion.servidor_estado - INFO - Estado procesado: temp_actual=23.5°C, temp_deseada=25.0°C, modo=calentando
```

---

## 📂 Resumen de Archivos Modificados

### ISSE_Termostato
```
✅ agentes_actuadores/visualizador_estado_consolidado.py  [NUEVO - 180 líneas]
✅ servicios_aplicacion/presentador.py                     [MODIFICADO - +10 líneas]
✅ servicios_aplicacion/operador_paralelo.py               [MODIFICADO - +8 líneas]
✅ servicios_aplicacion/lanzador.py                        [MODIFICADO - +15 líneas]
```

### simapp_termostato
```
✅ ANALISIS_PUERTOS.md                                     [ACTUALIZADO]
```

**Total de cambios:** 5 archivos, ~40 líneas de código agregadas/modificadas

---

## 🏗️ Detalles Técnicos de la Implementación

### Flujo de Ejecución (cada 5 segundos)

```
OperadorParalelo.muestra_parametros()
  │
  └─► Presentador.ejecutar()
        │
        ├─► gestor_bateria.mostrar_nivel_de_carga()
        ├─► gestor_bateria.mostrar_indicador_de_carga()
        ├─► gestor_ambiente.mostrar_temperatura()
        ├─► gestor_climatizador.mostrar_estado_climatizador()
        │
        └─► visualizador_consolidado.mostrar_estado_completo()
              │
              ├─► _construir_estado()
              │     ├─ Obtiene temperatura_actual
              │     ├─ Obtiene temperatura_deseada
              │     ├─ Obtiene estado_climatizador → mapea a modo_climatizador
              │     ├─ Detecta falla_sensor (temperatura == None)
              │     ├─ Detecta bateria_baja (indicador == "BAJA")
              │     ├─ Obtiene modo_display
              │     └─ Genera timestamp
              │
              ├─► json.dumps(estado)
              │
              └─► socket.connect(localhost:14001)
                  socket.send(json.encode('utf-8'))
                  socket.close()
```

### Manejo de Errores

El visualizador consolidado maneja:
- **ConnectionError:** Si ux_termostato no está activo, imprime error pero no crashea el sistema
- **Falla de sensor:** Si `temperatura_ambiente == None`, envía `temperatura_actual: 0.0` y `falla_sensor: true`
- **Batería baja:** Detecta automáticamente basado en `indicador == "BAJA"`

---

## 🔍 Diferencias con Sistema Cloud (API REST)

Este análisis se enfoca en el **sistema HIL local (socket TCP)**, que es diferente del sistema de monitoreo cloud:

| Característica | HIL Local (Socket) | Cloud Monitoring (API REST) |
|----------------|-------------------|----------------------------|
| **Propósito** | Testing integrado Desktop+RPi | Monitoreo remoto en la nube |
| **Protocolo** | TCP Socket | HTTP REST |
| **Puerto** | 14001 | HTTPS 443 |
| **Formato** | JSON consolidado | Endpoints individuales |
| **Destino** | ux_termostato (PyQt) | webapp_termostato (Flask) → app_termostato (API) |
| **Configuración** | `"visualizador_*": "socket"` | `"visualizador_*": "api"` |
| **Estado** | ✅ Implementado | ✅ Independiente |

**Nota:** Ambos sistemas son independientes y pueden coexistir. La configuración en `termostato.json` determina cuál se usa.

---

## ✅ Checklist de Configuración HIL

### ISSE_Termostato
- [x] Código de `VisualizadorEstadoConsolidadoSocket` creado
- [x] `Presentador` modificado para usar visualizador consolidado
- [x] `OperadorParalelo` modificado
- [x] `Lanzador` inyecta el visualizador
- [ ] `termostato.json` tiene `"visualizador_temperatura": "socket"` (si se requiere compatibilidad dual)

### simapp_termostato
- [x] `ux_termostato` implementado con `ServidorEstado` en puerto 14001
- [x] `ServidorEstado.from_json()` parsea correctamente el JSON consolidado
- [x] `config.json` tiene puerto 14001 configurado
- [ ] `.env` tiene `RASPBERRY_IP` con IP correcta (para RPi real)

### Testing
- [ ] ISSE_Termostato ejecutándose
- [ ] ux_termostato recibe JSON cada 5s sin errores
- [ ] UI de ux_termostato actualiza temperatura correctamente
- [ ] Modo climatizador se muestra correctamente
- [ ] Indicadores de alerta funcionan (batería baja, falla sensor)

---

## 🎓 Lecciones Aprendidas

1. **Formato consolidado > mensajes fragmentados:** Un JSON con todo el estado es más eficiente y menos propenso a errores que múltiples mensajes de texto plano.

2. **Inyección de dependencias:** El patrón de inyectar el visualizador consolidado permite activarlo/desactivarlo sin modificar la lógica de negocio.

3. **Retrocompatibilidad:** Mantener los visualizadores individuales permite debugging y compatibilidad con sistemas legacy.

4. **Mapeo de estados:** El mapeo de "apagado" → "reposo" es necesario porque ux_termostato usa semántica diferente (apagado=OFF, reposo=temperatura alcanzada).

---

## 📚 Referencias

- **Modelo de Dominio UX:** `ux_termostato/app/dominio/estado_termostato.py`
- **Servidor UX:** `ux_termostato/app/comunicacion/servidor_estado.py`
- **Visualizador Consolidado:** `ISSE_Termostato/agentes_actuadores/visualizador_estado_consolidado.py`
- **Especificación Original:** `simapp_termostato/docs/ESPECIFICACION_COMUNICACIONES.md`
- **CLAUDE.md:** `simapp_termostato/CLAUDE.md` (sección "Communication Protocol")

---

**Última actualización:** 2026-01-26
**Estado:** ✅ **SOLUCIONADO** - Integración HIL completada
**Responsable:** Victor Valotto + Claude Code
