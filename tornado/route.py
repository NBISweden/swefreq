import tornado.autoreload
import tornado.httpserver
import tornado.ioloop
import tornado.web
import auth
import os
import application
from tornado import template
from tornado.options import define, options
import logging
import base64
import uuid
import secrets

tornado.log.enable_pretty_logging()
logging.getLogger().setLevel(logging.DEBUG)

redirect_uri = "https://smog29-100.cloud.uppmax.uu.se:8080/login"

# Setup the Tornado Application
cookie_secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
settings = {"debug": True,
            "cookie_secret": cookie_secret,
            "login_url": "/login",
            "google_oauth": {
        "key": secrets.googleKey,
        "secret": secrets.googleSecret
        },
            "contact_person": 'mats.dahlberg@scilifelab.se',
            "redirect_uri": redirect_uri
            }

class Application(tornado.web.Application):
    def __init__(self, settings):
        handlers = [
            (r"/", application.home),
            (r"/static/(home.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(.*)", auth.SafeStaticFileHandler, {"path": "static/"}),
            (r"/javascript/(.*)", tornado.web.StaticFileHandler, {"path": "javascript/"}),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": "static/"}),
            ("/login", auth.LoginHandler),
            ("/logout", auth.LogoutHandler),
            ("/logEvent/(?P<sEvent>[^\/]+)", application.logEvent),
            ("/getUser", application.getUser),
            ("/getApprovedUsers", application.getApprovedUsers),
            ("/approveUser/(?P<sEmail>[^\/]+)", application.approveUser),
            ("/query/", application.query),
            ("/deleteUser/(?P<sEmail>[^\/]+)", application.deleteUser),
            ("/denyUser/(?P<sEmail>[^\/]+)", application.denyUser),
            ("/getOutsandingRequests", application.getOutsandingRequests),
            ("/requestAccess", application.requestAccess),
            ("/unauthorized", auth.UnAuthorizedHandler),
            (r'.*', auth.BaseHandler),
        ]

        self.declared_handlers = handlers

        # google oauth key
        self.oauth_key = settings["google_oauth"]["key"]

        # Setup the Tornado Application
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    # Instantiate Application
    application = Application(settings)

    ssl_options = {
        'certfile': os.path.join('cert/server.crt'),
        'keyfile': os.path.join('cert/myserver.key')
        }

    # Start HTTP Server
    http_server = tornado.httpserver.HTTPServer(application, ssl_options = ssl_options)
    http_server.listen(8080)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Start the IOLoop
    ioloop.start()
