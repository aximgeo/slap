import unittest
import json
import requests
from requests import Response
from unittest import TestCase
from slap.api import Api
from mock import PropertyMock, patch


class TestApi(TestCase):

    @staticmethod
    def create_api():
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            token_url=None,
            portal_url=None,
            username='user',
            password='pass'
        )
        return api

    def test_token_url_no_portal(self):
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            token_url=None,
            portal_url=None,
            username='user',
            password='pass'
        )
        self.assertEqual(api._token_url, 'http://myserver/arcgis/admin/generateToken')

    def test_token_url_with_portal(self):
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            token_url='foo/generateToken',
            portal_url='http://myserver/portal/sharing/rest',
            username='user',
            password='pass'
        )
        self.assertEqual(api._token_url, 'foo/generateToken')

    def test_token(self):
        api = self.create_api()
        api._token = 'my_token_value'
        self.assertEqual(api.token, 'my_token_value')
        api._token = None

    def test_get_token(self):
        with patch('slap.api.Api.post') as mock_post:
            api = self.create_api()
            token_params = {
                'username': api._username,
                'password': api._password,
                'client': 'requestip',
                'expiration': 60,
                'f': 'json'
            }
            token_value = 'my_new_token_value'
            mock_post.return_value = {'token': token_value}
            token = api.token
            mock_post.assert_called_once_with(api._token_url, token_params)
            self.assertEqual(token, token_value)

    def test_get(self):
        with patch('requests.get') as mock_request:
            api = self.create_api()
            url = 'my/url'
            params = {'foo': 'bar'}
            api.get(url=url, params=params)
            mock_request.assert_called_once_with(url, params=params, verify=api._verify_certs)

    def test_post(self):
        with patch('requests.post') as mock_request:
            api = self.create_api()
            url = 'my/url'
            params = {'foo': 'bar'}
            api.post(url=url, params=params)
            mock_request.assert_called_once_with(url, data=params, verify=api._verify_certs)

    def test_parse_response_with_bad_return_code(self):
        api = self.create_api()
        response = Response()
        response.status_code = 500
        response._content = '{"status":"success"}'
        self.assertRaises(requests.HTTPError, api.parse_response, response)

    def test_check_parsed_response(self):
        api = self.create_api()
        response = {'status': 'error', 'messages': ['an error occurred']}
        self.assertRaises(requests.exceptions.RequestException, api.check_parsed_response, response)

    def test_check_parsed_token_response(self):
        api = self.create_api()
        response = {'messages': ['an error occurred']}  # no 'status'
        try:
            api.check_parsed_response(response)
        except requests.exceptions.RequestException:
            self.fail()

    def get_mock(self, url, method, *args):
        with patch('slap.api.Api.token', new_callable=PropertyMock) as mock_token:
            with patch('slap.api.Api.get') as mock_method:
                mock_token.return_value = 'my_token_value'
                api = self.create_api()
                getattr(api, method)(*args)
                mock_token.assert_called_once_with()
                mock_method.assert_called_once_with(url, {'f': 'json', 'token': 'my_token_value'})

    def post_mock(self, url, method, expected, *args):
        with patch('slap.api.Api.token', new_callable=PropertyMock) as mock_token:
            with patch('slap.api.Api.post') as mock_method:
                mock_token.return_value = 'my_token_value'
                api = self.create_api()
                getattr(api, method)(*args)
                mock_token.assert_called_once_with()
                mock_method.assert_called_once_with(url, expected)

    def test_delete_map_service(self):
        self.post_mock('http://myserver/arcgis/admin/services/myService.MapServer/delete',
                       'delete_service',
                       {'f': 'json', 'token': 'my_token_value'},
                       'myService')

    def test_delete_map_service_with_folder(self):
        self.post_mock('http://myserver/arcgis/admin/services/myFolder/myService.MapServer/delete',
                       'delete_service',
                       {'f': 'json', 'token': 'my_token_value'},
                       'myService', 'myFolder')

    def test_get_map_service(self):
        self.get_mock('http://myserver/arcgis/admin/services/myService.MapServer',
                      'get_service_params', 'myService')

    def test_get_map_service_with_folder(self):
        self.get_mock('http://myserver/arcgis/admin/services/myFolder/myService.MapServer',
                          'get_service_params', 'myService', 'myFolder')

    def test_get_other_service(self):
        self.get_mock('http://myserver/arcgis/admin/services/myFolder/myService.ImageServer',
                      'get_service_params', 'myService', 'myFolder', 'ImageServer')

    def test_edit_map_service(self):
        self.post_mock('http://myserver/arcgis/admin/services/myService.MapServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json', 'token': 'my_token_value'},
                       'myService', {'foo': 'bar'})

    def test_edit_map_service_with_folder(self):
        self.post_mock('http://myserver/arcgis/admin/services/myFolder/myService.MapServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json', 'token': 'my_token_value'},
                       'myService', {'foo': 'bar'}, 'myFolder')

    def test_edit_other_service(self):
        self.post_mock('http://myserver/arcgis/admin/services/myFolder/myService.ImageServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json', 'token': 'my_token_value'},
                       'myService', {'foo': 'bar'}, 'myFolder',
                       'ImageServer')

    def test_map_service_exists(self):
        self.post_mock('http://myserver/arcgis/admin/services/exists/exists',
                       'service_exists',
                       {'folderName': 'myFolder', 'serviceName': 'myService', 'f': 'json', 'token': 'my_token_value',
                        'type': 'MapServer'},
                       'myService', 'myFolder')

    def test_build_params(self):
        with patch('slap.api.Api.token', new_callable=PropertyMock) as mock_token:
            mock_token.return_value = 'my-token'
            api = self.create_api()
            expected = {'foo': 'bar', 'f': 'json', 'token': 'my-token'}
            actual = api.build_params({'foo': 'bar'})
            self.assertEqual(expected, actual)

    def test_create_site(self):
        api = self.create_api()
        with patch('slap.api.Api.post') as mock_post:
            params = {
                'foo': 'bar'
            }
            expected_params = {
                'foo': 'bar',
                'username': 'user',
                'password': 'pwd',
                'confirmPassword': 'pwd',
                'f': 'json'
            }
            api.create_site(username='user', password='pwd', params=params)
            mock_post.assert_called_once_with(api._ags_url + '/createNewSite', expected_params)

    def test_create_default_site(self):
        api = self.create_api()
        with patch('slap.api.Api.create_site') as mock_create_site:
            api.create_default_site()
            mock_create_site.assert_called_once_with(api._username, api._password, api.get_default_site_params())

    def test_get_default_site_params(self):
        self.maxDiff = None
        expected = {
            'configStoreConnection': json.dumps({
                'connectionString': '/home/arcgis/server/usr/config-store',
                'type': 'FILESYSTEM'
            }),
            'directories': json.dumps({'directories': [
                {
                    'cleanupMode': 'NONE',
                    'description': 'Stores tile caches used by map, globe, and image services for rapid performance.',
                    'directoryType': 'CACHE',
                    'maxFileAge': 0,
                    'name': 'arcgiscache',
                    'physicalPath': '/home/arcgis/server/usr/directories/arcgiscache',
                    'virtualPath': ''},
                {
                    'cleanupMode': 'TIME_ELAPSED_SINCE_LAST_MODIFIED',
                    'description': 'Stores results and other information from geoprocessing services.',
                    'directoryType': 'JOBS',
                    'maxFileAge': 360,
                    'name': 'arcgisjobs',
                    'physicalPath': '/home/arcgis/server/usr/directories/arcgisjobs',
                    'virtualPath': ''
                },
                {
                    'cleanupMode': 'TIME_ELAPSED_SINCE_LAST_MODIFIED',
                    'description': 'Stores various information generated by services, such as map images.',
                    'directoryType': 'OUTPUT',
                    'maxFileAge': 10,
                    'name': 'arcgisoutput',
                    'physicalPath': '/home/arcgis/server/usr/directories/arcgisoutput',
                    'virtualPath': ''
                },
                {
                    'cleanupMode': 'NONE',
                    'description': 'Stores files that are used internally by the GIS server.',
                    'directoryType': 'SYSTEM',
                    'maxFileAge': 0,
                    'name': 'arcgissystem',
                    'physicalPath': '/home/arcgis/server/usr/directories/arcgissystem',
                    'virtualPath': ''
                }
            ]})
        }
        api = self.create_api()
        actual = api.get_default_site_params()
        self.assertEqual(json.loads(expected['configStoreConnection']), json.loads(actual['configStoreConnection']))
        self.assertEqual(json.loads(expected['directories']), json.loads(actual['directories']))


if __name__ == '__main__':

    unittest.main()
