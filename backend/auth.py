"""Authentication handlers."""

import base64
import logging
import uuid
import urllib.parse

import tornado.auth

from handlers import BaseHandler


class DeveloperLoginHandler(BaseHandler):
    def get(self):
        if not self.get_argument("user", False):
            self.send_error(status_code=403)
        elif not self.get_argument("email", False):
            self.send_error(status_code=403)

        self.set_secure_cookie('user', self.get_argument("user"))  # pylint: disable=no-value-for-parameter
        self.set_secure_cookie('email', self.get_argument("email"))  # pylint: disable=no-value-for-parameter
        self.set_secure_cookie('identity', self.get_argument("email"))  # pylint: disable=no-value-for-parameter
        self.finish()


class DeveloperLogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()

        redirect = self.get_argument("next", '/')
        self.redirect(redirect)


class ElixirLoginHandler(BaseHandler, tornado.auth.OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = "https://login.elixir-czech.org/oidc/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://login.elixir-czech.org/oidc/token"
    _OAUTH_USERINFO_ENDPOINT = "https://login.elixir-czech.org/oidc/userinfo"
    _OAUTH_SETTINGS_KEY = 'elixir_oauth'

    def _generate_state(self):
        state = uuid.uuid4().hex
        self.set_secure_cookie('state', state)
        return state

    def _check_state(self, state):
        cookie_state = self.get_secure_cookie('state').decode('ascii')
        return state == cookie_state

    async def get(self):
        if self.get_argument("code", False):

            if not self._check_state(self.get_argument('state', 'N/A')):
                self.set_user_msg("We're being MITM:ed or something ABORT!", "error")
                self.redirect("/security_warning")
                return

            user_token = await self.get_user_token(self.get_argument('code'))  # pylint: disable=no-value-for-parameter
            user = await self.get_user(user_token["access_token"])

            try:
                self.set_secure_cookie('access_token', user_token["access_token"])
                self.set_secure_cookie('user', user["name"])
                self.set_secure_cookie('email', user["email"])
                self.set_secure_cookie('identity', user["sub"])
            except KeyError as err:
                logging.error(f'ElixirLoginHandler: data missing ({err}); user: {user}' +
                              f', user_token: {user_token}')
                self.redirect("/error")
                return

            redirect = self.get_secure_cookie("login_redirect")
            self.clear_cookie("login_redirect")
            if redirect is None:
                redirect = '/'
            self.redirect(redirect)

        elif self.get_argument("error", False):
            logging.error("Elixir error: {}".format(self.get_argument("error")))  # pylint: disable=no-value-for-parameter
            logging.error(" Description: {}".format(self.get_argument("error_description")))  # pylint: disable=no-value-for-parameter

            self.set_user_msg(f"Elixir Error: ,{self.get_argument('error')} " +   # pylint: disable=no-value-for-parameter
                              f"{self.get_argument('error_description')}")  # pylint: disable=no-value-for-parameter
            self.redirect("/error")

        else:
            self.set_secure_cookie('login_redirect', self.get_argument("next", '/'), 1)
            state = self._generate_state()
            self.authorize_redirect(redirect_uri=self.settings['elixir_oauth']['redirect_uri'],
                                    client_id=self.settings['elixir_oauth']['id'],
                                    scope=['openid', 'profile', 'email', 'bona_fide_status'],
                                    response_type='code',
                                    extra_params={'state': state})

    async def get_user(self, access_token):
        http = self.get_auth_http_client()

        response = await http.fetch(self._OAUTH_USERINFO_ENDPOINT,
                                    headers={'Content-Type':  'application/x-www-form-urlencoded',
                                             'Authorization': "Bearer {}".format(access_token)})

        if response.error:
            logging.error(f"get_user error: {response}")
            return

        return tornado.escape.json_decode(response.body)

    async def get_user_token(self, code):
        redirect_uri = self.settings['elixir_oauth']['redirect_uri']
        http = self.get_auth_http_client()
        body = urllib.parse.urlencode({"redirect_uri": redirect_uri,
                                       "code": code,
                                       "grant_type": "authorization_code"})

        client_id = self.settings['elixir_oauth']['id']
        secret = self.settings['elixir_oauth']['secret']

        authorization = base64.b64encode(bytes(f"{client_id}:{secret}", 'ascii')).decode('ascii')

        response = await http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                                    method="POST",
                                    body=body,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded',
                                             'Authorization': "Basic {}".format(authorization)})

        if response.error:
            logging.error(f"get_user_token error: {response}")
            return

        return tornado.escape.json_decode(response.body)


class ElixirLogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()

        redirect = self.get_argument("next", '/')
        self.redirect(redirect)
