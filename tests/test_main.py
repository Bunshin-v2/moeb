import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HTML = "<html><body><footer>Local Footer</footer></body></html>"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())


def start_server(server: HTTPServer) -> None:
    server.serve_forever()


def test_main_output_files(tmp_path):
    server = HTTPServer(("localhost", 0), Handler)
    thread = threading.Thread(target=start_server, args=(server,), daemon=True)
    thread.start()
    url = f"http://{server.server_address[0]}:{server.server_address[1]}"
    try:
        result = subprocess.run(
            [sys.executable, "src/main.py", "--urls", url, "--output-dir", str(tmp_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        domain = urlparse(url).netloc.replace(".", "_") + ".txt"
        outfile = tmp_path / domain
        assert outfile.exists()
        assert "Local Footer" in outfile.read_text()
        assert f"Saved footer for {url}" in result.stdout
    finally:
        server.shutdown()
        thread.join()

