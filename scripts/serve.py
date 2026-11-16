from __future__ import annotations

import argparse
import mimetypes
import os
import posixpath
import re
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parent.parent
APP = REPO / "app"
TIMELINE = REPO / "video" / "timeline.json"

EXTRA_TYPES = {
    ".pmtiles": "application/octet-stream",
    ".bin": "application/octet-stream",
    ".geojson": "application/geo+json",
    ".json": "application/json",
    ".mjs": "text/javascript",
    ".js": "text/javascript",
    ".csv": "text/csv; charset=utf-8",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

RANGE_RE = re.compile(r"^bytes=(\d*)-(\d*)$")


class Handler(SimpleHTTPRequestHandler):
    """Serves files from the app folder (and an optional overlay) with Range support."""

    overlay: Path | None = None
    root: Path = APP

    def log_message(self, fmt: str, *args) -> None:  # quieter log, one line per request
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.send_header("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges, ETag")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def resolve(self, url_path: str) -> Path | None:
        """Map a URL path to a file, or None if it is outside the roots or missing."""
        path = posixpath.normpath(unquote(urlsplit(url_path).path))
        if path == "/data/timeline.json" and TIMELINE.is_file():
            return TIMELINE
        rel = path.lstrip("/")
        if rel in ("", "."):
            rel = "index.html"
        candidates = []
        if self.overlay is not None:
            candidates.append(self.overlay)
        candidates.append(self.root)
        for base in candidates:
            target = (base / rel).resolve()
            try:
                target.relative_to(base.resolve())
            except ValueError:
                return None
            if target.is_dir():
                target = target / "index.html"
            if target.is_file():
                return target
        return None

    def guess_type(self, path) -> str:
        ext = os.path.splitext(str(path))[1].lower()
        if ext in EXTRA_TYPES:
            return EXTRA_TYPES[ext]
        return mimetypes.guess_type(str(path))[0] or "application/octet-stream"

    def do_HEAD(self) -> None:
        self.serve(head=True)

    def do_GET(self) -> None:
        self.serve(head=False)

    def serve(self, head: bool) -> None:
        target = self.resolve(self.path)
        if target is None:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        size = target.stat().st_size
        ctype = self.guess_type(target)
        start, end = 0, size - 1
        status = HTTPStatus.OK
        rng = self.headers.get("Range")
        if rng:
            m = RANGE_RE.match(rng.strip().split(",")[0].strip())
            if not m or (m.group(1) == "" and m.group(2) == ""):
                self.send_range_error(size)
                return
            first, last = m.group(1), m.group(2)
            if first == "":  # suffix range: the last N bytes
                n = int(last)
                if n == 0:
                    self.send_range_error(size)
                    return
                start, end = max(0, size - n), size - 1
            else:
                start = int(first)
                end = min(int(last), size - 1) if last else size - 1
            if start >= size or start > end:
                self.send_range_error(size)
                return
            status = HTTPStatus.PARTIAL_CONTENT
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        self.send_header("Last-Modified", self.date_time_string(int(target.stat().st_mtime)))
        if status == HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if head:
            return
        with open(target, "rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(1 << 16, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                remaining -= len(chunk)

    def send_range_error(self, size: int) -> None:
        self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
        self.send_header("Content-Range", f"bytes */{size}")
        self.send_header("Content-Length", "0")
        self.end_headers()


def main() -> None:
    ap = argparse.ArgumentParser(description="Range-capable static server for app/")
    ap.add_argument("port", type=int, help="port to listen on, e.g. 8765")
    ap.add_argument("--host", default="127.0.0.1", help="interface to bind (default 127.0.0.1)")
    ap.add_argument("--root", default=str(APP), help="folder to serve (default app/)")
    ap.add_argument("--overlay", default=None, help="optional folder whose files take precedence over the root")
    args = ap.parse_args()
    Handler.root = Path(args.root).resolve()
    Handler.overlay = Path(args.overlay).resolve() if args.overlay else None
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"Serving {Handler.root} on http://{args.host}:{args.port}/"
          + (f" (overlay {Handler.overlay})" if Handler.overlay else ""), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
