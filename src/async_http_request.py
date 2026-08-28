import asyncio
import json

import aiohttp

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]


async def fetch_urls(urls: list[str], file_path: str) -> None:
    semaphore = asyncio.Semaphore(5)

    async def fetch_one(session: aiohttp.ClientSession, url: str) -> dict:
        async with semaphore:
            try:
                async with session.get(url) as response:
                    status = response.status
            except (TimeoutError, aiohttp.ClientError):
                status = 0
            return {
                "url": url,
                "status_code": status,
            }

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    with open(file_path, "w") as f:
        f.writelines(json.dumps(result) + "\n" for result in results)


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, file_path="./results.json"))
