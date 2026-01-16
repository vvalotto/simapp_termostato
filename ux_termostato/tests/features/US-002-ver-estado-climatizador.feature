# Feature: US-002 - Ver estado del climatizador

Feature: Ver estado del climatizador
  Como usuario del termostato
  Quiero ver el estado actual del climatizador (calentando, enfriando, reposo)
  Para saber si el sistema está actuando para alcanzar la temperatura deseada

  Background:
    Given la aplicación ux_termostato está iniciada
    And el panel climatizador está visible

  Scenario: Panel muestra los 3 indicadores visuales
    Given el termostato está encendido
    When se carga el panel climatizador
    Then se muestran 3 indicadores visuales
    And el indicador "Calor" tiene icono 🔥
    And el indicador "Reposo" tiene icono 🌬️
    And el indicador "Frío" tiene icono ❄️

  Scenario: Solo un indicador está activo cuando está calentando
    Given el termostato está encendido
    And el climatizador está en modo "calentando"
    When se actualiza el estado desde el servidor
    Then el indicador "Calor" está activo
    And el indicador "Reposo" está inactivo
    And el indicador "Frío" está inactivo

  Scenario: Solo un indicador está activo cuando está enfriando
    Given el termostato está encendido
    And el climatizador está en modo "enfriando"
    When se actualiza el estado desde el servidor
    Then el indicador "Frío" está activo
    And el indicador "Calor" está inactivo
    And el indicador "Reposo" está inactivo

  Scenario: Solo un indicador está activo cuando está en reposo
    Given el termostato está encendido
    And el climatizador está en modo "reposo"
    When se actualiza el estado desde el servidor
    Then el indicador "Reposo" está activo
    And el indicador "Calor" está inactivo
    And el indicador "Frío" está inactivo

  Scenario: Indicador activo se destaca visualmente - Calentando
    Given el termostato está encendido
    And el climatizador está en modo "calentando"
    When se renderiza el panel
    Then el indicador "Calor" tiene borde naranja (#f97316)
    And el indicador "Calor" tiene fondo naranja con transparencia
    And el indicador "Calor" tiene animación pulsante
    And el icono del indicador "Calor" está en color brillante

  Scenario: Indicador activo se destaca visualmente - Reposo
    Given el termostato está encendido
    And el climatizador está en modo "reposo"
    When se renderiza el panel
    Then el indicador "Reposo" tiene borde verde (#22c55e)
    And el indicador "Reposo" tiene fondo verde con transparencia
    And el indicador "Reposo" NO tiene animación
    And el icono del indicador "Reposo" está en color brillante

  Scenario: Indicador activo se destaca visualmente - Enfriando
    Given el termostato está encendido
    And el climatizador está en modo "enfriando"
    When se renderiza el panel
    Then el indicador "Frío" tiene borde azul (#3b82f6)
    And el indicador "Frío" tiene fondo azul con transparencia
    And el indicador "Frío" tiene animación pulsante
    And el icono del indicador "Frío" está en color brillante

  Scenario: Indicadores inactivos aparecen en gris apagado
    Given el termostato está encendido
    And el climatizador está en modo "calentando"
    When se renderiza el panel
    Then el indicador "Reposo" tiene borde gris (#64748b)
    And el indicador "Reposo" tiene fondo gris con transparencia
    And el indicador "Frío" tiene borde gris (#64748b)
    And el indicador "Frío" tiene fondo gris con transparencia

  Scenario: Estado se actualiza en tiempo real
    Given el termostato está encendido
    And el indicador "Calor" está activo
    When el servidor envía estado "reposo"
    Then el indicador "Calor" se desactiva inmediatamente
    And el indicador "Reposo" se activa inmediatamente
    And el cambio de estado es visible en menos de 100ms

  Scenario: Panel maneja estado apagado correctamente
    Given el termostato está apagado
    When se renderiza el panel
    Then todos los indicadores están inactivos
    And todos los indicadores tienen estilo "apagado"

  Scenario: Transición entre estados de climatización
    Given el termostato está encendido
    And el climatizador está en modo "calentando"
    When el servidor envía estado "enfriando"
    Then el indicador "Calor" se desactiva
    And la animación del indicador "Calor" se detiene
    And el indicador "Frío" se activa
    And la animación del indicador "Frío" comienza
    And la transición es suave y sin parpadeos
