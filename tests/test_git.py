import unittest
from unittest import TestCase
from mock import MagicMock, patch
from slap import git


class TestGitFileManager(TestCase):

    def test_can_filter_mxds(self):
        git.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(git.get_changed_mxds(), ['foo.mxd', 'baz.MXD'])

    def test_get_args(self):
        git.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(git.build_args(), '-i foo.mxd -i baz.MXD')

    def test_subprocess_output(self, ):
        mock_check_output = MagicMock()
        with patch('slap.git.check_output', mock_check_output):
            expected = ['git',  'diff', '--name-only',  'HEAD', 'HEAD~1']
            git.get_changed_files()
            mock_check_output.assert_called_once_with(expected)

if __name__ == "__main__":
    unittest.main()