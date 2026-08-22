import socket
import ipaddress
import re

def resolve_ip(target: str) -> str:
    """
    Validate target IP (IPv4/IPv6) or resolve domain to IP.
    Classifies targets and rejects private/loopback/reserved ranges.
    """
    target = target.strip()
    if not target:
        raise ValueError("Target cannot be empty.")
    
    # Check if it's an IP address
    try:
        ip = ipaddress.ip_address(target)
        if ip.is_private:
            raise ValueError(f"'{target}' is a private IP address (internal network).")
        if ip.is_loopback:
            raise ValueError(f"'{target}' is a loopback address (local system).")
        if ip.is_reserved:
            raise ValueError(f"'{target}' is a reserved IP address.")
        if ip.is_multicast:
            raise ValueError(f"'{target}' is a multicast IP address.")
        return str(ip)
    except ValueError:
        # Not an IP, try resolving as domain
        # Simple domain regex validation
        domain_regex = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(domain_regex, target):
            raise ValueError(f"'{target}' is not a valid IP or domain format.")
            
        try:
            return socket.gethostbyname(target)
        except socket.gaierror:
            raise ValueError(f"Could not resolve domain '{target}'.")
