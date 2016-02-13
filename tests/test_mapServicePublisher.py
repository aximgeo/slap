import json
import unittest
from unittest import TestCase
from mock import MagicMock, patch
mock_arcpy = MagicMock()
patch.dict("sys.modules", arcpy=mock_arcpy).start()

from ags_publishing_tools.MapServicePublisher import MapServicePublisher

class TestMapServicePublisher(TestCase):
    m = None

    def setUp(self):
        self.m = MapServicePublisher()
        self.m.config = {
            'connectionFilePath': 'my/connection',
            'mapServices': {
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }

    def connection_file_paths_match(self, path, config):
        self.assertEqual(self.m.currentDirectory + path, self.m.get_connection_file_path('mapServices', config))

    def test_get_top_level_connection_file_path(self):
        self.connection_file_paths_match('my/connection', {'input': 'foo'})

    def test_get_type_level_connection_file_path(self):
        self.m.config = {
            'mapServices': {
                'connectionFilePath': 'my/type/connection',
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }
        self.connection_file_paths_match('my/type/connection', {'input': 'foo'})

    def test_get_service_level_connection_file_path(self):
        self.m.config = {
            'mapServices': {
                'services': [
                    {
                        'input': 'foo',
                        'connectionFilePath': 'my/service/connection'
                    }
                ]
            }
        }
        self.connection_file_paths_match('my/service/connection', {
            'input': 'foo',
            'connectionFilePath': 'my/service/connection'
        })

    def test_raise_exception_when_input_not_found(self):
        with self.assertRaises(ValueError):
            self.m.publish_input('bar')

    def test_check_service_type_with_backslashes_in_input(self):
        def test_method():
            return True

        def fake_publish(type, method, config):
            return True

        self.m._publish_service = fake_publish
        self.m.config = json.loads('{"imageServices": {"services": [{"input": "\\\\foo\\bar\\baz","connectionFilePath": "my/service/connection"}]}}')
        self.assertTrue(self.m.check_service_type('imageServices', '\\foo\bar\baz', test_method))

    def test_analysis_successful_true(self):
        self.assertTrue(self.m.analysis_successful({}))

    def test_analysis_successful_raises_exception(self):
        with self.assertRaises(RuntimeError):
            self.m.analysis_successful({'foo': 'bar'})

    def test_get_filenames(self):
        self.assertEqual(self.m.get_filenames('foo', 'output/'), ('output/foo.sddraft', 'output/foo.sd'))

if __name__ == '__main__':

    unittest.main()
