import click
import asyncio
import aiohttp
from src.services.geolocation_service import GeolocationService

async def fetch_ip(session, ip, service):
    try:
        data = service.get_location(ip)
        return f"{ip}: {data.city}"
    except Exception as e:
        return f"{ip}: Error - {e}"

async def bulk_lookup(ips, service):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ip(session, ip, service) for ip in ips]
        return await asyncio.gather(*tasks)

@click.command()
@click.argument('file', type=click.File('r'))
def bulk(file):
    """Bulk lookup from a file."""
    ips = [line.strip() for line in file if line.strip()]
    service = GeolocationService()
    results = asyncio.run(bulk_lookup(ips, service))
    for res in results:
        click.echo(res)

# Add to existing CLI
# ...
