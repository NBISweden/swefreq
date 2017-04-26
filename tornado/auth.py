import tornado.web
import tornado.auth
import tornado.template as template
import json
import requests
import secrets
import logging
import secrets
import torndb as database

db = database.Connection(host = secrets.mysql_host,
                         database = secrets.mysql_schema,
                         user = secrets.mysql_user,
                         password = secrets.mysql_passwd)

def isAuthorized(email):
    tRes = db.query("""select username
    from swefreq.users where email = '%s'
    and full_user""" % (email))

    if len(tRes)>0:
        return True, tRes[0]
    else:
        return False, None

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

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_email(self):
        return self.get_secure_cookie("email")

    def get_current_token(self):
        return self.get_secure_cookie("access_token")

    def get_current_user_name(self):
        # Fix ridiculous bug with quotation marks showing on the web
        user = self.get_current_user()
        if user:
            if (user[0] == '"') and (user[-1] == '"'):
                return user[1:-1]
            else:
                return user
        return user

    def is_admin(self):
        email = self.get_current_email()
        tRes = db.query("""select full_user from swefreq.users where
                              email='%s' and swefreq_admin""" % email)
        lAdmin = True if len(tRes) == 1 else False
        return lAdmin

    def is_authorized(self):
        email = self.get_current_email()
        tRes = db.query("""select full_user from swefreq.users where
                              email='%s' and full_user""" % email)
        lAdmin = True if len(tRes) == 1 else False
        return lAdmin

    def write_error(self, status_code, **kwargs):
        """ Overwrites write_error method to have custom error pages.
        http://tornado.readthedocs.org/en/latest/web.html#tornado.web.RequestHandler.write_error
        """
        reason = 'Page not found'
        logging.info("Error do something here again")


class GoogleUser(object):
    """Stores the information that google returns from a user throuhgh its secured API.
    """
    def __init__(self, user_token):
        self.user_token = user_token
        self._google_plus_api = "https://www.googleapis.com/plus/v1/people/me"
        self.authenticated = False
        #Fetch actual information from Google API

        params = {'access_token': self.user_token.get('access_token')}
        r = requests.get(self._google_plus_api, params=params)
        if not r.status_code == requests.status_codes.codes.OK:
            self.authenticated = False
        else:
            info = json.loads(r.text)
            if isAuthorized([email['value'] for email in info.get('emails')][0]):
                self.authenticated = True
            self.display_name = info.get('displayName', '')
            self.emails = [email['value'] for email in info.get('emails')]

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
            self.redirect('/static/not_authorized.html')

class AuthorizedHandler(BaseHandler):
    def prepare(self):
        if not self.current_user:
            self.redirect('/static/not_authorized.html')
        if not self.is_authorized():
            self.redirect('/static/not_authorized.html')

class UnsafeHandler(BaseHandler):
    pass

class LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("code", False):
            user_token =  yield self.get_authenticated_user(
                redirect_uri=self.application.settings['redirect_uri'],
                code=self.get_argument('code')
                )
            user = GoogleUser(user_token)
            logging.info(user.display_name)
            (lAuthorized, saUser) = isAuthorized(user.emails[0])

            self.set_secure_cookie('user', user.display_name)
            self.set_secure_cookie('email', user.emails[0])
            if user.authenticated:
                self.set_secure_cookie('access_token', user_token['access_token'])

            # TODO: this should be removed when we start to support multiple
            # datasets, I leave this here for now.
            if lAuthorized:
                self.set_secure_cookie('authorized', 'yes sir')

            url = self.get_secure_cookie("login_redirect")
            self.clear_cookie("login_redirect")
            if url is None:
                url = '/'
            self.redirect(url)

        else:
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

        # TODO the `authorized` cookie is a stop-gap measure while moving to
        # the new database schema
        self.clear_cookie("authorized")
        self.clear_cookie("access_token")
        self.clear_cookie("login_redirect")
        self.set_secure_cookie('login_redirect', self.get_argument("next", '/'), 1)
        self.clear_cookie("user")
        self.clear_cookie("email")
        self.redirect("/")

class SafeStaticFileHandler(tornado.web.StaticFileHandler, SafeHandler):
    """ Serve static files for logged in users
    """
    pass

class AuthorizedStaticFileHandler(tornado.web.StaticFileHandler, AuthorizedHandler):
    """ Serve static files for authenticated users
    """
    pass
