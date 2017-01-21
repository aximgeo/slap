import os
from os import path
from collections import namedtuple
from slap.esri import ArcpyHelper
from unittest import TestCase
from mock import MagicMock, patch, call


@patch('slap.esri.arcpy')
class TestListDataSources(TestCase):

    @staticmethod
    def create_mock_layer(workspace):
        layer = MagicMock()
        layer.supports = MagicMock(return_value=True)
        layer.workspacePath = workspace
        return layer

    def test_list_single_data_source(self, mock_arcpy):
        data_source = 'layer1'
        layer = self.create_mock_layer(data_source)
        mock_arcpy.mapping.ListLayers = MagicMock(return_value=[layer])
        expected = [data_source]
        actual = ArcpyHelper.list_workspaces_for_mxd({})
        self.assertEqual(expected, actual)

    def test_lists_unique_data_sources(self, mock_arcpy):
        data_source1 = 'layer1'
        data_source2 = 'layer2'
        layer1 = self.create_mock_layer(data_source1)
        layer2 = self.create_mock_layer(data_source2)
        mock_arcpy.mapping.ListLayers = MagicMock(return_value=[layer1, layer1, layer2])
        expected = [data_source2, data_source1]
        actual = ArcpyHelper.list_workspaces_for_mxd({})
        self.assertEqual(expected, actual)

    def test_list_data_sources(self, mock_arcpy):
        data_source = 'layer1'
        layer = self.create_mock_layer(data_source)
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={})
        mock_arcpy.mapping.ListLayers = MagicMock(return_value=[layer])
        expected = [data_source]
        actual = ArcpyHelper.list_workspaces(['mxd1'])
        self.assertEqual(expected, actual)

    def test_list_data_sources_with_names(self, mock_arcpy):
        data_source = 'layer1'
        expected = [{'name': 'testName', 'workspacePath': data_source}]
        Description = namedtuple('Description', 'name')
        description = Description('testName')
        with patch('slap.esri.arcpy.Describe') as mock_describe:
            with patch('slap.esri.ArcpyHelper.list_workspaces') as mock:
                mock_describe.return_value = description
                mock.return_value = [data_source]
                actual = ArcpyHelper.get_workspaces_with_names(['mxd1'])
                self.assertEqual(expected, actual)


@patch('slap.esri.arcpy')
class TestRegisterDataSources(TestCase):

    def setUp(self):
        self.arcpy_helper = ArcpyHelper('user', 'pwd', 'my/ags')

    def test_does_not_add_existing_sources(self, mock_arcpy):
        mock_arcpy.ListDataStoreItems = MagicMock(return_value=["foo", "bar"])
        self.arcpy_helper.register_data_source = MagicMock()
        data_sources = [
            {
                "name": "foo",
                "serverPath": "path/to/database_connection.sde"
            },
            {
                "name": "bar",
                "serverPath": "path/to/database_connection.gdb"
            }
        ]
        self.arcpy_helper.register_data_sources(data_sources)
        self.arcpy_helper.register_data_source.assert_not_called()

    def test_add_data_store_item_folder(self, mock_arcpy):
        data_source = {
            "name": "myFolder",
            "serverPath": "path/to/database_connection.gdb"
        }
        self.arcpy_helper.register_data_source(data_source)
        mock_arcpy.AddDataStoreItem.assert_called_once_with(
            connection_file=self.arcpy_helper.connection_file_path,
            datastore_type='FOLDER',
            connection_name='myFolder',
            server_path=self.arcpy_helper.get_full_path(data_source["serverPath"]),
            client_path=self.arcpy_helper.get_full_path(data_source["serverPath"])
        )

    def test_add_data_store_item_sde(self, mock_arcpy):
        data_source = {
            "name": "myDatabase",
            "serverPath": "path/to/database_connection.sde"
        }
        self.arcpy_helper.register_data_source(data_source)
        mock_arcpy.AddDataStoreItem.assert_called_once_with(
            connection_file=self.arcpy_helper.connection_file_path,
            datastore_type='DATABASE',
            connection_name='myDatabase',
            server_path=self.arcpy_helper.get_full_path(data_source["serverPath"]),
            client_path=self.arcpy_helper.get_full_path(data_source["serverPath"])
        )

@patch('slap.esri.arcpy')
class TestArcpyHelper(TestCase):

    def setUp(self):
        self.arcpy_helper = ArcpyHelper('user', 'pwd', 'my/ags')

    def test_get_full_path(self, mock_arcpy):
        self.assertEqual(os.path.join(os.getcwd(), 'foo'), self.arcpy_helper.get_full_path('foo'))

    def test_get_mxd_from_path(self, mock_arcpy):
        path_to_mxd = '/path/to/mxd'
        mock_arcpy.mapping.MapDocument = MagicMock()
        self.arcpy_helper._get_mxd_from_path(path_to_mxd)
        mock_arcpy.mapping.MapDocument.assert_called_once_with(path.normpath(path_to_mxd))

    def test_set_workspaces(self, mock_arcpy):
        workspaces = [
            {
                "old": {
                    "path": "c:/path/to/integration/connectionFile1.sde"
                },
                "new": {
                    "path": "c:/path/to/production/connectionFile1.sde",
                    "type": "FILEGDB_WORKSPACE"
                }
            },
            {
                "old": {
                    "path": "c:/path/to/integration/connectionFile2.sde",
                    "type": "FILEGDB_WORKSPACE"
                },
                "new": {
                    "path": "c:/path/to/production/connectionFile2.sde"
                }
            }
        ]
        expected_calls = [
                call(
                    old_workspace_path="c:/path/to/integration/connectionFile1.sde",
                    old_workspace_type="SDE_WORKSPACE",
                    new_workspace_path="c:/path/to/production/connectionFile1.sde",
                    new_workspace_type="FILEGDB_WORKSPACE",
                    validate=False
                ),
                call(
                    old_workspace_path="c:/path/to/integration/connectionFile2.sde",
                    old_workspace_type="FILEGDB_WORKSPACE",
                    new_workspace_path="c:/path/to/production/connectionFile2.sde",
                    new_workspace_type="SDE_WORKSPACE",
                    validate=False
                ),
        ]
        with patch('slap.esri.ArcpyHelper._get_mxd_from_path') as mock_mxd_creator:
            mock_mxd = MagicMock()
            mock_mxd.replaceWorkspaces = MagicMock()
            mock_mxd.save = MagicMock()
            mock_mxd.relativePaths = False
            mock_mxd_creator.return_value = mock_mxd
            self.arcpy_helper.set_workspaces('/path/to/mxd', workspaces)
            mock_mxd.replaceWorkspaces.assert_has_calls(expected_calls)
            self.assertTrue(mock_mxd.relativePaths)
            mock_mxd.save.assert_called_once()

    def test_set_workspaces_is_called(self, mock_arcpy):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.arcpy_helper.set_workspaces = MagicMock()
        self.arcpy_helper.publish_mxd({'input': 'someFile',
                            'serverUrl': 'some/path',
                            'workspaces': {'old': 'foo', 'new': 'bar'}
                                       }, 'file', 'file.sddraft')
        self.arcpy_helper.set_workspaces.assert_called_once_with('someFile', {'new': 'bar', 'old': 'foo'})

    def test_publish_gp_with_defaults(self, mock_arcpy):
        self.arcpy_helper.connection_file_path = os.path.join(self.arcpy_helper.cwd, 'some/path')
        self.arcpy_helper.publish_gp({
            'input': 'gp/myFile.tbx',
            'result': 'my/result',
            'serverUrl': 'some/path'
        }, 'file', 'file.sddraft')
        mock_arcpy.CreateGPSDDraft.assert_called_once_with(
            result=self.arcpy_helper.get_full_path('my/result'),
            out_sddraft='file.sddraft',
            service_name='file',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.arcpy_helper.cwd, 'some/path'),
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

    def test_publish_gp_with_config_values(self, mock_arcpy):
        mock_arcpy.CreateGPSDDraft = MagicMock()
        self.arcpy_helper.connection_file_path = os.path.join(self.arcpy_helper.cwd, 'some/path')
        self.arcpy_helper.publish_gp({
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
            result=self.arcpy_helper.get_full_path('my/result'),
            out_sddraft='myFile.sddraft',
            service_name='myNamedService',
            server_type='MY_SERVER_TYPE',
            connection_file_path=os.path.join(self.arcpy_helper.cwd, 'some/path'),
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

    def test_publish_mxd_with_defaults(self, mock_arcpy):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.arcpy_helper.connection_file_path = os.path.join(self.arcpy_helper.cwd, 'some/path')
        self.arcpy_helper.publish_mxd({
            'input': 'myFile.mxd',
            'serverUrl': 'some/path'
        }, 'file', 'file.sddraft')
        mock_arcpy.mapping.CreateMapSDDraft.assert_called_once_with(
            map_document={'mxd': 'myMap'},
            out_sddraft='file.sddraft',
            service_name='file',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.arcpy_helper.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            tags=None
        )

    def test_publish_mxd_with_config_values(self, mock_arcpy):
        mock_arcpy.mapping.MapDocument = MagicMock(return_value={'mxd': 'myMap'})
        mock_arcpy.mapping.CreateMapSDDraft = MagicMock()
        self.arcpy_helper.connection_file_path = os.path.join(self.arcpy_helper.cwd, 'some/path')
        self.arcpy_helper.publish_mxd({
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
            connection_file_path=os.path.join(self.arcpy_helper.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags'
        )

    def test_publish_image_service_with_defaults(self, mock_arcpy):
        mock_arcpy.CreateImageSDDraft = MagicMock()
        self.arcpy_helper.connection_file_path = os.path.join(self.arcpy_helper.cwd, 'some/path')
        self.arcpy_helper.publish_image_service({
            'input': '//share/dir/fgdb.gdb/myFile',
            'serverUrl': 'some/path'
        }, 'myFile', 'myFile.sddraft')
        mock_arcpy.CreateImageSDDraft.assert_called_once_with(
            raster_or_mosaic_layer='//share/dir/fgdb.gdb/myFile',
            out_sddraft='myFile.sddraft',
            service_name='myFile',
            server_type='ARCGIS_SERVER',
            connection_file_path=os.path.join(self.arcpy_helper.cwd, 'some/path'),
            copy_data_to_server=False,
            folder_name=None,
            summary=None,
            tags=None
        )

    def test_publish_image_service_with_config_values(self, mock_arcpy):
        mock_arcpy.CreateImageSDDraft = MagicMock()
        self.arcpy_helper.connection_file_path = os.path.join(self.arcpy_helper.cwd, 'some/path')
        self.arcpy_helper.publish_image_service({
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
            connection_file_path=os.path.join(self.arcpy_helper.cwd, 'some/path'),
            copy_data_to_server=True,
            folder_name='myFolder',
            summary='My Summary',
            tags='Tags tags'
        )

    def test_setting_service_initial_state(self, mock_arcpy):
        mock_arcpy.UploadServiceDefinition_server = MagicMock()
        self.arcpy_helper.upload_service_definition("test", 'STOPPED')
        mock_arcpy.UploadServiceDefinition_server.assert_called_once_with(
            in_sd_file='test',
            in_server=self.arcpy_helper.connection_file_path,
            in_startupType='STOPPED'
        )

    def test_setting_service_initial_state_defaults_to_started(self, mock_arcpy):
        mock_arcpy.UploadServiceDefinition_server = MagicMock()
        self.arcpy_helper.upload_service_definition("test")
        mock_arcpy.UploadServiceDefinition_server.assert_called_once_with(
            in_sd_file='test',
            in_server=self.arcpy_helper.connection_file_path,
            in_startupType='STARTED'
        )