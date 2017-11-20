import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

import application
import handlers
import settings
import beacon
#import template


define("port", default=4000, help="run on the given port", type=int)
define("develop", default=False, help="Run in develop environment", type=bool)

# Setup the Tornado Application
tornado_settings = {"debug": False,
            "cookie_secret": settings.cookie_secret,
            "login_url": "/login",
            "google_oauth": {
                "key": settings.google_key,
                "secret": settings.google_secret
            },
            "elixir_oauth": {
                "id": settings.elixir["id"],
                "secret": settings.elixir["secret"],
                "redirect_uri": settings.elixir["redirectUri"],
            },
            "contact_person": 'mats.dahlberg@scilifelab.se',
            "redirect_uri": settings.redirect_uri,
            "xsrf_cookies": True,
            "template_path": "templates/",
        }

class Application(tornado.web.Application):
    def __init__(self, settings):
        self.declared_handlers = [
            ## Static handlers
            (r"/static/(.*)",                                                        tornado.web.StaticFileHandler,
                                                                                         {"path": "static/"}),
            (r'/(favicon.ico)',                                                      tornado.web.StaticFileHandler,
                                                                                         {"path": "static/img/"}),
            (r"/release/(?P<dataset>[^\/]+)/(?P<hash>[^\/]+)/(?P<file>[^\/]+)",      handlers.TemporaryStaticNginxFileHandler,
                                                                                         {"path": "/release-files/"}),
            (r"/release/(?P<dataset>[^\/]+)/(?P<file>[^\/]+)",                       handlers.AuthorizedStaticNginxFileHandler,
                                                                                         {"path": "/release-files/"}),
            ## Authentication
            ("/login",                                                               handlers.LoginHandler),
            ("/logout",                                                              handlers.LogoutHandler),
            ("/elixir/login",                                                        handlers.ElixirLoginHandler),
            ("/elixir/logout",                                                       handlers.ElixirLogoutHandler),
            ## API Methods
            ("/api/countries",                                                       application.CountryList),
            ("/api/users/me",                                                        application.GetUser),
            ### Dataset Api
            ("/api/datasets",                                                        application.ListDatasets),
            ("/api/datasets/(?P<dataset>[^\/]+)",                                    application.GetDataset),
            ("/api/datasets/(?P<dataset>[^\/]+)/log/(?P<event>[^\/]+)/(?P<target>[^\/]+)", application.LogEvent),
            ("/api/datasets/(?P<dataset>[^\/]+)/logo",                               application.ServeLogo),
            ("/api/datasets/(?P<dataset>[^\/]+)/files",                              application.DatasetFiles),
            ("/api/datasets/(?P<dataset>[^\/]+)/collection",                         application.Collection),
            ("/api/datasets/(?P<dataset>[^\/]+)/users_current",                      application.DatasetUsersCurrent),
            ("/api/datasets/(?P<dataset>[^\/]+)/users_pending",                      application.DatasetUsersPending),
            ("/api/datasets/(?P<dataset>[^\/]+)/temporary_link",                     application.GenerateTemporaryLink),
            ("/api/datasets/(?P<dataset>[^\/]+)/users/(?P<email>[^\/]+)/request",    application.RequestAccess),
            ("/api/datasets/(?P<dataset>[^\/]+)/users/(?P<email>[^\/]+)/approve",    application.ApproveUser),
            ("/api/datasets/(?P<dataset>[^\/]+)/users/(?P<email>[^\/]+)/revoke",     application.RevokeUser),
            ("/api/datasets/(?P<dataset>[^\/]+)/versions",                           application.ListDatasetVersions),
            ("/api/datasets/(?P<dataset>[^\/]+)/versions/(?P<version>[^\/]+)",       application.GetDataset),
            ("/api/datasets/(?P<dataset>[^\/]+)/versions/(?P<version>[^\/]+)/files", application.DatasetFiles),
            ("/api/datasets/(?P<dataset>[^\/]+)/versions/(?P<version>[^\/]+)/temporary_link", application.GenerateTemporaryLink),
            ### Beacon API
            ("/api/beacon/query",                                                    beacon.Query),
            ("/api/beacon/info",                                                     beacon.Info),
            # # # # # Legacy beacon URIs # # # # #
            ("/query",                                                               beacon.Query),
            ("/info",                                                                tornado.web.RedirectHandler,
                                                                                         {"url": "/api/beacon/info"}),
            ## Catch all
            ("/api/.*",                                                              tornado.web.ErrorHandler,
                                                                                         {"status_code": 404} ),
            (r'().*',                                                                  tornado.web.StaticFileHandler,
                                                                                         {"path": "templates/",  "default_filename": "index.html"}),
        ]

        # google oauth key
        self.oauth_key = tornado_settings["google_oauth"]["key"]

        # Setup the Tornado Application
        tornado.web.Application.__init__(self, self.declared_handlers, **settings)

if __name__ == '__main__':
    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()

    if options.develop:
        tornado_settings['debug'] = True
        tornado_settings['develop'] = True
        logging.getLogger().setLevel(logging.DEBUG)

    # Instantiate Application
    application = Application(tornado_settings)
    application.listen(options.port)

    # Start HTTP Server
    http_server = tornado.httpserver.HTTPServer(application)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Start the IOLoop
    ioloop.start()
