from unittest import TestCase
from mock import MagicMock, patch
from slap import cli
mock_arcpy = MagicMock()
module_patcher = patch.dict('sys.modules', {'arcpy': mock_arcpy})
module_patcher.start()


class TestCli(TestCase):

    def test_only_one(self):
        self.assertTrue(cli.only_one([True, False, False]))
        self.assertTrue(cli.only_one([False, ['foo', 'bar'], False]))
        self.assertTrue(cli.only_one([True, [], False]))
        self.assertTrue(cli.only_one(["some sha", False, False]))
        self.assertTrue(cli.only_one([True, False]))
        self.assertFalse(cli.only_one([True, True]))
        self.assertFalse(cli.only_one([True, ['foo'], False]))

    def test_throws_if_no_config(self):
        with self.assertRaises(SystemExit):
            cli.main(['-u', 'user', '-p', 'pass'])

    def test_throws_if_no_username(self):
        with self.assertRaises(SystemExit):
            cli.main(['-c', 'config.json', '-p', 'pass'])

    def test_throws_if_no_password(self):
        with self.assertRaises(SystemExit):
            cli.main(['-u', 'user', '-c', 'config.json'])

    def test_throws_if_both_git_and_inputs_specified(self):
        with self.assertRaises(SystemExit):
            cli.main(['-u', 'user', '-p', 'pass', '-c', 'config.json', '-i', 'some/file', '-g', 'some-hash'])
