import unittest
from unittest import TestCase
from mock import MagicMock, patch
from slap import git


@patch('slap.git.get_changed_files')
class TestGitFileManager(TestCase):

    def test_can_filter_mxds(self, get_changed_files_mock):
        get_changed_files_mock.return_value = ['foo.mxd', 'bar.txt', 'baz.MXD']
        self.assertEqual(git.get_changed_mxds(), ['foo.mxd', 'baz.MXD'])


@patch('slap.git.check_output')
class TestGitArguments(TestCase):

    def test_default_revision(self, mock_check_output):
        expected = ['git',  'diff', '--name-only',  'HEAD', 'HEAD~1']
        git.get_changed_files()
        mock_check_output.assert_called_once_with(expected)

    def test_specified_revision(self, mock_check_output):
        sha = 'some_commit_sha'
        expected = ['git',  'diff', '--name-only',  'HEAD', sha]
        git.get_changed_files(sha)
        mock_check_output.assert_called_once_with(expected)

if __name__ == "__main__":
    unittest.main()
