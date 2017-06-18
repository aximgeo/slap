import requests
from requests.auth import AuthBase

from slap.api import parse_response


class TokenAuth(AuthBase):
    def __init__(self, username, password, token_url):
        self._token_url = token_url
        self._username = username
        self._password = password
        self._token = None

    def __call__(self, prepared_request):
        token = self._get_token() if self._token is None else self._token
        prepared_request.prepare_url(prepared_request.url, token)
        return prepared_request

    def _get_token(self):
        params = {
            'username': self._username,
            'password': self._password,
            'client': 'requestip',
            'expiration': 60,
            'f': 'json'
        }
        response = requests.post(self._token_url, params)
        parsed_response = parse_response(response)
        self._token = parsed_response['token']
        return self._token
