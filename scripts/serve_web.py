#!/usr/bin/env python3
"""Local preview of web/ with Vercel's URL rules.

Production serves web/ with cleanUrls + trailingSlash:false, so the site's
internal links are extensionless (`/moratoriums`, `/blog`). Python's stock
http.server 404s on those; this shim resolves `/x` -> `x.html` and
`/dir` -> `dir/index.html`, and serves 404.html for misses, so a local click
path matches what a resident sees on aigridwatch.com.

    python3 scripts/serve_web.py [port]      # default 8777
"""
import http.server
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "web"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def translate_path(self, path):
        full = pathlib.Path(super().translate_path(path))
        bare = path.split("?", 1)[0].split("#", 1)[0]
        if full.is_file() or bare.endswith("/"):
            return str(full)
        if full.with_suffix(".html").is_file():
            return str(full.with_suffix(".html"))
        if (full / "index.html").is_file():
            return str(full / "index.html")
        nf = ROOT / "404.html"
        return str(nf) if nf.is_file() else str(full)

    def send_head(self):
        # A miss resolves to 404.html above; make the status say so too.
        if (self.translate_path(self.path) == str(ROOT / "404.html")
                and not self.path.startswith("/404")):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            return open(ROOT / "404.html", "rb")
        return super().send_head()

    def log_message(self, fmt, *args):  # quieter console
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    print(f"serving {ROOT} on http://localhost:{port} (clean URLs)")
    http.server.ThreadingHTTPServer(("", port), Handler).serve_forever()
