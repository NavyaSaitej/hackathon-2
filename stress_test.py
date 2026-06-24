import asyncio
import httpx
import logging
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Stress Agent - %(message)s')

URL = "http://127.0.0.1:8000/generate"
HEADERS = {
    "Content-Type": "application/json",
    "X-App-Secret": "quickcards-dev-secret"
}
PAYLOAD = {
    "url": "https://www.youtube.com/watch?v=Dq6dBoFor00"
}

async def make_request(client, worker_id):
    start = time.time()
    try:
        response = await client.post(URL, json=PAYLOAD, headers=HEADERS, timeout=30.0)
        elapsed = time.time() - start
        if response.status_code == 200:
            logging.info(f"Worker {worker_id}: Success in {elapsed:.2f}s")
        elif response.status_code == 429:
            logging.warning(f"Worker {worker_id}: Rate limited (429) in {elapsed:.2f}s")
        else:
            logging.error(f"Worker {worker_id}: Failed with status {response.status_code}")
    except Exception as e:
        logging.error(f"Worker {worker_id}: Exception occurred: {e}")

async def stress_test_round(num_workers=10):
    logging.info(f"Starting stress test round with {num_workers} concurrent requests...")
    async with httpx.AsyncClient() as client:
        tasks = [make_request(client, i) for i in range(num_workers)]
        await asyncio.gather(*tasks)
    logging.info("Stress test round complete.")

async def loop():
    while True:
        await stress_test_round(num_workers=8)
        logging.info("Sleeping for 60 seconds before next round...")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(loop())
