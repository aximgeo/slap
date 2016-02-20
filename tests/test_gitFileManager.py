__author__ = 'ifirkin'

import unittest
from unittest import TestCase
from mock import MagicMock
from ags_publishing_tools import GitFileManager


class TestGitFileManager(TestCase):

    def test_can_filter_mxds(self):
        self.assertEqual(GitFileManager.get_changed_mxds(['foo.mxd', 'bar.txt', 'baz.MXD']), ['foo.mxd', 'baz.MXD'])

    def test_get_args(self):
        GitFileManager.get_changed_files = MagicMock(return_value=['foo.mxd', 'bar.txt', 'baz.MXD'])
        self.assertEqual(GitFileManager.build_args(), '-i foo.mxd -i baz.MXD')