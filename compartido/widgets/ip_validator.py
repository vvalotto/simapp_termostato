"""
Validadores de IP para ConfigPanel.

Define el protocolo para validar direcciones IP y una implementación
por defecto, permitiendo extensibilidad sin modificar ConfigPanel.
"""
# pylint: disable=unnecessary-ellipsis
import re
from typing import Protocol


class IPValidator(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocolo para validadores de direcciones IP.

    Permite inyectar diferentes estrategias de validación de IP
    sin modificar ConfigPanel, cumpliendo con el principio Open/Closed.

    Example:
        class StrictIPValidator:
            def validate(self, ip: str) -> bool:
                # Validación estricta personalizada
                ...

            def get_error_message(self) -> str:
                return "IP inválida"

        panel = ConfigPanel(ip_validator=StrictIPValidator())
    """

    def validate(self, ip: str) -> bool:
        """
        Valida una dirección IP.

        Args:
            ip: Cadena con la dirección IP a validar.

        Returns:
            True si la IP es válida, False en caso contrario.
        """
        ...

    def get_error_message(self) -> str:
        """
        Retorna el mensaje de error para IPs inválidas.

        Returns:
            Mensaje de error descriptivo.
        """
        ...


class DefaultIPValidator:
    """
    Validador de direcciones IPv4 por defecto.

    Valida que la IP tenga formato correcto: cuatro octetos
    numéricos separados por puntos, cada uno entre 0 y 255.
    También acepta 'localhost' como valor válido.
    """

    _IP_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )

    def validate(self, ip: str) -> bool:
        """
        Valida una dirección IPv4.

        Args:
            ip: Cadena con la dirección IP a validar.

        Returns:
            True si la IP es válida o es 'localhost'.
        """
        if not ip:
            return False

        ip_stripped = ip.strip()

        # Aceptar localhost
        if ip_stripped.lower() == 'localhost':
            return True

        # Validar formato IPv4
        return bool(self._IP_PATTERN.match(ip_stripped))

    def get_error_message(self) -> str:
        """Retorna el mensaje de error para IPs inválidas."""
        return "IP inválida. Use formato: xxx.xxx.xxx.xxx o localhost"
