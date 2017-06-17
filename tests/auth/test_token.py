from unittest import TestCase

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
            mock_post.assert_called_once_with(token_url, token_params)
