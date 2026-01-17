# Feature: US-003 - Ver indicadores de alerta

Feature: Ver indicadores de alerta
  Como usuario del termostato
  Quiero ver indicadores LED que me alerten sobre fallas del sensor o batería baja
  Para tomar acción cuando haya problemas con el sistema

  Background:
    Given la aplicación ux_termostato está iniciada
    And la configuración está cargada correctamente
    And el panel de indicadores está visible en la parte superior

  Scenario: LEDs muestran estado normal al iniciar
    Given el termostato está encendido
    And NO hay fallas en el sistema
    Then el LED "Sensor" está en color gris apagado
    And el LED "Batería" está en color gris apagado
    And el label del LED izquierdo muestra "Sensor"
    And el label del LED derecho muestra "Batería"

  Scenario: LED sensor se enciende en rojo cuando hay falla
    Given el sistema está operando normalmente
    And el LED "Sensor" está en gris apagado
    When se recibe señal de falla del sensor (falla_sensor: true)
    Then el LED "Sensor" cambia a color rojo
    And el LED "Sensor" muestra animación pulsante
    And el LED "Batería" permanece en gris apagado

  Scenario: LED sensor vuelve a normal cuando se recupera
    Given el LED "Sensor" está en rojo pulsante
    And hay falla activa del sensor
    When se recibe señal de sensor recuperado (falla_sensor: false)
    Then el LED "Sensor" cambia a gris apagado
    And la animación pulsante se detiene

  Scenario: LED batería se enciende en amarillo cuando está baja
    Given el sistema está operando normalmente
    And el LED "Batería" está en gris apagado
    When se recibe señal de batería baja (bateria_baja: true)
    Then el LED "Batería" cambia a color amarillo
    And el LED "Batería" muestra animación pulsante
    And el LED "Sensor" permanece en gris apagado

  Scenario: LED batería vuelve a normal cuando se recarga
    Given el LED "Batería" está en amarillo pulsante
    And hay alerta de batería baja activa
    When se recibe señal de batería normal (bateria_baja: false)
    Then el LED "Batería" cambia a gris apagado
    And la animación pulsante se detiene

  Scenario: Múltiples alertas activas simultáneamente
    Given el sistema está operando normalmente
    And ambos LEDs están en gris apagado
    When se recibe señal de falla del sensor (falla_sensor: true)
    And se recibe señal de batería baja (bateria_baja: true)
    Then el LED "Sensor" está en rojo pulsante
    And el LED "Batería" está en amarillo pulsante
    And ambos LEDs muestran animación simultánea

  Scenario: Panel de indicadores está posicionado correctamente
    Given la aplicación está completamente cargada
    Then el panel de indicadores está en la parte superior de la UI
    And los LEDs están alineados horizontalmente
    And hay espaciado apropiado entre los LEDs

  Scenario: Animación pulsante es visible y atrae atención
    Given hay falla activa del sensor
    And el LED "Sensor" está en rojo pulsante
    Then la animación pulsante es fluida (sin saltos)
    And el ciclo de animación se repite continuamente
    And la animación es suficientemente visible para llamar la atención
