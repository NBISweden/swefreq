import logging
import tornado.auth
import urllib.parse
import db

from handlers import BaseHandler

class DeveloperLoginHandler(BaseHandler):
    def get(self):
        if not self.get_argument("user", False):
            self.send_error(status_code=403)
        elif not self.get_argument("email", False):
            self.send_error(status_code=403)

        self.set_secure_cookie('user', self.get_argument("user"))
        self.set_secure_cookie('email', self.get_argument("email"))
        self.set_secure_cookie('identity', self.get_argument("email"))
        self.set_secure_cookie('identity_type', 'google')
        self.finish()


class DeveloperLogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()

        redirect = self.get_argument("next", '/')
        self.redirect(redirect)


class ElixirLoginHandler(BaseHandler, tornado.auth.OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL     = "https://perun.elixir-czech.cz/oidc/authorize"
    _OAUTH_ACCESS_TOKEN_URL  = "https://perun.elixir-czech.cz/oidc/token"
    _OAUTH_USERINFO_ENDPOINT = "https://perun.elixir-czech.cz/oidc/userinfo"
    _OAUTH_SETTINGS_KEY      = 'elixir_oauth'

    def _generate_state(self):
        state = uuid.uuid4().hex
        self.set_secure_cookie('state', state)
        return state

    def _check_state(self, state):
        cookie_state = self.get_secure_cookie('state').decode('ascii')
        return state == cookie_state

    def _update_to_elixir_account(self, user, from_account_type = "google"):
        """
        Takes a previous login session and updates the user in the database
        """
        try:
            _email = self.get_secure_cookie('email').decode('utf-8')
            _identity_type = self.get_secure_cookie('identity_type').decode('utf-8')

            if _identity_type == from_account_type:
                db.User.update( name = user["name"],
                                email = user["email"],
                                identity = user["sub"],
                                identity_type = 'elixir'
                               ).where( db.User.email == _email ).execute()
        except AttributeError as e:
            # This will happen whenever we don't have a previous login, so this is fine
            pass
        except Exception as e:
            if "Duplicate entry" in str(e):
                logging.error("This elixir account is already in our database, so it can't be used to update another google account.")
            else:
                logging.error(str(e))

    async def get(self):
        if self.get_argument("code", False):

            if not self._check_state(self.get_argument('state', 'N/A')):
                # TODO Redirect somewhere?
                logging.error("We're beeing MITM:ed or something ABORT!")
                return

            user_token = await self.get_user_token(self.get_argument('code'))
            user       = await self.get_user(user_token["access_token"])

            self._update_to_elixir_account(user = user, from_account_type = "google")

            self.set_secure_cookie('access_token', user_token["access_token"])
            self.set_secure_cookie('user', user["name"])
            self.set_secure_cookie('email', user["email"])
            self.set_secure_cookie('identity', user["sub"])
            self.set_secure_cookie('identity_type', 'elixir')

            redirect = self.get_secure_cookie("login_redirect")
            self.clear_cookie("login_redirect")
            if redirect is None:
                redirect = '/'
            self.redirect(redirect)

        elif self.get_argument("error", False):
            logging.error("Elixir error: {}".format( self.get_argument("error") ))
            logging.error(" Description: {}".format( self.get_argument("error_description") ))
            # TODO We should do some redirect here I guess

        else:
            self.set_secure_cookie('login_redirect', self.get_argument("next", '/'), 1)
            state = self._generate_state()
            self.authorize_redirect(
                    redirect_uri  = self.settings['elixir_oauth']['redirect_uri'],
                    client_id     = self.settings['elixir_oauth']['id'],
                    scope         = ['openid', 'profile', 'email', 'bona_fide_status'],
                    response_type = 'code',
                    extra_params  = {'state': state}
                )

    async def get_user(self, access_token):
        http = self.get_auth_http_client()

        response = await http.fetch(
                self._OAUTH_USERINFO_ENDPOINT,
                headers = {
                    'Content-Type':  'application/x-www-form-urlencoded',
                    'Authorization': "Bearer {}".format(access_token),
                }
            )

        if response.error:
            logging.error("get_user error: {}".format(response))
            return

        return tornado.escape.json_decode( response.body )

    async def get_user_token(self, code):
        redirect_uri = self.settings['elixir_oauth']['redirect_uri']
        http = self.get_auth_http_client()
        body = urllib.parse.urlencode({
                "redirect_uri": redirect_uri,
                "code": code,
                "grant_type": "authorization_code",
            })

        client_id = self.settings['elixir_oauth']['id']
        secret    = self.settings['elixir_oauth']['secret']

        authorization = base64.b64encode(
                bytes("{}:{}".format(client_id, secret),
                      'ascii' )
            ).decode('ascii')

        response = await http.fetch(
                self._OAUTH_ACCESS_TOKEN_URL,
                method  = "POST",
                body    = body,
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': "Basic {}".format(authorization),
                },
            )

        if response.error:
            logging.error("get_user_token error: {}".format(response))
            return

        return tornado.escape.json_decode( response.body )


class ElixirLogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()

        redirect = self.get_argument("next", '/')
        self.redirect(redirect)


class GoogleLoginHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
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

            try:
                # Check if there is the user is already in the database.
                # This will generate an exception if the user does not exist, preventing login
                db.User.select().where(db.User.email == self._get_google_email(user)).get()

                self.set_secure_cookie('user', user["displayName"])
                self.set_secure_cookie('access_token', user_token["access_token"])
                self.set_secure_cookie('email', self._get_google_email(user))
                self.set_secure_cookie('identity', self._get_google_email(user))
                self.set_secure_cookie('identity_type', 'google')
            except Exception:
                msg = "You have no user information logged in our database, so you may directly log in using elixir without updating."
                self.set_user_msg(msg, "success")

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

    def _get_google_email(self, user):
        email = ''
        # There can be several emails registered for a user.
        for email in user["emails"]:
            if email.get('type', '') == 'account':
                return email['value']

        return user['emails'][0]['value']


class GoogleLogoutHandler(BaseHandler, tornado.auth.GoogleOAuth2Mixin):
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

        self.clear_all_cookies()

        redirect = self.get_argument("next", '/')
        self.redirect(redirect)
