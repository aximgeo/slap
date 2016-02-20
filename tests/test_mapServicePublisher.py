import os
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

    def test_set_workspaces(self):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.set_workspaces = MagicMock()
        self.m.publish_mxd({'input': 'someFile',
                            'connectionFilePath': 'some/path',
                            'workspaces': {'old': 'foo', 'new': 'bar'}
                            }, 'file', 'file.sddraft')
        self.m.set_workspaces.assert_called_once_with({'mxd': 'myMap'}, {'new': 'bar', 'old': 'foo'})

    def test_publish_mxd_with_defaults(self):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.publish_mxd({
           'input': 'myFile.mxd',
            'connectionFilePath': 'some/path'
        }, 'file', 'file.sddraft')
        mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
            map_document={'mxd': 'myMap'},
            out_sddraft='file.sddraft',
            service_name='file',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            tags=None
        )

    def test_publish_mxd_with_config_values(self):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.publish_mxd({
            'input': 'myFile.mxd',
            'connectionFilePath': 'some/path',
            'serviceName': 'myService',
            'serverType': 'MY_SERVER_TYPE',
            'copyDataToServer': True,
            'folderName': 'myFolder',
            'summary': 'My Summary',
            'tags': 'Tags tags'
        }, 'file', 'file.sddraft')
        mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
            map_document={'mxd': 'myMap'},
            out_sddraft='file.sddraft',
            service_name='myService',
            server_type='MY_SERVER_TYPE',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags'
        )

    def test_raise_exception_when_input_not_found(self):
        with self.assertRaises(ValueError):
            self.m.publish_input('bar')

    def test_check_service_type_with_backslashes_in_input(self):
        self.m.publish_service = MagicMock(return_value=True)
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

    def test_set_draft_configuration(self):
        self.m.draft_parser.parse_sd_draft = MagicMock()
        self.m.draft_parser.set_as_replacement_service = MagicMock()
        self.m.draft_parser.save_sd_draft = MagicMock()
        self.m.draft_parser.set_configuration_property = MagicMock()
        self.m.set_draft_configuration('file.sddraft', {'myKey': 'myValue'})
        self.m.draft_parser.parse_sd_draft.assert_called_once_with('file.sddraft')
        self.m.draft_parser.set_as_replacement_service.assert_called_once_with()
        self.m.draft_parser.set_configuration_property.assert_called_once_with('myKey', 'myValue')
        self.m.draft_parser.save_sd_draft.assert_called_once_with()

if __name__ == '__main__':

    unittest.main()
