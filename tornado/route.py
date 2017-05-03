import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

import application
import handlers
import secrets

define("port", default=4000, help="run on the given port", type=int)

tornado.log.enable_pretty_logging()
logging.getLogger().setLevel(logging.DEBUG)

redirect_uri = secrets.redirect_uri

# Setup the Tornado Application
settings = {"debug": True,
            "cookie_secret": secrets.cookie_secret,
            "login_url": "/login",
            "google_oauth": {
                "key": secrets.google_key,
                "secret": secrets.google_secret
            },
            "contact_person": 'mats.dahlberg@scilifelab.se',
            "redirect_uri": redirect_uri
        }

class Application(tornado.web.Application):
    def __init__(self, settings):
        self.declared_handlers = [
            (r"/", application.home),
            (r"/static/(home.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(dataBeacon.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(privacyPolicy.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(not_authorized.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(about.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(terms.html)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r"/static/(.*)", handlers.SafeStaticFileHandler, {"path": "static/"}),
            (r"/release/(.*)", handlers.AuthorizedStaticFileHandler, { "path": "release/"}),
            (r"/javascript/(.*)", tornado.web.StaticFileHandler, {"path": "javascript/"}),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": "static/"}),
            ("/login", handlers.LoginHandler),
            ("/logout", handlers.LogoutHandler),
            ("/logEvent/(?P<sEvent>[^\/]+)", application.logEvent),
            ("/getUser", application.getUser),
            ("/getApprovedUsers", application.getApprovedUsers),
            ("/approveUser/(?P<sEmail>[^\/]+)", application.approveUser),
            ("/query", application.query),
            ("/info", application.info),
            ("/revokeUser/(?P<sEmail>[^\/]+)", application.revokeUser),
            ("/getOutstandingRequests", application.getOutstandingRequests),
            ("/requestAccess", application.requestAccess),
            ("/country_list", application.country_list),
            (r'.*', handlers.BaseHandler),
        ]

        # google oauth key
        self.oauth_key = settings["google_oauth"]["key"]

        # Setup the Tornado Application
        tornado.web.Application.__init__(self, self.declared_handlers, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    # Instantiate Application
    application = Application(settings)
    application.listen(options.port)

    # Start HTTP Server
    http_server = tornado.httpserver.HTTPServer(application)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Start the IOLoop
    ioloop.start()
