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

    def test_raise_exception_when_input_not_found(self):
        with self.assertRaises(ValueError):
            self.m.publish_input('bar')

    def test_check_service_type_with_backslashes_in_input(self):
        def fake_publish(type, config):
            return True

        self.m.publish_service = fake_publish
        self.m.config = json.loads('{"imageServices": {"services": [{"input": "\\\\foo\\bar\\baz","connectionFilePath": "my/service/connection"}]}}')
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
        self.assertEqual(self.m.publish_mxd, self.m._get_method_by_type('mapServices'))
        self.assertEqual(self.m.publish_gp, self.m._get_method_by_type('gpServices'))
        self.assertEqual(self.m.publish_image_service, self.m._get_method_by_type('imageServices'))
        with self.assertRaises(ValueError):
            self.m._get_method_by_type('foo')

if __name__ == '__main__':

    unittest.main()
