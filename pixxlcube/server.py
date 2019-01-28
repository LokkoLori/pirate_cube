from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import signal
import subprocess
import time

PORT = 8088

def startcmd(path):
    return "/usr/bin/python {}/{}".format(os.path.dirname(os.path.abspath(__file__)), path)

procs = (
    ("/logo", startcmd("../plasma/logodemo.py")),
    ("/grandpix", startcmd("../plasma/gpdemo.py")),
    ("/plasma", startcmd("../plasma/plasma.py")),
    ("/pacube", startcmd("../pacube.py")),
    ("/gravitydot", startcmd("../gravitydot.py")),
    ("/stop", "echo pixxlcube stoped")
)

apro = None

class PiXXLCubeServer(BaseHTTPRequestHandler):

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def pixxlresponse(self, data={}):
        if self.path == "/favicon.ico":
            return ""

        global apro
        if self.path!="/" and apro:
            os.killpg(os.getpgid(apro.pid), signal.SIGTERM)
            apro = None
            time.sleep(2)

        for proc in procs:
            if self.path == proc[0]:
                apro = subprocess.Popen(proc[1], stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

        links = ""
        for proc in procs:
            links += "<a href='{0}'>{0}</a><br/>\n".format(proc[0])
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