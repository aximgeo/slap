import unittest
import json
import requests
from requests import Response
from unittest import TestCase
from slap.api import Api, check_parsed_response, parse_response
from mock import PropertyMock, patch

from slap.auth.token import TokenAuth


class TestApi(TestCase):
    @staticmethod
    def create_api(auth=None, verify_certs=False):
        api = Api(
            ags_url='http://myserver/arcgis/admin',
            auth=TokenAuth(username='user', password='pass', token_url='get/my/token') if auth is None else auth,
            verify_certs=verify_certs
        )
        return api

    def test_get(self):
        with patch('requests.get') as mock_request:
            auth = TokenAuth(username='user', password='pass', token_url='get/my/token')
            api = self.create_api(auth)
            url = 'my/url'
            params = {'foo': 'bar'}
            api.get(url=url, params=params)
            mock_request.assert_called_once_with(url, params=params, auth=auth, verify=False)

    def test_post(self):
        with patch('requests.post') as mock_request:
            auth = TokenAuth(username='user', password='pass', token_url='get/my/token')
            api = self.create_api(auth)
            url = 'my/url'
            params = {'foo': 'bar'}
            api.post(url=url, params=params)
            mock_request.assert_called_once_with(url, data=params, auth=auth, verify=False)

    def test_parse_response_with_bad_return_code(self):
        response = Response()
        response.status_code = 500
        response._content = '{"status":"success"}'
        self.assertRaises(requests.HTTPError, parse_response, response)

    def test_check_parsed_response(self):
        response = {'status': 'error', 'messages': ['an error occurred']}
        self.assertRaises(requests.exceptions.RequestException, check_parsed_response, response)

    def test_check_parsed_token_response(self):
        response = {'messages': ['an error occurred']}  # no 'status'
        try:
            check_parsed_response(response)
        except requests.exceptions.RequestException:
            self.fail()

    def get_mock(self, url, method, *args):
        with patch('slap.api.Api.get') as mock_method:
            api = self.create_api()
            getattr(api, method)(*args)
            mock_method.assert_called_once_with(url, {'f': 'json'})

    def post_mock(self, url, method, expected, *args):
        with patch('slap.api.Api.post') as mock_method:
            api = self.create_api()
            getattr(api, method)(*args)
            mock_method.assert_called_once_with(url, expected)

    def test_delete_map_service(self):
        self.post_mock(
            'http://myserver/arcgis/admin/services/myService.MapServer/delete',
            'delete_service',
            {'f': 'json'},
            'myService'
        )

    def test_delete_map_service_with_folder(self):
        self.post_mock('http://myserver/arcgis/admin/services/myFolder/myService.MapServer/delete',
                       'delete_service',
                       {'f': 'json'},
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
                       {'service': '{"foo": "bar"}', 'f': 'json'},
                       'myService', {'foo': 'bar'})

    def test_edit_map_service_with_folder(self):
        self.post_mock('http://myserver/arcgis/admin/services/myFolder/myService.MapServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json'},
                       'myService', {'foo': 'bar'}, 'myFolder')

    def test_edit_other_service(self):
        self.post_mock('http://myserver/arcgis/admin/services/myFolder/myService.ImageServer/edit', 'edit_service',
                       {'service': '{"foo": "bar"}', 'f': 'json'},
                       'myService', {'foo': 'bar'}, 'myFolder',
                       'ImageServer')

    def test_map_service_exists(self):
        self.post_mock('http://myserver/arcgis/admin/services/exists/exists',
                       'service_exists',
                       {'folderName': 'myFolder', 'serviceName': 'myService', 'f': 'json',
                        'type': 'MapServer'},
                       'myService', 'myFolder')

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
        username = 'user'
        password = 'pass'
        with patch('slap.api.Api.create_site') as mock_create_site:
            api.create_default_site(username=username, password=password)
            mock_create_site.assert_called_once_with(username, password, api.get_default_site_params())

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
