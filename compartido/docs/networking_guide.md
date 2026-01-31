# Guía de Networking - Compartido

> Guía de uso de clientes y servidores socket

## Introducción

Este módulo proporciona clases base para comunicación TCP en el proyecto.

## Clientes Socket

### EphemeralSocketClient

Cliente con patrón efímero (conectar → enviar → cerrar).

**Cuándo usar:** Para envíos simples de mensajes sin mantener conexión.

### BaseSocketClient

Cliente base con soporte asíncrono.

**Cuándo usar:** Para comunicación persistente con el servidor.

## Servidores Socket

### BaseSocketServer

Servidor TCP con threading para múltiples conexiones.

**Cuándo usar:** Para recibir datos de múltiples clientes.

---

**Nota:** Este documento será completado con ejemplos de código y patrones de uso.
