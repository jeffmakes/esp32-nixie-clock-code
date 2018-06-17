import ure as re
import picoweb
import logging
import gc


class WebServer:
    def __init__(self, address, port, debug=-1):
        # debug values:
        # -1 disable all logging
        # 0 (False) normal logging: requests and errors
        # 1 (True) debug logging
        # 2 extra debug logging
        self.debug = debug
        logging.basicConfig(level=logging.DEBUG)
        self.address = address
        self.port = port
        self.ROUTES = [
            # You can specify exact URI string matches...
            ("/", self.index),
            ("/ncsi.txt", self.ncsi),                   # microsoft
            ("/connecttest.txt", self.connecttest),     # microsoft
            ("/redirect", self.redirect),               # microsoft
            ("/gen_204", self.redirect),                # android
            ("/generate_204", self.redirect),       # android
            ("/hotspot-detect.html", self.redirect),    # apple
            ("/squares", self.squares),
            ("/file", lambda req, resp: (yield from self.app.sendfile(resp, "captiveportal.py"))),
            # ... or match using a regex, the match result available as req.url_match
            # for match group extraction in your view.
            (re.compile("^/iam/(.+)"), self.hello),
        ]

        self.app = picoweb.WebApp("__main__", routes=self.ROUTES)

    def run(self):
        self.app.run(host=self.address, port=self.port, debug=self.debug)

    def index(self, req, resp):
        # You can construct an HTTP response completely yourself, having
        # a full control of headers sent...
        yield from resp.awrite("HTTP/1.0 200 OK\r\n")
        yield from resp.awrite("Content-Type: text/html\r\n")
        yield from resp.awrite("\r\n")
        yield from resp.awrite("I can show you a table of <a href='squares'>squares</a>.<br/>")
        yield from resp.awrite("Or my <a href='file'>source</a>.")

    def squares(self, req, resp):
        # Or can use a convenience function start_response() (see its source for
        # extra params it takes).
        yield from picoweb.start_response(resp)
        yield from app.render_template(resp, "squares.tpl", (req,))

    def hello(self, req, resp):
        yield from picoweb.start_response(resp)
        # Here's how you extract matched groups from a regex URI match
        yield from resp.awrite("Hello " + req.url_match.group(1))

    def ncsi(self, request, response):
        yield from response.awrite("HTTP/1.1 200 OK\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("\r\n")
        yield from response.awrite("Microsoft NCSI\r\n")
        yield from response.awrite("\r\n")
        gc.collect()

    def connecttest(self, request, response):
        yield from response.awrite("HTTP/1.1 200 OK\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("\r\n")
        yield from response.awrite("Microsoft Connect Test\r\n")
        yield from response.awrite("\r\n")
        gc.collect()

    def redirect(self, request, response):
        yield from response.awrite("HTTP/1.1 302 Found\r\n")
        yield from response.awrite("Location: http://login.com\r\n")
        yield from response.awrite("\r\n")
        gc.collect()

    def generate_204(self, request, response):
        yield from response.awrite("HTTP/1.1 200 OK\r\n")
        yield from response.awrite("Content-Type: text/html\r\n")
        yield from response.awrite("dummy text\r\n")
        yield from response.awrite("\r\n")
        gc.collect()

        
