import logging
import peewee
import tornado.auth
import tornado.web
import os.path
import datetime

import db


class BaseHandler(tornado.web.RequestHandler):
    """Base Handler. Handlers should not inherit from this
    class directly but from either SafeHandler or UnsafeHandler
    to make security status explicit.
    """
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
            logging.debug("No current user: Send error 403")
            self.send_error(status_code=403)

class AuthorizedHandler(SafeHandler):
    def prepare(self):
        logging.debug("Checking if user is authorized")
        super().prepare()

        if self._finished:
            return

        kwargs = self.path_kwargs
        if not kwargs['dataset']:
            logging.debug("No dataset: Send error 403")
            self.send_error(status_code=403)
        if not self.current_user.has_access( db.get_dataset(kwargs['dataset']) ):
            logging.debug("No user access: Send error 403")
            self.send_error(status_code=403)
        logging.debug("User is authorized")

class AdminHandler(SafeHandler):
    def prepare(self):
        super().prepare()

        if self._finished:
            return

        kwargs = self.path_kwargs
        if not kwargs['dataset']:
            logging.debug("No dataset: Send error 403")
            self.send_error(status_code=403)
        if not self.current_user.is_admin( db.get_dataset(kwargs['dataset']) ):
            logging.debug("No user admin: Send error 403")
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


class BaseStaticNginxFileHandler(UnsafeHandler):
    """Serve static files for users from the nginx frontend

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

    def get(self, dataset, file, user=None):
        logging.debug("Want to download dataset {} ({})".format(dataset, file))

        if not user:
            user = self.current_user

        dbfile = (db.DatasetFile
                  .select()
                  .where(db.DatasetFile.name == file)
                  .get())
        db.UserDownloadLog.create(
                user = user,
                dataset_file = dbfile
            )

        abspath = os.path.abspath(os.path.join(self.root, file))
        self.set_header("X-Accel-Redirect", abspath)
        self.set_header("Content-Disposition", "attachment")

        logging.debug("Setting X-Accel-Redirect to {}".format(abspath))
        self.finish()


class AuthorizedStaticNginxFileHandler(AuthorizedHandler, BaseStaticNginxFileHandler):
    """Serve static files for authenticated users from the nginx frontend

    Requires a ``path`` argument in constructor which should be the root of
    the nginx frontend where the files can be found. Then configure the nginx
    frontend something like this

        location <path> {
            internal;
            alias <location of files>;
        }
    """
    pass


class EphemeralStaticNginxFileHandler(BaseStaticNginxFileHandler):
    def get_user_from_hash(self, hash):
        logging.debug("Getting the ephemeral user")
        return (db.User
                   .select(db.User)
                   .join(db.Linkhash)
                   .where(db.Linkhash.hash == hash)
               ).get()

    def get(self, dataset, hash, file):
        logging.debug("Want to download hash {} ({})".format(hash, file))
        linkhash = (db.Linkhash
                        .select()
                        .join(db.DatasetVersion)
                        .join(db.DatasetFile)
                        .where(db.Linkhash.hash       == hash,
                               db.Linkhash.expires_on >  datetime.datetime.now(),
                               db.DatasetFile.name    == file))
        if linkhash.count() > 0:
            logging.debug("Linkhash valid")
            user = self.get_user_from_hash(hash)
            super().get(dataset, file, user)
        else:
            logging.debug("Linkhash invalid")
            self.send_error(status_code=403)


class AngularTemplate(UnsafeHandler):
    def initialize(self, path):
        self.root = path

    def get(self, path):
        self.render(self.root + path)
