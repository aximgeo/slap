from unittest import TestCase
from mock import MagicMock, patch
mock_arcpy = MagicMock()
module_patcher = patch.dict('sys.modules', {'arcpy': mock_arcpy})
module_patcher.start()
from slap import cli


class TestCli(TestCase):

    def test_only_one(self):
        self.assertTrue(cli.only_one([True, False, False]))
        self.assertTrue(cli.only_one([False, ['foo', 'bar'], False]))
        self.assertTrue(cli.only_one([True, [], False]))
        self.assertTrue(cli.only_one(["some sha", False, False]))
        self.assertFalse(cli.only_one([True, True]))
        self.assertFalse(cli.only_one([True, ['foo'], False]))