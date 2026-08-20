import socket
import ipaddress

def resolve_ip(target: str) -> str:
    """Resolve domain to IP or validate IP."""
    try:
        # Check if it's already an IP
        ipaddress.ip_address(target)
        return target
    except ValueError:
        # Resolve domain
        return socket.gethostbyname(target)
