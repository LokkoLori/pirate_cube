from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import signal
import subprocess
import time

#This is a prototype server, a very basic solution "You know nothing John Snow"

PORT = 8088

def startcmd(path):
    return "/usr/bin/python {}/{}".format(os.path.dirname(os.path.abspath(__file__)), path)

apps = (
    ("logo", startcmd("../plasma/logodemo.py")),
    ("grandpix", startcmd("../plasma/gpdemo.py")),
    ("plasma", startcmd("../plasma/plasma.py")),
    ("pacube", startcmd("../pacube/pacube.py")),
    ("gravitydot", startcmd("../gravitydot.py")),
    ("stop", 'echo "pixxlcube stopped"')
)

apro = None

def start_app(cmd):
    global apro
    if apro:
        os.killpg(os.getpgid(apro.pid), signal.SIGTERM)
        apro = None
        time.sleep(2)
    print cmd
    apro = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

class PiXXLCubeServer(BaseHTTPRequestHandler):

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def pixxlresponse(self, data={}):
        if self.path == "/favicon.ico":
            return ""

        links = ""
        for appd in apps:
            if "/"+appd[0] == self.path:
                start_app(appd[1])
            links += "<a href='/{0}'>{0}</a><br/>\n".format(appd[0])

        return "<html><head><style>a {{font-size: 5em}}</style></head><body><h1>Say hello to my PiXXL Cube!</h1><br/>{}</body></html>".format(links)

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self.pixxlresponse())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length = int(content_length[0]) if content_length else 0
        data = self.rfile.read(length).split('&')
        self.wfile.write(self.pixxlresponse(data))

def start_server():
    httpd = HTTPServer(("", PORT), PiXXLCubeServer)
    print "starting pixxlcube server at port", PORT
    httpd.serve_forever()

def stop_server():
    global apro
    if apro:
        os.killpg(os.getpgid(apro.pid), signal.SIGTERM)

import atexit
atexit.register(stop_server)

if __name__ == "__main__":
    start_server()