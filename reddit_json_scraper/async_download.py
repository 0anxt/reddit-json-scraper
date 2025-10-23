import asyncio
import os
from asyncio import Semaphore
import aiohttp
import aiofiles

async def _download_one(session, sem: Semaphore, url: str, out_path: str, chunk_size: int = 1 << 16):
    async with sem:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Failed {url} status {resp.status}")
            tmp = out_path + ".part"
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            async with aiofiles.open(tmp, "wb") as f:
                async for chunk in resp.content.iter_chunked(chunk_size):
                    await f.write(chunk)
            os.replace(tmp, out_path)

async def download_many(urls_and_paths, concurrency: int = 6, total_timeout: float = 180.0):
    sem = Semaphore(concurrency)
    timeout = aiohttp.ClientTimeout(total=total_timeout)
    connector = aiohttp.TCPConnector(limit=concurrency)
    headers = {"User-Agent": "reddit-json-scraper/async"}
    async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
        tasks = [asyncio.create_task(_download_one(session, sem, u, p)) for u, p in urls_and_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
