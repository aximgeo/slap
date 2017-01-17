from unittest import TestCase
from mock import MagicMock, patch
from slap import cli
mock_arcpy = MagicMock()
module_patcher = patch.dict('sys.modules', {'arcpy': mock_arcpy})
module_patcher.start()


class TestPublishCli(TestCase):

    required_args = ['publish', '-u', 'user', '-p', 'pass']

    def test_throws_if_no_username(self):
        with self.assertRaises(SystemExit):
            cli.main(['publish', '-c', 'config.json', '-p', 'pass'])

    def test_throws_if_no_password(self):
        with self.assertRaises(SystemExit):
            cli.main(['publish', '-u', 'user', '-c', 'config.json'])

    def test_throws_if_both_git_and_inputs_specified(self):
        with self.assertRaises(SystemExit):
            cli.main(['publish', '-u', 'user', '-p', 'pass', '-c', 'config.json', '-i', 'some/file', '-g', 'some-hash'])

    def test_uses_default_config(self):
        with patch('slap.cli.Publisher') as mock_publisher:
            with patch('slap.publisher.ConfigParser.load_config'):
                cli.main(['publish', '-u', 'user', '-p', 'pass'])
                mock_publisher.assert_called_once_with('user', 'pass', 'config.json', None)

    def test_set_hostname(self):
        with patch('slap.cli.Publisher') as mock_publisher:
            with patch('slap.publisher.ConfigParser.load_config'):
                cli.main(self.required_args + ['-n', 'host'])
                mock_publisher.assert_called_once_with('user', 'pass', 'config.json', 'host')

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

    def test_publish_inputs(self):
        with patch('slap.publisher.Publisher.publish_input') as mock_publish:
            with patch('slap.publisher.ConfigParser.load_config'):
                input_file = 'my/file'
                cli.main(self.required_args + ['-i', input_file])
                mock_publish.assert_called_once_with(input_file)

    def test_publish_git(self):
        with patch('slap.cli.Publisher.publish_input') as mock_publisher:
            with patch('slap.publisher.ConfigParser.load_config'):
                with patch('slap.git.get_changed_mxds') as mock_git:
                    sha = 'some-hash'
                    file = 'some/file'
                    mock_git.return_value = [file]
                    cli.main(self.required_args + ['-g', sha])
                    mock_git.assert_called_once_with(sha)
                    mock_publisher.assert_called_once_with(file)
