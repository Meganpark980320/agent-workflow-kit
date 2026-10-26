"""표준 라이브러리만 쓰는 최소 웹 서버: 정적 파일(static/) + JSON API(/api/...).
실행: python app.py  (PORT 환경변수, 기본 3000, 0.0.0.0 바인딩)
"""
import json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
ITEMS = []  # 예시 저장소 (메모리)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            return self._json(200, {"ok": True})
        if self.path == "/api/items":
            return self._json(200, ITEMS)
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/items":
            n = int(self.headers.get("Content-Length") or 0)
            if n > 1_000_000:
                return self._json(413, {"error": "too large"})
            try:
                data = json.loads(self.rfile.read(n) or b"{}")
            except json.JSONDecodeError:
                return self._json(400, {"error": "invalid json"})
            text = str(data.get("text", "")).strip()
            if not text:
                return self._json(400, {"error": "text required"})
            ITEMS.append({"id": len(ITEMS) + 1, "text": text})
            return self._json(201, ITEMS[-1])
        return self._json(404, {"error": "not found"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"listening on 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
