import json
import os
from http.server import HTTPServer
from urllib import error, request

from python_architecture.common.http import JSONRequestHandler

AUCTION_SERVICE = os.getenv("AUCTION_SERVICE_URL", "http://auction_service:8001")
BIDDING_SERVICE = os.getenv("BIDDING_SERVICE_URL", "http://bidding_service:8002")
HISTORY_SERVICE = os.getenv("HISTORY_SERVICE_URL", "http://history_service:8003")


class GatewayHandler(JSONRequestHandler):
    routes = []


def call_service(method: str, url: str, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"error": body or exc.reason}


@GatewayHandler.route("POST", "/api/auctions")
def create_auction(handler, payload, params):
    resp = call_service("POST", f"{AUCTION_SERVICE}/auctions", payload)
    auction = resp.get("auction")
    if auction:
        history_payload = {
            "auction_id": auction["id"],
            "event_type": "created",
            "payload": auction["name"],
        }
        call_service("POST", f"{HISTORY_SERVICE}/events", history_payload)
    return 201, resp


@GatewayHandler.route("GET", "/api/auctions")
def list_auctions(handler, payload, params):
    resp = call_service("GET", f"{AUCTION_SERVICE}/auctions")
    return 200, resp


@GatewayHandler.route("POST", "/api/auctions/<auction_id>/bid")
def place_bid(handler, payload, params):
    auction_id = params.get("auction_id")
    current = call_service("GET", f"{AUCTION_SERVICE}/auctions/{auction_id}")
    auction = current.get("auction")
    if not auction:
        return 404, {"error": "auction not found"}
    validation = call_service("POST", f"{BIDDING_SERVICE}/validate", {
        "amount": payload.get("amount"),
        "current_bid": auction.get("current_bid"),
        "bidder": payload.get("bidder"),
    })
    if not validation.get("ok"):
        return 200, validation
    update = call_service("POST", f"{AUCTION_SERVICE}/auctions/{auction_id}/bid", payload)
    call_service("POST", f"{HISTORY_SERVICE}/events", {
        "auction_id": auction_id,
        "event_type": "bid",
        "payload": f"{payload.get('bidder')} bid ${payload.get('amount')}",
    })
    return 200, update


@GatewayHandler.route("POST", "/api/auctions/<auction_id>/close")
def close_auction(handler, payload, params):
    auction_id = params.get("auction_id")
    closed = call_service("POST", f"{AUCTION_SERVICE}/auctions/{auction_id}/close")
    auction = closed.get("auction")
    if auction:
        call_service("POST", f"{HISTORY_SERVICE}/events", {
            "auction_id": auction_id,
            "event_type": "closed",
            "payload": auction.get("highest_bidder", ""),
        })
    return 200, closed


@GatewayHandler.route("GET", "/api/history")
def get_history(handler, payload, params):
    events = call_service("GET", f"{HISTORY_SERVICE}/events")
    return 200, events


def run():
    port = int(os.getenv("GATEWAY_PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), GatewayHandler)
    print(f"Gateway listening on {port}")
    server.serve_forever()


if __name__ == "__main__":
    run()

