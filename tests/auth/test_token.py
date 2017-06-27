from unittest import TestCase

import requests
import requests_mock
from mock import patch

from slap.auth.token import TokenAuth


class TestTokenAuth(TestCase):

    def test_get_token(self):
        with patch('requests.post') as mock_post:
            username='user'
            password='pass'
            token_url='token/url'
            token_params = {
                'username': username,
                'password': password,
                'client': 'requestip',
                'expiration': 60,
                'f': 'json'
            }
            auth = TokenAuth(username, password, token_url)
            auth._get_token()
            mock_post.assert_called_once_with(token_url, token_params, verify=False)

    def test_caches_token(self):
        with requests_mock.mock() as mock_request:
            with patch('slap.auth.token.TokenAuth._get_token') as mock_get_token:
                url = 'mock://test.com'
                mock_request.post(url)
                auth = TokenAuth(username='user', password='pass', token_url='get/token')
                auth._token = 'token'
                requests.post(url, auth=auth)
                mock_get_token.assert_not_called()
