# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2026-01-10

### Descripcion

Primera version estable del Simulador de Temperatura. Implementa arquitectura MVC con patrones Factory y Coordinator para comunicacion con ISSE_Termostato via TCP.

### Agregado

- **Dominio**
  - `GeneradorTemperatura`: Generacion de valores con variacion senoidal
  - `VariacionSenoidal`: Algoritmo de variacion configurable (amplitud, periodo, base)
  - `EstadoTemperatura`: Modelo de datos inmutable

- **Comunicacion**
  - `ClienteTemperatura`: Cliente TCP efimero al puerto 12000
  - `ServicioEnvioTemperatura`: Integracion generador + cliente con senales Qt

- **Presentacion (MVC)**
  - `PanelEstado`: Visualizacion de temperatura actual, modo y conexion
  - `PanelControlTemperatura`: Ajuste de parametros senoidales y modo manual
  - `PanelGrafico`: Grafico en tiempo real con pyqtgraph
  - `PanelConexion`: Configuracion IP/puerto y control de conexion

- **Arquitectura**
  - `ComponenteFactory`: Creacion centralizada de componentes
  - `SimuladorCoordinator`: Gestion de senales entre componentes
  - `UIPrincipalCompositor`: Composicion de layout UI

- **Configuracion**
  - `ConfigManager`: Carga de configuracion desde JSON y variables de entorno
  - Soporte para `config.json` y `.env`

- **Calidad**
  - 283 tests unitarios
  - Scripts de analisis de calidad (metrics, gates, reports)
  - Pylint score: 9.52/10
  - Complejidad ciclomatica: 1.36
  - Indice mantenibilidad: 70.10

- **Documentacion**
  - README.md con instrucciones de uso
  - Arquitectura detallada con diagramas
  - Informes de calidad de diseno

### Metricas

| Metrica | Valor |
|---------|-------|
| Lineas de codigo | 4,032 |
| Archivos Python | 36 |
| Funciones | 319 |
| Tests | 283 |
| Pylint | 9.52/10 |
| Quality Grade | A |

---

## Plantilla para Futuras Versiones

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Agregado
- Nuevas funcionalidades

### Cambiado
- Cambios en funcionalidades existentes

### Obsoleto
- Funcionalidades que seran eliminadas

### Eliminado
- Funcionalidades eliminadas

### Corregido
- Correccion de errores

### Seguridad
- Correcciones de vulnerabilidades
```
