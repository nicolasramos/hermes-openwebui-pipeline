#!/usr/bin/env python3
"""Servidor estático de imágenes generadas por Hermes.

Sirve ~/.hermes/cache/images con:
  GET /<file>           -> imagen inline (para markdown del chat)
  GET /download/<file>  -> descarga con Content-Disposition: attachment
  GET /                 -> listing (lo usa el pipe hermes_trace)

Arranque: python3 images_server.py  (puerto 8787, 0.0.0.0)
"""

import http.server
import mimetypes
import os
import urllib.parse

DIR = os.path.expanduser("~/.hermes/cache/images")
PORT = 8787


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/download/"):
            name = os.path.basename(parsed.path[len("/download/"):])
            path = os.path.join(DIR, name)
            if os.path.isfile(path):
                ctype, _ = mimetypes.guess_type(name)
                ctype = ctype or "application/octet-stream"
                size = os.path.getsize(path)
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Disposition", 'attachment; filename="%s"' % name)
                self.send_header("Content-Length", str(size))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404, "File not found")
            return
        super().do_GET()


if __name__ == "__main__":
    os.makedirs(DIR, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("Images server on :%d serving %s" % (PORT, DIR))
    server.serve_forever()
