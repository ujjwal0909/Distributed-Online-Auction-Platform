import json
from http.server import BaseHTTPRequestHandler


class JSONRequestHandler(BaseHTTPRequestHandler):
    routes = []

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_PUT(self):
        self.handle_request("PUT")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def handle_request(self, method: str):
        path = self.path.split("?")[0]
        handler, params = self._match_route(method, path)
        if handler is None:
            self.send_error(404, "Not Found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b""
            payload = json.loads(body.decode("utf-8")) if body else {}
            status, response = handler(self, payload, params)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as exc:
            self.send_error(500, f"Internal error: {exc}")

    @classmethod
    @classmethod
    def _match_route(cls, method: str, path: str):
        for registered_method, parts, handler in cls.routes:
            if registered_method != method:
                continue
            candidate = path.strip("/").split("/") if path.strip("/") else []
            if len(candidate) != len(parts):
                continue
            params = {}
            match = True
            for idx, part in enumerate(parts):
                if part.startswith("<") and part.endswith(">"):
                    params[part[1:-1]] = candidate[idx]
                elif part != candidate[idx]:
                    match = False
                    break
            if match:
                return handler, params
        return None, {}

    @classmethod
    def route(cls, method: str, path: str):
        def decorator(func):
            parts = path.strip("/").split("/") if path.strip("/") else []
            cls.routes.append((method, parts, func))
            return func

        return decorator

