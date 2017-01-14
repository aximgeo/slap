import os
from unittest import TestCase
from mock import patch
from pyfakefs import fake_filesystem
from slap import config_builder


class TestConfigBuilder(TestCase):

    def test_get_file_from_directory(self):
        test_file = os.path.join('test', 'testFile.mxd')
        fs = fake_filesystem.FakeFilesystem()
        fs.CreateFile(test_file)
        fake_os = fake_filesystem.FakeOsModule(fs)
        expected = [test_file]
        with patch('slap.config_builder.os', fake_os):
            actual = config_builder.get_mxds(['test'])
            self.assertEqual(expected, actual)

