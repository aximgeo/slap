import json
import unittest
from unittest import TestCase
from mock import MagicMock
from slap.publisher import only_one
from slap.publisher import Publisher


class TestMapServicePublisher(TestCase):
    m = None

    def setUp(self):
        self.m = Publisher()
        self.m.init_arcpy_helper('user', 'pwd', 'my/server')
        self.m.config = {
            'serverUrl': 'my/server',
            'mapServices': {
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }

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
        self.assertEqual(self.m._get_service_name_from_config(config), 'foo')

    def test_service_name_set_by_json(self):
        config = {
            'input': 'my/filename.mxd',
            'json': {
                'serviceName': 'baz'
            }
        }
        self.assertEqual(self.m._get_service_name_from_config(config), 'baz')

    def test_service_name_set_by_filename(self):
        config = {
            'input': 'my/filename.mxd',
        }
        self.assertEqual(self.m._get_service_name_from_config(config), 'filename')

    def test_raise_exception_when_input_not_found(self):
        with self.assertRaises(ValueError):
            self.m.publish_input('bar')

    def test_check_service_type_with_backslashes_in_input(self):
        self.m.publish_service = MagicMock(return_value=True)
        self.m.config = json.loads(
            '{"imageServices": {"services": [{"input": "\\\\foo\\bar\\baz","connectionFilePath": "my/service/connection"}]}}')
        self.assertTrue(self.m.check_service_type('imageServices', '\\foo\bar\baz'))

    def test_analysis_successful_true(self):
        self.assertTrue(self.m.analysis_successful({}))

    def test_analysis_successful_raises_exception(self):
        with self.assertRaises(RuntimeError):
            self.m.analysis_successful({'foo': 'bar'})

    def test_get_sddraft_output(self):
        self.assertEqual(self.m.get_sddraft_output('foo', 'output/'), 'output/foo.sddraft')

    def test_get_sd_output(self):
        self.assertEqual(self.m.get_sd_output('foo', 'output/'), 'output/foo.sd')

    def test_get_method_by_type(self):
        self.assertEqual(self.m.arcpy_helper.publish_mxd, self.m._get_method_by_type('mapServices'))
        self.assertEqual(self.m.arcpy_helper.publish_gp, self.m._get_method_by_type('gpServices'))
        self.assertEqual(self.m.arcpy_helper.publish_image_service, self.m._get_method_by_type('imageServices'))
        with self.assertRaises(ValueError):
            self.m._get_method_by_type('foo')

if __name__ == '__main__':

    unittest.main()
