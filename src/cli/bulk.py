import click
import asyncio
import logging
from typing import List
from src.services.geolocation_service import GeolocationService
from src.core.utils import resolve_ip

logger = logging.getLogger("GeoTraceBulk")
logging.basicConfig(level=logging.INFO)

# Limit concurrency to prevent rate-limiting
CONCURRENCY_LIMIT = 5

async def process_target(semaphore: asyncio.Semaphore, target: str, service: GeolocationService):
    async with semaphore:
        try:
            # Run blocking service call in thread pool if needed, 
            # but for now we keep it simple as the service is synchronous.
            # In a production environment, we should make the service async.
            target = target.strip()
            resolved_ip = resolve_ip(target)
            data = service.get_location(resolved_ip)
            return {"target": target, "status": "success", "data": data}
        except Exception as e:
            return {"target": target, "status": "failed", "error": str(e)}

async def run_bulk_lookup(targets: List[str], service: GeolocationService):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    tasks = [process_target(semaphore, target, service) for target in targets]
    return await asyncio.gather(*tasks)

@click.command()
@click.argument('file', type=click.File('r'))
def bulk(file):
    """Bulk lookup from a file with bounded concurrency."""
    targets = [line.strip() for line in file if line.strip()]
    service = GeolocationService()
    
    logger.info(f"Starting bulk processing for {len(targets)} targets.")
    
    results = asyncio.run(run_bulk_lookup(targets, service))
    
    success_count = 0
    fail_count = 0
    
    for res in results:
        if res["status"] == "success":
            click.echo(f"[SUCCESS] {res['target']}: {res['data'].city}, {res['data'].country}")
            success_count += 1
        else:
            click.echo(f"[FAILED]  {res['target']}: {res['error']}")
            fail_count += 1
            
    click.echo(f"\nProcessing complete. Success: {success_count}, Failed: {fail_count}")
