import os
from unittest import TestCase
from mock import patch
from pyfakefs import fake_filesystem
from slap import config_builder


class TestConfigBuilder(TestCase):

    def setUp(self):
        self.fs = fake_filesystem.FakeFilesystem()
        self.fake_os = fake_filesystem.FakeOsModule(self.fs)

    def test_default_args(self):
        with patch('slap.config_builder.create_config_dictionary') as mock_config:
            with patch('__builtin__.open') as mock_open:
                mock_config.return_value = {}
                directories = [os.getcwd()]
                config_builder.create_config(directories)
                mock_config.assert_called_once_with(directories, 'hostname', False)
                mock_open.assert_called_once_with('config.json', 'w+')

    def test_saves_default_config_file(self):
        test_file = os.path.join('test', 'testFile.mxd')
        self.fs.CreateFile(test_file)
        fake_open = fake_filesystem.FakeFileOpen(self.fs)
        with patch('slap.config_builder.os', self.fake_os):
            with patch('__builtin__.open', fake_open):
                config_builder.create_config(['test'])
                self.assertTrue(self.fake_os.path.isfile('config.json'))

    def test_saves_named_config_file(self):
        test_file = os.path.join('test', 'testFile.mxd')
        test_directory = os.path.join('output', 'somewhere')
        config_file = os.path.join(test_directory, 'test-config.json')
        self.fs.CreateFile(test_file)
        self.fs.CreateDirectory(test_directory)
        fake_open = fake_filesystem.FakeFileOpen(self.fs)

        with patch('slap.config_builder.os', self.fake_os):
            with patch('__builtin__.open', fake_open):
                config_builder.create_config(['test'], config_file)
                self.assertTrue(self.fake_os.path.isfile(config_file))

    def test_returns_empty_config_dict(self):
        expected = {
            'agsUrl': 'https://hostname:6443/arcgis/admin',
            'mapServices': {
                'services': []
            }
        }
        actual = config_builder.create_config_dictionary([])
        self.assertEqual(expected, actual)

    def test_returns_empty_config_dict_with_hostname(self):
        expected = {
            'agsUrl': 'https://myhostname:6443/arcgis/admin',
            'mapServices': {
                'services': []
            }
        }
        actual = config_builder.create_config_dictionary([], 'myhostname')
        self.assertEqual(expected, actual)

    def test_returns_config_with_one_service(self):
        test_file = os.path.join('test', 'testFile.mxd')

        expected = {
            'agsUrl': 'https://hostname:6443/arcgis/admin',
            'mapServices': {
                'services': [
                    {'input': test_file}
                ]
            }
        }

        self.fs.CreateFile(test_file)
        with patch('slap.config_builder.os', self.fake_os):
            actual = config_builder.create_config_dictionary(['test'])
            self.assertEqual(expected, actual)

    def test_get_file_from_directory(self):
        test_file = os.path.join('test', 'testFile.mxd')
        expected = [test_file]
        self.fs.CreateFile(test_file)

        with patch('slap.config_builder.os', self.fake_os):
            actual = config_builder.get_mxds(['test'])
            self.assertEqual(expected, actual)

    def test_gets_files_from_directory_list(self):
        test_file = os.path.join('test', 'test.mxd')
        test_file_2 = os.path.join('test2', 'test.mxd')
        self.fs.CreateFile(test_file)
        self.fs.CreateFile(test_file_2)
        expected = [test_file, test_file_2]
        with patch('slap.config_builder.os', self.fake_os):
            actual = config_builder.get_mxds(['test', 'test2'])
            self.assertEqual(expected, actual)

    def test_gets_only_mxd_files(self):
        test_file = os.path.join('test', 'testFile.mxd')
        test_file_2 = os.path.join('test', 'badTestFile.txt')
        test_file_3 = os.path.join('test', 'testFileCaps.MXD')
        expected = [test_file, test_file_3]
        self.fs.CreateFile(test_file)
        self.fs.CreateFile(test_file_2)
        self.fs.CreateFile(test_file_3)

        with patch('slap.config_builder.os', self.fake_os):
            actual = config_builder.get_mxds(['test'])
            self.assertEqual(expected, actual)

    def test_get_data_sources(self):
        with patch('__builtin__.open'):
            with patch('slap.config_builder.get_mxds'):
                with patch('slap.esri.ArcpyHelper'):
                    with patch('slap.config_builder.create_data_sources_config') as mock:
                        mock.return_value = {}
                        config_builder.create_config(directories=[], register_data_sources=True)
                        mock.assert_called_once()

    def test_create_data_sources_config(self):
        expected = [
            {
                "name": "server1-database1-user1",
                "serverPath": "dataSource1"
            },
            {
                "name": "server2-database2-user2",
                "serverPath": "dataSource2"
            }
        ]
        actual = config_builder.create_data_sources_config([
            {'name': 'server1-database1-user1', 'workspacePath': 'dataSource1'},
            {'name': 'server2-database2-user2', 'workspacePath': 'dataSource2'}
        ])
        self.assertEqual(expected, actual)
