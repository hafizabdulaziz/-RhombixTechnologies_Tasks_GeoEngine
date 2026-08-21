import socket
import ipaddress
from typing import Union

def resolve_ip(target: str) -> str:
    """
    Validate target IP (IPv4/IPv6) or resolve domain to IP.
    Classifies targets and rejects private/loopback/reserved ranges.
    """
    target = target.strip()
    
    # Check if it's an IP address
    try:
        ip = ipaddress.ip_address(target)
        if ip.is_private:
            raise ValueError(f"Target '{target}' is a private IP address and cannot be geolocated.")
        if ip.is_loopback:
            raise ValueError(f"Target '{target}' is a loopback address and cannot be geolocated.")
        if ip.is_reserved:
            raise ValueError(f"Target '{target}' is a reserved IP address and cannot be geolocated.")
        if ip.is_multicast:
            raise ValueError(f"Target '{target}' is a multicast IP address and cannot be geolocated.")
        return str(ip)
    except ValueError:
        # Not an IP, try resolving as domain
        try:
            return socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve or validate IP/domain '{target}'.")
