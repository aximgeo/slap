import os
import json
import unittest
from unittest import TestCase
from mock import MagicMock, patch
mock_arcpy = MagicMock()
patch.dict("sys.modules", arcpy=mock_arcpy).start()

from slap.publisher import only_one
from slap.publisher import Publisher


class TestMapServicePublisher(TestCase):
    m = None

    def setUp(self):
        self.m = Publisher()
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

    def test_set_workspaces(self):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.set_workspaces = MagicMock()
        self.m.publish_mxd({'input': 'someFile',
                            'serverUrl': 'some/path',
                            'workspaces': {'old': 'foo', 'new': 'bar'}
                            }, 'file', 'file.sddraft')
        self.m.set_workspaces.assert_called_once_with('someFile', {'new': 'bar', 'old': 'foo'})

    def test_publish_gp_with_defaults(self):
        mock_arcpy.CreateGPSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.config_parser.cwd, 'some/path')
        self.m.publish_gp({
            'input': 'gp/myFile.tbx',
            'result': 'my/result',
            'serverUrl': 'some/path'
        }, 'file', 'file.sddraft')
        mock_arcpy.CreateGPSDDraft.assert_called_once_with(
            result=os.path.join(os.getcwd(), 'my/result'),
            out_sddraft='file.sddraft',
            service_name='file',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            executionType="Asynchronous",
            resultMapServer=False,
            showMessages="INFO",
            maximumRecords=5000,
            minInstances=2,
            maxInstances=3,
            maxUsageTime=100,
            maxWaitTime=10,
            maxIdleTime=180,
            tags=None
        )

    def test_publish_gp_with_config_values(self):
        mock_arcpy.CreateGPSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.config_parser.cwd, 'some/path')
        self.m.publish_gp({
            'input': 'gp/myFile.tbx',
            'result': 'my/result',
            'serverUrl': 'some/path',
            'serverType': 'MY_SERVER_TYPE',
            'copyDataToServer': True,
            'folderName': 'myFolder',
            'serviceName': 'myNamedService',
            'summary': 'My Summary',
            'executionType': 'Synchronous',
            'tags': 'Tags tags'
        }, 'myFile', 'myFile.sddraft')
        mock_arcpy.CreateGPSDDraft.assert_called_once_with(
            result=os.path.join(os.getcwd(), 'my/result'),
            out_sddraft='myFile.sddraft',
            service_name='myNamedService',
            server_type='MY_SERVER_TYPE',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags',
            executionType="Synchronous",
            resultMapServer=False,
            showMessages="INFO",
            maximumRecords=5000,
            minInstances=2,
            maxInstances=3,
            maxUsageTime=100,
            maxWaitTime=10,
            maxIdleTime=180
        )

    def test_publish_mxd_with_defaults(self):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.config_parser.cwd, 'some/path')
        self.m.publish_mxd({
           'input': 'myFile.mxd',
           'serverUrl': 'some/path'
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
        self.m.connection_file_path = os.path.join(self.m.config_parser.cwd, 'some/path')
        self.m.publish_mxd({
            'input': 'myFile.mxd',
            'serverType': 'MY_SERVER_TYPE',
            'copyDataToServer': True,
            'folderName': 'myFolder',
            'serviceName': 'myNamedService',
            'summary': 'My Summary',
            'tags': 'Tags tags'
        }, 'myFile', 'myFile.sddraft')
        mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
            map_document={'mxd': 'myMap'},
            out_sddraft='myFile.sddraft',
            service_name='myNamedService',
            server_type='MY_SERVER_TYPE',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags'
        )

    def test_publish_image_service_with_defaults(self):
        mock_arcpy.CreateImageSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.config_parser.cwd, 'some/path')
        self.m.publish_image_service({
            'input': '//share/dir/fgdb.gdb/myFile',
            'serverUrl': 'some/path'
        }, 'myFile', 'myFile.sddraft')
        mock_arcpy.CreateImageSDDraft.assert_called_once_with(
            raster_or_mosaic_layer='//share/dir/fgdb.gdb/myFile',
            out_sddraft='myFile.sddraft',
            service_name='myFile',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            tags=None
        )

    def test_publish_image_service_with_config_values(self):
        mock_arcpy.CreateImageSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.config_parser.cwd, 'some/path')
        self.m.publish_image_service({
            'input': '//share/dir/fgdb.gdb/myFile',
            'serverUrl': 'some/path',
            'serverType': 'MY_SERVER_TYPE',
            'copyDataToServer': True,
            'folderName': 'myFolder',
            'serviceName': 'myNamedService',
            'summary': 'My Summary',
            'tags': 'Tags tags'
        }, 'myFile', 'myFile.sddraft')
        mock_arcpy.CreateImageSDDraft.assert_called_once_with(
            raster_or_mosaic_layer='//share/dir/fgdb.gdb/myFile',
            out_sddraft='myFile.sddraft',
            service_name='myNamedService',
            server_type='MY_SERVER_TYPE',
            connection_file_path=os.path.join(self.m.config_parser.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags'
        )

    def test_setting_service_initial_state(self):
        mock_arcpy.UploadServiceDefinition_server = MagicMock()
        config = json.loads('{"initialState": "STOPPED"}')
        self.m.upload_service_definition("test", config)
        mock_arcpy.UploadServiceDefinition_server.assert_called_once_with(
            in_sd_file='test',
            in_server=self.m.connection_file_path,
            in_startupType='STOPPED'
        )

    def test_setting_service_initial_state_defaults_to_started(self):
        mock_arcpy.UploadServiceDefinition_server = MagicMock()
        self.m.upload_service_definition("test", [])
        mock_arcpy.UploadServiceDefinition_server.assert_called_once_with(
            in_sd_file='test',
            in_server=self.m.connection_file_path,
            in_startupType='STARTED'
        )

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
