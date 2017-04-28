import tornado.web
import tornado.auth
import tornado.template as template
import json
import requests
import logging
import peewee

import secrets
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
        try:
            self.dataset = db.Dataset.select().where( db.Dataset.name == 'SweGen').get()
        except peewee.DoesNotExist:
            ## TODO Can't find dataset, should return a 404 page.
            pass

    def get_current_user(self):
        email = self.get_secure_cookie('email')
        name  = self.get_secure_cookie('user')

        # Fix ridiculous bug with quotation marks showing on the web
        if name and (name[0] == '"') and (name[-1] == '"'):
            name = user[1:-1]

        if email:
            try:
                self.user = db.User.select().where( db.User.email == email ).get()
            except peewee.DoesNotExist:
                ## Not saved in the database yet
                return db.User(email = email, name = name)
        else:
            return None

    def get_current_user_name(self):
        user = self.current_user
        if user:
            return user.name
        return None

    def is_admin(self):
        user = self.current_user
        if not user:
            return False

        try:
            db.DatasetAccess.select().where(
                    db.DatasetAccess.user == user,
                    db.DatasetAccess.dataset == self.dataset,
                    db.DatasetAccess.is_admin
                ).get()
            return True
        except peewee.DoesNotExist:
            return False

    def is_authorized(self):
        user = self.current_user
        if not user:
            return False

        try:
            db.DatasetAccess.select().where(
                    db.DatasetAccess.user == user,
                    db.DatasetAccess.dataset == self.dataset,
                    db.DatasetAccess.has_access
                ).get()
            return True
        except peewee.DoesNotExist:
            return False

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
            self.authenticated = True
            info = json.loads(r.text)
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
        super(SafeHandler, self).prepare()
        if not self.current_user:
            self.redirect('/static/not_authorized.html')

class AuthorizedHandler(BaseHandler):
    def prepare(self):
        super(AurhizedHandler, self).prepare()
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

            self.set_secure_cookie('user', user.display_name)
            self.set_secure_cookie('email', user.emails[0])
            self.set_secure_cookie('access_token', user_token['access_token'])

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
