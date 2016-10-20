import json
import unittest
from unittest import TestCase
from mock import MagicMock, patch
from slap.publisher import only_one
from slap.publisher import Publisher


class TestMapServicePublisher(TestCase):
    publisher = None

    def setUp(self):
        config = {
            'agsUrl': 'my/server',
            'mapServices': {
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }
        self.publisher = Publisher('user', 'pwd', config)

    def test_only_one(self):
        self.assertTrue(only_one([True, False, False]))
        self.assertTrue(only_one([False, ['foo', 'bar'], False]))
        self.assertTrue(only_one([True, [], False]))
        self.assertTrue(only_one(["some sha", False, False]))
        self.assertFalse(only_one([True, True]))
        self.assertFalse(only_one([True, ['foo'], False]))

    def test_service_name_set_by_param(self):
        config = {
            'input': 'my/filename.mxd',
            'serviceName': 'foo',
            'json': {
                'serviceName': 'bar'
            }
        }
        self.assertEqual(self.publisher._get_service_name_from_config(config), 'foo')

    def test_service_name_set_by_json(self):
        config = {
            'input': 'my/filename.mxd',
            'json': {
                'serviceName': 'baz'
            }
        }
        self.assertEqual(self.publisher._get_service_name_from_config(config), 'baz')

    def test_service_name_set_by_filename(self):
        config = {
            'input': 'my/filename.mxd',
        }
        self.assertEqual(self.publisher._get_service_name_from_config(config), 'filename')

    def test_raise_exception_when_input_not_found(self):
        with self.assertRaises(ValueError):
            self.publisher.publish_input('bar')

    def test_check_service_type_with_backslashes_in_input(self):
        self.publisher.publish_service = MagicMock(return_value=True)
        self.publisher.config = json.loads(
            '{"imageServices": {"services": [{"input": "\\\\foo\\bar\\baz","connectionFilePath": "my/service/connection"}]}}')
        self.assertTrue(self.publisher.check_service_type('imageServices', '\\foo\bar\baz'))

    def test_analysis_successful_true(self):
        self.assertTrue(self.publisher.analysis_successful({}))

    def test_analysis_successful_raises_exception(self):
        with self.assertRaises(RuntimeError):
            self.publisher.analysis_successful({'foo': 'bar'})

    def test_get_method_by_type(self):
        self.assertEqual(self.publisher.arcpy_helper.publish_mxd, self.publisher._get_method_by_type('mapServices'))
        self.assertEqual(self.publisher.arcpy_helper.publish_gp, self.publisher._get_method_by_type('gpServices'))
        self.assertEqual(self.publisher.arcpy_helper.publish_image_service, self.publisher._get_method_by_type('imageServices'))
        with self.assertRaises(ValueError):
            self.publisher._get_method_by_type('foo')


@patch('slap.config.ConfigParser.load_config')
class TestLoadingConfig(TestCase):

    def test_load_config_by_path(self, mock_load_config):
        config_path = 'path/to/config'
        publisher = Publisher('user', 'pwd', config_path)
        publisher.config_parser.load_config.assert_called_once_with(config_path)

    def test_load_config_as_dict(self, mock_load_config):
        publisher = Publisher('user', 'pwd', {'input': 'foo', 'agsUrl': 'bar'})
        assert not publisher.config_parser.load_config.called

if __name__ == '__main__':

    unittest.main()
