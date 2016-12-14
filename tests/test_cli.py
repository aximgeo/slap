from unittest import TestCase
from mock import MagicMock, patch
from slap import cli
mock_arcpy = MagicMock()
module_patcher = patch.dict('sys.modules', {'arcpy': mock_arcpy})
module_patcher.start()


class TestCli(TestCase):

    required_args = ['-u', 'user', '-p', 'pass', '-c', 'config.json']

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

    def test_register_data_sources(self):
        with patch('slap.publisher.Publisher.register_data_sources') as mock_register:
            with patch('slap.publisher.ConfigParser.load_config'):
                cli.main(self.required_args)
                mock_register.assert_called_once()

    def test_publish_all(self):
        with patch('slap.publisher.Publisher.publish_all') as mock_publish:
            with patch('slap.publisher.ConfigParser.load_config'):
                cli.main(self.required_args)
                mock_publish.assert_called_once()

    def test_create_site(self):
        with patch('slap.api.Api.create_site') as mock_create_site:
            with patch('slap.publisher.ConfigParser.load_config'):
                cli.main(self.required_args + ['-s'])
                mock_create_site.assert_called_once()
