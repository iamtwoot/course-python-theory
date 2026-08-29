import asyncio
import json

import aiofiles
import aiohttp


async def fetch_urls(url_file_path: str) -> None:
    semaphore = asyncio.Semaphore(5)
    write_lock = asyncio.Lock()

    async with aiofiles.open(url_file_path, "r") as f:
        urls = [line.strip() for line in await f.readlines() if line.strip()]

    async with aiofiles.open("result.jsonl", "w") as out_file:

        async def fetch_one(session: aiohttp.ClientSession, url: str) -> None:
            async with semaphore:
                try:
                    async with session.get(url) as response:
                        content = await response.json()
                except (TimeoutError, aiohttp.ClientError):
                    return

            line = json.dumps({"url": url, "content": content}) + "\n"
            async with write_lock:
                await out_file.write(line)


        async with aiohttp.ClientSession() as session:
            tasks = [fetch_one(session, url) for url in urls]
            await asyncio.gather(*tasks)

