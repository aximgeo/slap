from requests.auth import AuthBase


class TokenAuth(AuthBase):
    def __init__(self, username, password, token_url):

        self._token_url = token_url
        self._username = username
        self._password = password
        self._token = None

    def __call__(self, r):
        # Implement my authentication
        return r
