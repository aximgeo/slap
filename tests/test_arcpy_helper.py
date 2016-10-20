import os
import json
from unittest import TestCase
from slap.arcpy_helper import ArcpyHelper
from mock import MagicMock, patch
mock_arcpy = MagicMock()
patch.dict("sys.modules", arcpy=mock_arcpy).start()


class TestArcpyHelper(TestCase):
    m = None

    def setUp(self):
        self.m = ArcpyHelper('user', 'pwd', 'my/ags')

    def test_get_full_path(self):
        self.assertEqual(os.path.join(os.getcwd(), 'foo'), self.m.get_full_path('foo'))

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
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
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
            connection_file_path=os.path.join(self.m.cwd, 'some/path'),
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
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
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
            connection_file_path=os.path.join(self.m.cwd, 'some/path'),
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
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
        self.m.publish_mxd({
            'input': 'myFile.mxd',
            'serverUrl': 'some/path'
        }, 'file', 'file.sddraft')
        mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
            map_document={'mxd': 'myMap'},
            out_sddraft='file.sddraft',
            service_name='file',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.m.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            tags=None
        )

    def test_publish_mxd_with_config_values(self):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
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
            connection_file_path=os.path.join(self.m.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags'
        )

    def test_publish_image_service_with_defaults(self):
        mock_arcpy.CreateImageSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
        self.m.publish_image_service({
            'input': '//share/dir/fgdb.gdb/myFile',
            'serverUrl': 'some/path'
        }, 'myFile', 'myFile.sddraft')
        mock_arcpy.CreateImageSDDraft.assert_called_once_with(
            raster_or_mosaic_layer='//share/dir/fgdb.gdb/myFile',
            out_sddraft='myFile.sddraft',
            service_name='myFile',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.m.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            tags=None
        )

    def test_publish_image_service_with_config_values(self):
        mock_arcpy.CreateImageSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
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
            connection_file_path=os.path.join(self.m.cwd, 'some/path'),
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