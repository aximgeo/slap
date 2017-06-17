from unittest import TestCase

from mock import patch


class TestTokenAuth(TestCase):

    # def test_token_url_no_portal(self):
    #     api = Api(
    #         ags_url='http://myserver/arcgis/admin',
    #         token_url=None,
    #         portal_url=None,
    #         username='user',
    #         password='pass'
    #     )
    #     self.assertEqual(api._token_url, 'http://myserver/arcgis/admin/generateToken')
    #
    # def test_token_url_with_portal(self):
    #     api = Api(
    #         ags_url='http://myserver/arcgis/admin',
    #         token_url='foo/generateToken',
    #         portal_url='http://myserver/portal/sharing/rest',
    #         username='user',
    #         password='pass'
    #     )
    #     self.assertEqual(api._token_url, 'foo/generateToken')
    #
    # def test_token(self):
    #     api = self.create_api()
    #     api._token = 'my_token_value'
    #     self.assertEqual(api.token, 'my_token_value')
    #     api._token = None
    #
    # def test_get_token(self):
    #     with patch('slap.api.Api.post') as mock_post:
    #         api = self.create_api()
    #         token_params = {
    #             'username': api._username,
    #             'password': api._password,
    #             'client': 'requestip',
    #             'expiration': 60,
    #             'f': 'json'
    #         }
    #         token_value = 'my_new_token_value'
    #         mock_post.return_value = {'token': token_value}
    #         token = api.token
    #         mock_post.assert_called_once_with(api._token_url, token_params)
    #         self.assertEqual(token, token_value)