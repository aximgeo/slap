from os import path
import json
import unittest
from unittest import TestCase
from mock import MagicMock, patch, call
from slap.publisher import Publisher


class TestMapServicePublisher(TestCase):

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

    def test_publish_all(self):
        expected_calls = [call(x) for x in self.publisher.config_parser.service_types]
        with patch('slap.publisher.Publisher.publish_services') as mock_publish_services:
            self.publisher.publish_all()
            mock_publish_services.assert_has_calls(expected_calls)

    def test_get_publishing_params_from_config(self):
        config = {
            'input': 'some/input',
            'output': 'some/output',
            'serviceName': 'serviceName',
            'folderName': 'folderName',
            'json': {'foo': 'bar'},
            'initialState': 'STOPPED'
        }
        expected = ('some/input', 'some/output', 'serviceName', 'folderName', {'foo': 'bar'}, 'STOPPED')
        self.assertEqual(expected, self.publisher._get_publishing_params_from_config(config))

    def test_get_default_publishing_params_from_config(self):
        config = {
            'input': 'some/input'
        }
        expected = ('some/input', 'output', 'input', None, {}, 'STARTED')
        self.assertEqual(expected, self.publisher._get_publishing_params_from_config(config))

    def test_publish_service_no_errors(self):
        with patch('slap.publisher.Publisher._get_method_by_service_type') as mock_publish_method:
            mock_publish_method.return_value = MagicMock(return_value={'errors': {}})
            with patch('slap.publisher.Publisher.publish_sd_draft') as mock_publish_sd_draft:
                self.publisher.publish_service('some_type', {'input': 'some/input'})
                mock_publish_sd_draft.assert_called_once()

    def test_publish_service_with_errors(self):
        with patch('slap.publisher.Publisher._get_method_by_service_type') as mock_publish_method:
            mock_publish_method.return_value = MagicMock(return_value={'errors': {'something': 'bad'}})
            with patch('slap.publisher.Publisher.publish_sd_draft') as mock_publish_sd_draft:
                with self.assertRaises(RuntimeError):
                    self.publisher.publish_service('some_type', {'input': 'some/input'})
                mock_publish_sd_draft.assert_not_called()

    def test_get_service_definition_paths(self):
        expected = ('file', path.abspath('output/file.sddraft'), path.abspath('output/file.sd'))
        actual = self.publisher._get_service_definition_paths('/my/file.mxd', 'output')
        self.assertEqual(expected, actual)

    def test_create_output_directory(self):
        pass

    def test_set_hostname(self):
        config = {
            'agsUrl': 'http://server/arcgis',
            'mapServices': {
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }
        publisher = Publisher('user', 'pwd', config, 'server2')
        self.assertEqual(publisher.config['agsUrl'], 'http://server2/arcgis')

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
            '{"imageServices": {"services": [{"input": "\\\\foo\\bar\\baz",'
            '"connectionFilePath": "my/service/connection"}]}}')
        self.assertTrue(self.publisher._check_service_type('imageServices', '\\foo\bar\baz'))

    def test_analysis_successful_true(self):
        self.assertTrue(self.publisher.analysis_successful({}))

    def test_analysis_successful_raises_exception(self):
        with self.assertRaises(RuntimeError):
            self.publisher.analysis_successful({'foo': 'bar'})

    def test_get_method_by_type(self):
        self.assertEqual(self.publisher.arcpy_helper.publish_mxd, self.publisher._get_method_by_service_type('mapServices'))
        self.assertEqual(self.publisher.arcpy_helper.publish_gp, self.publisher._get_method_by_service_type('gpServices'))
        self.assertEqual(self.publisher.arcpy_helper.publish_image_service,
                         self.publisher._get_method_by_service_type('imageServices'))
        with self.assertRaises(ValueError):
            self.publisher._get_method_by_service_type('foo')

    def test_register_data_sources(self):
        data_sources = [{'foo': 'bar'}]
        self.publisher.config = {'dataSources': data_sources}
        with patch('slap.esri.ArcpyHelper.register_data_sources') as mock_register:
            self.publisher.register_data_sources()
            mock_register.assert_called_once_with(data_sources)

    def test_delete_service(self):
        service_name = 'myService'
        folder_name = 'folder'
        with patch('slap.api.Api.service_exists') as mock_exists:
            mock_exists.return_value = {'exists': True}
            with patch('slap.api.Api.delete_service') as mock_delete:
                self.publisher.delete_service(service_name, folder_name)
                mock_delete.assert_called_once_with(service_name=service_name, folder=folder_name)

    def test_delete_service_only_if_exists(self):
        service_name = 'myService'
        folder_name = 'folder'
        with patch('slap.api.Api.service_exists') as mock_exists:
            mock_exists.return_value = {'exists': False}
            with patch('slap.api.Api.delete_service') as mock_delete:
                self.publisher.delete_service(service_name, folder_name)
                mock_delete.assert_not_called()

    def test_update_service(self):
        service_name = 'myService'
        folder_name = 'folder'
        params = {'foo': 'bar', 'baz': 'quux'}
        with patch('slap.api.Api.get_service_params') as mock_get_params:
            mock_get_params.return_value = {'baz': 'quux'}
            with patch('slap.api.Api.edit_service') as mock_edit:
                self.publisher.update_service(service_name, folder_name, {'foo': 'bar'})
                mock_edit.assert_called_once_with(service_name=service_name, folder=folder_name, params=params)


@patch('slap.esri.ArcpyHelper.stage_service_definition')
@patch('slap.publisher.Publisher.delete_service')
@patch('slap.esri.ArcpyHelper.upload_service_definition')
@patch('slap.publisher.Publisher.update_service')
class TestMapServicePublisherSdDraft(TestCase):

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

    def test_publish_sd_draft(self, mock_update, mock_upload_sd, mock_delete, mock_stage_sd):
        sddraft = 'path/to/sddraft'
        sd = 'path/to/sd'
        service_name = 'myService'
        self.publisher.publish_sd_draft(sddraft, sd, service_name)
        mock_stage_sd.assert_called_once_with(sddraft=sddraft, sd=sd)
        mock_delete.assert_called_once_with(service_name=service_name, folder_name=None)
        mock_upload_sd.assert_called_once_with(sd=sd, initial_state='STARTED')
        mock_update.assert_not_called()

    def test_publish_sd_draft_with_json(self, mock_update, mock_upload_sd, mock_delete, mock_stage_sd):
        sddraft = 'path/to/sddraft'
        sd = 'path/to/sd'
        service_name = 'myService'
        folder = 'folder'
        initial_state = 'STOPPED'
        json = {'foo': 'bar'}
        self.publisher.publish_sd_draft(sddraft, sd, service_name, folder, initial_state, json)
        mock_stage_sd.assert_called_once_with(sddraft=sddraft, sd=sd)
        mock_delete.assert_called_once_with(service_name=service_name, folder_name=folder)
        mock_upload_sd.assert_called_once_with(sd=sd, initial_state=initial_state)
        mock_update.assert_called_once_with(service_name=service_name, folder_name=folder, json=json)


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
