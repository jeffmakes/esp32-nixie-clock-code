import ure as re
import picoweb
import logging

class WebServer:
    def __init__(self, address, port, debug=-1):
        logging.basicConfig(level=logging.DEBUG)

        self.ROUTES = [
            # You can specify exact URI string matches...
            ("/", self.index),
            ("/squares", self.squares),
            ("/file", lambda req, resp: (yield from self.app.sendfile(resp, "example_webapp.py"))),
            # ... or match using a regex, the match result available as req.url_match
            # for match group extraction in your view.
            (re.compile("^/iam/(.+)"), self.hello),
        ]

        print("example_webapp init")
        #self.app = picoweb.WebApp(__name__, self.ROUTES)
        self.app = picoweb.WebApp("__main__", routes=self.ROUTES)

        # debug values:
        # -1 disable all logging
        # 0 (False) normal logging: requests and errors
        # 1 (True) debug logging
        # 2 extra debug logging
        self.app.run(host=address, port=port, debug=debug)

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

