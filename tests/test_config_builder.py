import os
from unittest import TestCase
from mock import patch
from pyfakefs import fake_filesystem
from slap import config_builder


class TestConfigBuilder(TestCase):

    def test_returns_empty_config_dict(self):
        expected = {
            'agsUrl': 'https://<hostname>:6443/arcgis/admin',
            'mapServices': {
                'services': []
            }
        }
        actual = config_builder.build_config([])
        self.assertEqual(expected, actual)

    def test_returns_config_with_one_service(self):
        test_file = os.path.join('test', 'testFile.mxd')

        expected = {
            'agsUrl': 'https://<hostname>:6443/arcgis/admin',
            'mapServices': {
                'services': [
                    {'input': test_file}
                ]
            }
        }

        fs = fake_filesystem.FakeFilesystem()
        fs.CreateFile(test_file)
        fake_os = fake_filesystem.FakeOsModule(fs)
        with patch('slap.config_builder.os', fake_os):
            actual = config_builder.build_config(['test'])
            self.assertEqual(expected, actual)


class TestConfigBuilderFileList(TestCase):

    def test_get_file_from_directory(self):
        test_file = os.path.join('test', 'testFile.mxd')
        expected = [test_file]
        fs = fake_filesystem.FakeFilesystem()
        fs.CreateFile(test_file)
        fake_os = fake_filesystem.FakeOsModule(fs)
        with patch('slap.config_builder.os', fake_os):
            actual = config_builder.get_mxds(['test'])
            self.assertEqual(expected, actual)

    def test_gets_files_from_directory_list(self):
        test_file = os.path.join('test', 'test.mxd')
        test_file_2 = os.path.join('test2', 'test.mxd')
        fs = fake_filesystem.FakeFilesystem()
        fake_os = fake_filesystem.FakeOsModule(fs)
        fs.CreateFile(test_file)
        fs.CreateFile(test_file_2)
        expected = [test_file, test_file_2]
        with patch('slap.config_builder.os', fake_os):
            actual = config_builder.get_mxds(['test', 'test2'])
            self.assertEqual(expected, actual)

    def test_gets_only_mxd_files(self):
        test_file = os.path.join('test', 'testFile.mxd')
        test_file_2 = os.path.join('test', 'badTestFile.txt')
        test_file_3 = os.path.join('test', 'testFileCaps.MXD')
        expected = [test_file, test_file_3]
        fs = fake_filesystem.FakeFilesystem()
        fs.CreateFile(test_file)
        fs.CreateFile(test_file_2)
        fs.CreateFile(test_file_3)
        fake_os = fake_filesystem.FakeOsModule(fs)
        with patch('slap.config_builder.os', fake_os):
            actual = config_builder.get_mxds(['test'])
            self.assertEqual(expected, actual)
