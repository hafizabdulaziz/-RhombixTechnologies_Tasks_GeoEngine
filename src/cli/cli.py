import click
from src.services.geolocation_service import GeolocationService
from src.services.history import HistoryService
from src.services.map_service import generate_map_html
from src.core.utils import resolve_ip
from src.database.models import init_db

init_db()
service = GeolocationService()

@click.group()
def cli():
    """GeoEngine CLI"""
    pass

@cli.command()
@click.argument('target')
def lookup(target):
    """Lookup geolocation for an IP or Domain."""
    try:
        ip = resolve_ip(target)
        data = service.get_location(ip)
        HistoryService.save_lookup(data)
        click.echo(f"Location: {data.city}, {data.country}")
    except Exception as e:
        click.echo(f"Error: Could not resolve or lookup '{target}'. {e}")

@cli.command()
@click.argument('target')
def map(target):
    """Generate map for an IP or Domain."""
    ip = resolve_ip(target)
    data = service.get_location(ip)
    if data.latitude and data.longitude:
        generate_map_html(data.latitude, data.longitude, data.city or "Unknown")
        click.echo("Map generated.")
    else:
        click.echo("No coordinates found.")

if __name__ == "__main__":
    cli()
