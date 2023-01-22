import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64

HTTP_SERVER_PORT = 80

def now() -> int:
    return int(time.time() * 1000)

class RemoteDesktop:
    def __init__(self):
        self.screenshot: None
        self.commands = []
rd: RemoteDesktop = RemoteDesktop()

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args):
        BaseHTTPRequestHandler.__init__(self, *args)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")
        BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            parsed_query = parse_qs(parsed_path.query)
            response = {}
            if parsed_path.path:
                if parsed_path.path == '/':
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    f = open("./index.html", "r")
                    self.html = f.read()
                    f.close()
                    self.wfile.write(self.html.encode())
                    return
                if '/screenshot' in parsed_path.path:
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.end_headers()
                    if rd.screenshot:
                        self.wfile.write(rd.screenshot)
                    else:
                        self.wfile.write('')
                if '/control' in parsed_path.path:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(rd.commands, separators=(',', ':')).encode())
                    rd.commands = []
        except Exception as e:
            print('do_GET() exception: ', e.args[0])

    def do_POST(self):
        try:
            parsed_path = urlparse(self.path)
            parsed_query = parse_qs(parsed_path.query)
            response = {}
            content_len = int(self.headers.get('Content-Length'))
            if content_len > 0:
                post_body_text = self.rfile.read(content_len)
                post_body_json = json.loads(post_body_text)
                #print(post_body_json['type'])
                if '/screenshot' in parsed_path.path:
                    if post_body_json['type'] == 'screenshot':
                        payload: str = post_body_json['payload']
                        rd.screenshot = base64.b64decode(payload.encode('utf-8'))
                if '/control' in parsed_path.path:
                    rd.commands.append(post_body_json)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response, separators=(',', ':')).encode())
        except Exception as e:
            print('do_POST() exception: ', e.args[0])
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'error': e.args[0]
            }
            self.wfile.write(json.dumps(response, separators=(',', ':')).encode())

    def log_message(self, format, *args):
        return

def web_server_thread_function(rd):
    httpd = HTTPServer(('', HTTP_SERVER_PORT), HTTPRequestHandler)
    httpd.serve_forever()

web_server_thread = threading.Thread(target=web_server_thread_function, args=(rd,))
web_server_thread.start()

