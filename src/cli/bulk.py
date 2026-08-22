import click
import asyncio
import logging
import concurrent.futures
from typing import List
from src.services.geolocation_service import GeolocationService
from src.core.utils import resolve_ip

logger = logging.getLogger("GeoTraceBulk")
logging.basicConfig(level=logging.INFO)

# Limit concurrency to prevent rate-limiting
CONCURRENCY_LIMIT = 5

async def process_target(semaphore: asyncio.Semaphore, target: str, service: GeolocationService, executor: concurrent.futures.ThreadPoolExecutor):
    async with semaphore:
        loop = asyncio.get_running_loop()
        try:
            target = target.strip()
            # Offload blocking service calls to thread pool
            resolved_ip = await loop.run_in_executor(executor, resolve_ip, target)
            data = await loop.run_in_executor(executor, service.get_location, resolved_ip)
            return {"target": target, "status": "success", "data": data}
        except Exception as e:
            logger.error(f"Error processing {target}: {e}")
            return {"target": target, "status": "failed", "error": str(e)}

async def run_bulk_lookup(targets: List[str], service: GeolocationService):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY_LIMIT) as executor:
        tasks = [process_target(semaphore, target, service, executor) for target in targets]
        return await asyncio.gather(*tasks)

@click.command()
@click.argument('file', type=click.File('r'))
def bulk(file):
    """Bulk lookup from a file with bounded concurrency."""
    targets = [line.strip() for line in file if line.strip()]
    service = GeolocationService()
    
    logger.info(f"Starting bulk processing for {len(targets)} targets.")
    
    try:
        results = asyncio.run(run_bulk_lookup(targets, service))
    except Exception as e:
        logger.critical(f"Bulk processing failed: {e}")
        return
    
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
