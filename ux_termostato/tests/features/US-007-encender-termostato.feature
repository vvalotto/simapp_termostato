# language: es

Característica: Encender el termostato
  Como usuario del termostato
  Quiero poder encender el sistema con un botón
  Para activar la climatización cuando lo necesite

  Antecedentes:
    Dado que la aplicación UX Termostato está abierta
    Y el termostato está apagado

  Escenario: Ver botón ENCENDER cuando el termostato está apagado
    Cuando visualizo el panel de control power
    Entonces veo el botón "ENCENDER"
    Y el botón tiene el icono de power ⚡
    Y el botón tiene color verde
    Y el botón está habilitado

  Escenario: Encender el termostato exitosamente
    Dado que el termostato está apagado
    Cuando presiono el botón "ENCENDER"
    Entonces el termostato cambia a estado encendido
    Y el botón cambia a "APAGAR"
    Y el color del botón cambia a gris
    Y se envía el comando {"comando": "power", "estado": "on"} al Raspberry Pi
    Y el display muestra la temperatura actual en lugar de "---"
    Y los botones de control de temperatura se habilitan

  Escenario: Habilitar controles al encender
    Dado que el termostato está apagado
    Y los botones SUBIR y BAJAR están deshabilitados
    Cuando presiono el botón "ENCENDER"
    Entonces el botón SUBIR se habilita
    Y el botón BAJAR se habilita
    Y el selector de vista se habilita

  Escenario: Display muestra temperatura al encender
    Dado que el termostato está apagado
    Y el display muestra "---"
    Cuando presiono el botón "ENCENDER"
    Y el sistema recibe temperatura 22.5°C del Raspberry Pi
    Entonces el display muestra "22.5 °C"
    Y el label del display indica "Temperatura Ambiente"

  Escenario: Estado del climatizador al encender
    Dado que el termostato está apagado
    Y el climatizador muestra estado "apagado" (todo gris)
    Cuando presiono el botón "ENCENDER"
    Entonces el climatizador comienza a actualizarse
    Y el estado del climatizador refleja el modo actual (calor/reposo/frío)

  Escenario: Feedback visual al presionar el botón
    Dado que el termostato está apagado
    Cuando presiono el botón "ENCENDER"
    Entonces veo feedback visual en el botón (scale-95)
    Y el cambio de estado es inmediato

  Escenario: No se puede encender si ya está encendido
    Dado que el termostato está encendido
    Cuando visualizo el panel de control power
    Entonces veo el botón "APAGAR"
    Y no veo el botón "ENCENDER"

  Escenario: Envío de comando al Raspberry Pi
    Dado que el termostato está apagado
    Y el cliente está conectado al puerto 13000 del Raspberry Pi
    Cuando presiono el botón "ENCENDER"
    Entonces se envía un comando JSON con estructura:
      """
      {
        "comando": "power",
        "estado": "on"
      }
      """
    Y el comando se envía al puerto 13000
    Y no se espera confirmación del Raspberry Pi (fire and forget)
