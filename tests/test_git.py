from unittest import TestCase
from mock import MagicMock, patch
from slap import git

# mock_subprocess = MagicMock()
# patch.dict("sys.modules", subprocess=mock_subprocess).start()


class TestGitFileManager(TestCase):

    def test_can_filter_mxds(self):
        git.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(git.get_changed_mxds(), ['foo.mxd', 'baz.MXD'])

    def test_get_args(self):
        git.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(git.build_args(), '-i foo.mxd -i baz.MXD')

    @patch('slap.git.check_output')
    def test_subprocess_output(self, mock_check_output):
        expected = ['git',  'diff', '--name-only',  'HEAD', 'HEAD~1']
        # mock_check_output.return_value = ''
        # mock_check_output.return_value.returncode = 0
        git.get_changed_files()
        mock_check_output.assert_called_once_with(expected)
