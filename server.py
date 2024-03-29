import json
import time
import threading
from urllib.parse import urlparse, parse_qs
import base64
import signal

#from http.server import HTTPServer, BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading

HTTP_SERVER_PORT = 8899

def now() -> int:
    return int(time.time() * 1000)

exit_flag: bool = False
def signal_handler(sig, frame):
    global exit_flag
    exit_flag = True
    print('Ctrl+C pressed!')
    pass

signal.signal(signal.SIGINT, signal_handler)


class RemoteDesktop:
    def __init__(self):
        self.screenshot = None
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
                        self.wfile.write(bytes())
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

web_server: ThreadingHTTPServer = None
def web_server_thread_function():
    global web_server
    web_server = ThreadingHTTPServer(('0.0.0.0', HTTP_SERVER_PORT), HTTPRequestHandler)
    web_server.serve_forever()
    print(f'web server listening 0.0.0.0:{HTTP_SERVER_PORT}...')
    try:
        web_server.serve_forever()
    except Exception as e:
        print(f'signal server stopped')
        print(e.args[0])
    web_server.server_close()
    print(f'signal server stopped')

print('init')
web_server_thread = threading.Thread(target=web_server_thread_function, args=())
web_server_thread.start()

while True:
    if exit_flag:
        break
    time.sleep(0.1)

web_server.shutdown()
