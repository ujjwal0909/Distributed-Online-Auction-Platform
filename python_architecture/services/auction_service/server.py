import json
import os
import threading
import time
from http.server import HTTPServer
from typing import Dict

from python_architecture.common.http import JSONRequestHandler


auditions: Dict[str, dict] = {}
_lock = threading.Lock()


class AuctionHandler(JSONRequestHandler):
    routes = []


@AuctionHandler.route("POST", "/auctions")
def create_auction(handler, payload, params):
    name = payload.get("name")
    starting_bid = payload.get("starting_bid", 0)
    duration = payload.get("duration_seconds", 60)
    if not name:
        return 400, {"error": "name is required"}
    if starting_bid <= 0:
        return 400, {"error": "starting_bid must be positive"}
    auction_id = str(int(time.time() * 1000))
    auction = {
        "id": auction_id,
        "name": name,
        "description": payload.get("description", ""),
        "starting_bid": starting_bid,
        "current_bid": starting_bid,
        "highest_bidder": "",
        "duration_seconds": duration,
        "status": "OPEN",
        "closing_time": time.time() + duration,
    }
    with _lock:
        auditions[auction_id] = auction
    return 201, {"auction": auction}


@AuctionHandler.route("GET", "/auctions")
def list_auctions(handler, payload, params):
    with _lock:
        values = list(auditions.values())
    return 200, {"auctions": values}


@AuctionHandler.route("GET", "/auctions/<auction_id>")
def get_auction(handler, payload, params):
    auction_id = params.get("auction_id")
    with _lock:
        auction = auditions.get(auction_id)
    if not auction:
        return 404, {"error": "auction not found"}
    return 200, {"auction": auction}


@AuctionHandler.route("POST", "/auctions/<auction_id>/bid")
def update_bid(handler, payload, params):
    auction_id = params.get("auction_id")
    amount = payload.get("amount", 0)
    bidder = payload.get("bidder", "")
    if amount <= 0 or not bidder:
        return 400, {"error": "invalid bid"}
    with _lock:
        auction = auditions.get(auction_id)
        if not auction:
            return 404, {"error": "auction not found"}
        auction["current_bid"] = amount
        auction["highest_bidder"] = bidder
    return 200, {"auction": auction}


@AuctionHandler.route("POST", "/auctions/<auction_id>/close")
def close_auction(handler, payload, params):
    auction_id = params.get("auction_id")
    with _lock:
        auction = auditions.get(auction_id)
        if not auction:
            return 404, {"error": "auction not found"}
        auction["status"] = "CLOSED"
        auction["closing_time"] = time.time()
    return 200, {"auction": auction}


def run():
    port = int(os.getenv("AUCTION_SERVICE_PORT", "8001"))
    server = HTTPServer(("0.0.0.0", port), AuctionHandler)
    print(f"Auction service listening on {port}")
    server.serve_forever()


if __name__ == "__main__":
    run()

