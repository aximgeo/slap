from unittest import TestCase
from mock import MagicMock
from slap import git


class TestGitFileManager(TestCase):

    def test_can_filter_mxds(self):
        git.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(git.get_changed_mxds(), ['foo.mxd', 'baz.MXD'])

    def test_get_args(self):
        git.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(git.build_args(), '-i foo.mxd -i baz.MXD')