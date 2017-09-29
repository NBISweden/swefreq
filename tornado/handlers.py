import logging
import peewee
import tornado.auth
import tornado.web
import os.path

import db


class BaseHandler(tornado.web.RequestHandler):
    """Base Handler. Handlers should not inherit from this
    class directly but from either SafeHandler or UnsafeHandler
    to make security status explicit.
    """
    def get(self):
        """ The GET method on this handler will be overwritten by all other handler.
        As it is the default handler used to match any request that is not mapped
        in the main app, a 404 error will be raised in that case (because the get method
        won't be overwritten in that case)
        """
        raise tornado.web.HTTPError(404, reason='Page not found')

    def prepare(self):
        ## Make sure we have the xsrf_token
        self.xsrf_token
        db.database.connect()

    def on_finish(self):
        if not db.database.is_closed():
            db.database.close()

    def get_current_user(self):
        email = self.get_secure_cookie('email')
        name  = self.get_secure_cookie('user')

        # Fix ridiculous bug with quotation marks showing on the web
        if name and (name[0] == '"') and (name[-1] == '"'):
            name = user[1:-1]

        if email:
            try:
                return db.User.select().where( db.User.email == email ).get()
            except peewee.DoesNotExist:
                ## Not saved in the database yet
                return db.User(email = email.decode('utf-8'),
                               name  = name.decode('utf-8'))
        else:
            return None

    def write_error(self, status_code, **kwargs):
        """ Overwrites write_error method to have custom error pages.
        http://tornado.readthedocs.org/en/latest/web.html#tornado.web.RequestHandler.write_error
        """
        reason = 'Page not found'
        logging.info("Error do something here again")


class SafeHandler(BaseHandler):
    """ All handlers that need authentication and authorization should inherit
    from this class.
    """
    def prepare(self):
        """This method is called before any other method.
        Having the decorator @tornado.web.authenticated here implies that all
        the Handlers that inherit from this one are going to require
        authentication in all their methods.
        """
        if not self.current_user:
            self.send_error(status_code=403)

class AuthorizedHandler(SafeHandler):
    def prepare(self):
        super(AuthorizedHandler, self).prepare()

        if self._finished:
            return

        kwargs = self.path_kwargs
        if not kwargs['dataset']:
            self.send_error(status_code=403)
        if not self.current_user.has_access( db.get_dataset(kwargs['dataset']) ):
            self.send_error(status_code=403)

class AdminHandler(SafeHandler):
    def prepare(self):
        super(AdminHandler, self).prepare()

        if self._finished:
            return

        kwargs = self.path_kwargs
        if not kwargs['dataset']:
            self.send_error(status_code=403)
        if not self.current_user.is_admin( db.get_dataset(kwargs['dataset']) ):
            self.send_error(status_code=403)

class UnsafeHandler(BaseHandler):
    pass

class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    """
    See http://www.tornadoweb.org/en/stable/auth.html#google for documentation
    on this. Here I have copied the example more or less verbatim.
    """
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("code", False):
            logging.debug("Requesting user token")
            user_token = yield self.get_authenticated_user(
                redirect_uri=self.application.settings['redirect_uri'],
                code=self.get_argument('code'))

            logging.debug("Requesting user info")
            user = yield self.oauth2_request(
                    "https://www.googleapis.com/plus/v1/people/me",
                    access_token=user_token["access_token"])

            self.set_secure_cookie('user', user["displayName"])
            self.set_secure_cookie('access_token', user_token["access_token"])

            # There can be several emails registered for a user.
            for email in user["emails"]:
                if email.get('type', '') == 'account':
                    self.set_secure_cookie('email', email['value'])
                    break
            else:
                # No account email, just take the first one
                self.set_secure_cookie('email', user['emails'][0]['value'])

            url = self.get_secure_cookie("login_redirect")
            self.clear_cookie("login_redirect")
            if url is None:
                url = '/'
            self.redirect(url)

        else:
            logging.debug("Redirecting to google for login")
            self.set_secure_cookie('login_redirect', self.get_argument("next", '/'), 1)
            self.authorize_redirect(
                        redirect_uri=self.application.settings['redirect_uri'],
                        client_id=self.application.oauth_key,
                        scope=['profile', 'email'],
                        response_type='code',
                        extra_params={'approval_prompt': 'auto'})

class LogoutHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    def get(self):
        def handle_request(response):
            if response.error:
                logging.info("Error, failed in logout")
                logging.info(response.error)
            else:
                logging.info("User logged out")

        sAccessToken = self.get_secure_cookie("access_token")
        sLogoutUrl = "https://accounts.google.com/o/oauth2/revoke?token=" + str(sAccessToken)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(sLogoutUrl, handle_request)

        self.clear_cookie("access_token")
        self.clear_cookie("login_redirect")
        self.clear_cookie("user")
        self.clear_cookie("email")

        redirect = self.get_argument("next", '/')
        self.redirect(redirect)

class SafeStaticFileHandler(tornado.web.StaticFileHandler, SafeHandler):
    """ Serve static files for logged in users
    """
    pass

class AuthorizedStaticNginxFileHanlder(AuthorizedHandler):
    """ Serve static files for authenticated users from the nginx frontend

    Requires a ``path`` argument in constructor which should be the root of
    the nginx frontend where the files can be found. Then configure the nginx
    frontend something like this

        location <path> {
            internal;
            alias <location of files>;
        }
    """
    def initialize(self, path):
        if not path.startswith("/"):
            path = "/" + path
        self.root = path

    def get(self, dataset, file):
        abspath = os.path.abspath(os.path.join(self.root, file))
        self.set_header("X-Accel-Redirect", abspath)
        self.set_header("Content-Disposition", "attachment")
        self.finish()


class AngularTemplate(UnsafeHandler):
    def initialize(self, path):
        self.root = path

    def get(self, path, *args, **kwargs):
        self.render(self.root + path)
