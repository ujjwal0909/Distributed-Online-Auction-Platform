import json
import sys
import time
from statistics import mean
from urllib import request


def call(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(url):
    with request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run(base_url: str, iterations: int = 5):
    latencies = []
    for idx in range(iterations):
        start = time.time()
        create = call(f"{base_url}/api/auctions", {
            "name": f"Load Test Item {idx}",
            "description": "Benchmark item",
            "starting_bid": 10 + idx,
            "duration_seconds": 120,
        })
        auction_id = create.get("auction", {}).get("id")
        call(f"{base_url}/api/auctions/{auction_id}/bid", {"bidder": "bot", "amount": 20 + idx})
        call(f"{base_url}/api/auctions/{auction_id}/close", {})
        get(f"{base_url}/api/history")
        latencies.append(time.time() - start)
    throughput = iterations / sum(latencies)
    print(f"Latency avg: {mean(latencies):.4f}s")
    print(f"Throughput: {throughput:.2f} ops/s")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <base_url>")
        sys.exit(1)
    run(sys.argv[1])

