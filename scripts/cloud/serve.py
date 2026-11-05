"""Loopback-only development preview; notification/network APIs are blocked."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Additional CSP intersects the HTML's policy. No fetch, XHR,
        # WebSocket, EventSource, or beacon can reach email/Chat endpoints.
        self.send_header('Content-Security-Policy', "connect-src 'none'; form-action 'none'; object-src 'none'")
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        # Serve only public app entry points, not .git, records, or photos.
        path = self.path.split('?', 1)[0]
        if path == '/':
            self.path = '/index.html'
        elif path not in {f'/{name}' for name in (
            'index.html', 'heian-review.html', 'onin-review.html',
            'kamakura-review.html', 'yuika-review-v2.html',
        )}:
            self.send_error(404)
            return
        super().do_GET()

    def do_HEAD(self):
        self.send_error(405)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1', args.port), partial(PreviewHandler, directory=str(ROOT))) as server:
        print(f'Preview: http://127.0.0.1:{server.server_port}/ (notification APIs blocked)', flush=True)
        server.serve_forever()
