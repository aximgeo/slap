import os
import json
from unittest import TestCase
from mock import MagicMock, patch

# We need to mock arcpy before we import the helper




class TestArcpyHelper(TestCase):

    def setUp(self):
        self.mock_arcpy = MagicMock()
        self.module_patcher = patch.dict('sys.modules', {'arcpy': self.mock_arcpy})
        self.module_patcher.start()
        from slap.esri import ArcpyHelper
        self.m = ArcpyHelper('user', 'pwd', 'my/ags')

    def tearDown(self):
        self.module_patcher.stop()

    def test_get_full_path(self):
        self.assertEqual(os.path.join(os.getcwd(), 'foo'), self.m.get_full_path('foo'))

    def test_set_workspaces(self):
        self.mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        self.mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.set_workspaces = MagicMock()
        self.m.publish_mxd({'input': 'someFile',
                            'serverUrl': 'some/path',
                            'workspaces': {'old': 'foo', 'new': 'bar'}
                            }, 'file', 'file.sddraft')
        self.m.set_workspaces.assert_called_once_with('someFile', {'new': 'bar', 'old': 'foo'})

    def test_publish_gp_with_defaults(self):
        self.mock_arcpy.CreateGPSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
        self.m.publish_gp({
            'input': 'gp/myFile.tbx',
            'result': 'my/result',
            'serverUrl': 'some/path'
        }, 'file', 'file.sddraft')
        self.mock_arcpy.CreateGPSDDraft.assert_called_once_with(
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
        self.mock_arcpy.CreateGPSDDraft = MagicMock()
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
        self.mock_arcpy.CreateGPSDDraft.assert_called_once_with(
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
        self.mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        self.mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
        self.m.publish_mxd({
            'input': 'myFile.mxd',
            'serverUrl': 'some/path'
        }, 'file', 'file.sddraft')
        self.mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
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
        self.mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        self.mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
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
        self.mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
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
        self.mock_arcpy.CreateImageSDDraft = MagicMock()
        self.m.connection_file_path = os.path.join(self.m.cwd, 'some/path')
        self.m.publish_image_service({
            'input': '//share/dir/fgdb.gdb/myFile',
            'serverUrl': 'some/path'
        }, 'myFile', 'myFile.sddraft')
        self.mock_arcpy.CreateImageSDDraft.assert_called_once_with(
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
        self.mock_arcpy.CreateImageSDDraft = MagicMock()
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
        self.mock_arcpy.CreateImageSDDraft.assert_called_once_with(
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
        self.mock_arcpy.UploadServiceDefinition_server = MagicMock()
        config = json.loads('{"initialState": "STOPPED"}')
        self.m.upload_service_definition("test", config)
        self.mock_arcpy.UploadServiceDefinition_server.assert_called_once_with(
            in_sd_file='test',
            in_server=self.m.connection_file_path,
            in_startupType='STOPPED'
        )

    def test_setting_service_initial_state_defaults_to_started(self):
        self.mock_arcpy.UploadServiceDefinition_server = MagicMock()
        self.m.upload_service_definition("test", [])
        self.mock_arcpy.UploadServiceDefinition_server.assert_called_once_with(
            in_sd_file='test',
            in_server=self.m.connection_file_path,
            in_startupType='STARTED'
        )