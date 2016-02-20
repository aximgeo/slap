__author__ = 'ifirkin'

import unittest
from unittest import TestCase
from mock import MagicMock, patch
from ags_publishing_tools import GitFileManager


class TestGitFileManager(TestCase):

    def test_can_filter_mxds(self):
        self.assertEqual(GitFileManager.get_changed_mxds(['foo.mxd', 'bar.txt', 'baz.MXD']), ['foo.mxd', 'baz.MXD'])