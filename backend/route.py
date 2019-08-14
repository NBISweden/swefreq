import logging
import sys

import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import tornado.web

import application
import handlers
import auth
import settings as swefreq_settings

from modules.browser.route import routes as browser_routes

define("port", default=4000, help="run on the given port", type=int)
define("develop", default=False, help="Run in develop environment", type=bool)

# Setup the Tornado Application
tornado_settings = {"debug": False,
                    "cookie_secret": swefreq_settings.cookie_secret,
                    "login_url": "/login",
                    "elixir_oauth": {
                        "id": swefreq_settings.elixir["id"],
                        "secret": swefreq_settings.elixir["secret"],
                        "redirect_uri": swefreq_settings.elixir["redirectUri"],
                    },
                    "xsrf_cookies": True,
                    "template_path": "templates/"}


class Application(tornado.web.Application):
    def __init__(self, settings):
        self.declared_handlers = [
            # Static handlers
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": "static/img/"}),
            (r"/release/(?P<dataset>[^\/]+)/versions/(?P<ds_version>[^/]+)/(?P<hash_value>[^\/]+)/(?P<file>[^\/]+)",
             handlers.TemporaryStaticNginxFileHandler,
             {"path": "/release-files/"}),
            (r"/release/(?P<dataset>[^\/]+)/versions/(?P<ds_version>[^/]+)/(?P<file>[^\/]+)",
             handlers.AuthorizedStaticNginxFileHandler,
             {"path": "/release-files/"}),
            # Authentication
            (r"/logout", auth.ElixirLogoutHandler),
            (r"/elixir/login", auth.ElixirLoginHandler),
            (r"/elixir/logout", auth.ElixirLogoutHandler),
            # API Methods
            (r"/api/countries", application.CountryList),
            (r"/api/users/me", application.GetUser),
            (r"/api/users/datasets", application.UserDatasetAccess),
            (r"/api/users/sftp_access", application.SFTPAccess),
            (r"/api/schema", application.GetSchema),
            # Dataset Api
            (r"/api/dataset", application.ListDatasets),
            (r"/api/dataset/(?P<dataset>[^\/]+)", application.GetDataset),
            (r"/api/dataset/(?P<dataset>[^\/]+)/log/(?P<event>[^\/]+)/(?P<target>[^\/]+)", application.LogEvent),
            (r"/api/dataset/(?P<dataset>[^\/]+)/logo", application.ServeLogo),
            (r"/api/dataset/(?P<dataset>[^\/]+)/(?:versions/(?P<ds_version>[^/]+)/)?files", application.DatasetFiles),
            (r"/api/dataset/(?P<dataset>[^\/]+)/(?:versions/(?P<ds_version>[^/]+)/)?collection", application.Collection),
            (r"/api/dataset/(?P<dataset>[^\/]+)/users_current", application.DatasetUsersCurrent),
            (r"/api/dataset/(?P<dataset>[^\/]+)/users_pending", application.DatasetUsersPending),
            (r"/api/dataset/(?P<dataset>[^\/]+)/(?:versions/(?P<ds_version>[^/]+)/)?temporary_link", application.GenerateTemporaryLink),
            (r"/api/dataset/(?P<dataset>[^\/]+)/users/[^\/]+/request", application.RequestAccess),
            (r"/api/dataset/(?P<dataset>[^\/]+)/users/(?P<email>[^\/]+)/approve", application.ApproveUser),
            (r"/api/dataset/(?P<dataset>[^\/]+)/users/(?P<email>[^\/]+)/revoke", application.RevokeUser),
            (r"/api/dataset/(?P<dataset>[^\/]+)/versions", application.ListDatasetVersions),
            (r"/api/dataset/(?P<dataset>[^\/]+)/versions/(?P<version>[^\/]+)", application.GetDataset),
            (r"/api/dataset/(?P<dataset>[^\/]+)/versions/(?P<version>[^\/]+)/files", application.DatasetFiles),
            (r"/api/dataset/(?P<dataset>[^\/]+)/versions/(?P<version>[^\/]+)/temporary_link", application.GenerateTemporaryLink),
        ]

        # Adding module handlers
        self.declared_handlers += browser_routes

        # Adding Catch all handlers
        self.declared_handlers += [
            (r"/api/.*", tornado.web.ErrorHandler, {"status_code": 404}),
            (r'().*', tornado.web.StaticFileHandler, {"path": "static/templates/", "default_filename": "index.html"}),
            ]

        # Adding developer login handler
        if settings.get('develop', False):
            self.declared_handlers.insert(-1, ("/developer/login", auth.DeveloperLoginHandler))
            self.declared_handlers.insert(-1, ("/developer/quit", application.QuitHandler))

        # Setup the Tornado Application
        tornado.web.Application.__init__(self, self.declared_handlers, **settings)


if __name__ == '__main__':
    # Make sure that the extra option to `settings` isn't upsetting tornado
    if '--settings_file' in sys.argv:
        flag_index = sys.argv.index('--settings_file')
        # first remove flag, then argument
        del sys.argv[flag_index]
        del sys.argv[flag_index]

    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()

    if options.develop:
        tornado_settings['debug'] = True
        tornado_settings['develop'] = True
        logging.getLogger().setLevel(logging.DEBUG)

    # Instantiate Application
    tornado_application = Application(tornado_settings)
    tornado_application.listen(options.port, xheaders=True)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Start the IOLoop
    ioloop.start()
