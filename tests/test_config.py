from unittest import TestCase
from mock import patch, mock_open
import json
from slap.config import ConfigParser


class TestConfigParser(TestCase):

    def setUp(self):
        self.config_parser = ConfigParser()
        self.config_parser.map_service_default_json = {}
        self.config_parser.image_service_default_json = {}
        self.config_parser.gp_service_default_json = {}

    def test_load_config_from_file(self):
        config_data = '{"foo": "bar"}'
        expected = json.loads(config_data)
        with patch('__builtin__.open', mock_open(read_data=config_data)):
            config_parser = ConfigParser()
            actual = config_parser._load_config_from_file('/path/to/config')
            self.assertEqual(expected, actual)

    def test_load_config(self):
        file_path = '/path/to/config'
        expected_config = dict(foo='bar')
        with patch('slap.config.ConfigParser._load_config_from_file') as mock_load_file:
            mock_load_file.return_value = expected_config
            with patch('slap.config.ConfigParser.parse_config') as mock_parse:
                self.config_parser.load_config(file_path)
                mock_load_file.assert_called_once_with(file_path)
                mock_parse.assert_called_once_with(expected_config)

    def test_empty_config(self):
        self.assertEqual(self.config_parser.parse_config({}), {
            'mapServices': {
                'services': []
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })

    def test_root_only_config(self):
        self.assertEqual(self.config_parser.parse_config({'serverUrl': 'https://my/server'}), {
            'serverUrl': 'https://my/server',
            'mapServices': {
                'services': []
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })

    def test_no_map_services(self):
        config = {
            'serverUrl': 'https://my/server',
            'gpServices': {
                'services': [{'input': 'gp', 'json': {}}]
            },
            'imageServices': {
                'services': [{'input': 'image', 'json': {}}]
            }
        }
        self.assertEqual(self.config_parser.parse_config(config), {
            'serverUrl': 'https://my/server',
            'mapServices': {
                'services': []
            },
            'gpServices': {
                'services': [{'serverUrl': 'https://my/server', 'input': 'gp', 'json': {}}]
            },
            'imageServices': {
                'services': [{'serverUrl': 'https://my/server', 'input': 'image', 'json': {}}]
            }
        })

    def test_no_gp_services(self):
        config = {
            'serverUrl': 'https://my/server',
            'mapServices': {
                'services': [{'input': 'map', 'json': {}}]
            },
            'imageServices': {
                'services': [{'input': 'image', 'json': {}}]
            }
        }
        self.assertEqual(self.config_parser.parse_config(config), {
            'serverUrl': 'https://my/server',
            'mapServices': {
                'services': [{'serverUrl': 'https://my/server', 'input': 'map', 'json': {}}]
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': [{'serverUrl': 'https://my/server', 'input': 'image', 'json': {}}]
            }
        })

    def test_no_image_services(self):
        config = {
            'serverUrl': 'https://my/server',
            'gpServices': {
                'services': [{'input': 'gp', 'json': {}}]
            },
            'mapServices': {
                'services': [{'input': 'map', 'json': {}}]
            }
        }
        self.assertEqual(self.config_parser.parse_config(config), {
            'serverUrl': 'https://my/server',
            'mapServices': {
                'services': [{'serverUrl': 'https://my/server', 'input': 'map', 'json': {}}]
            },
            'gpServices': {
                'services': [{'serverUrl': 'https://my/server', 'input': 'gp', 'json': {}}]
            },
            'imageServices': {
                'services': []
            }
        })

    def test_get_root_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        self.assertEqual(self.config_parser.get_root_keys(config), {'root_level': 'root'})

    def test_get_type_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        self.assertEqual(self.config_parser.get_type_keys(config, 'mapServices'), {'type_level': 'type'})

    def test_flattening_keys(self):
        config = {
            'root_level': 'root',
            'mapServices': {
                'type_level': 'type',
                'services': [{
                    'input': 'map'
                }]
            }
        }
        expected = {
            'input': 'map',
            'root_level': 'root',
            'type_level': 'type'
         }
        self.assertEqual(self.config_parser.parse_config(config)['mapServices']['services'][0], expected)

    def test_flattening_nested_keys(self):
        config = {
            'root_level': 'root',
            'properties': {
                'myRootProp': 'someValue'
            },
            'mapServices': {
                'type_level': 'type',
                'properties': {
                    'myTypeProp': 'someOtherValue'
                },
                'services': [{
                    'input': 'map',
                    'properties': {
                        'myServiceProp': 'someThirdValue'
                    }
                }]
            }
        }
        self.assertEqual(self.config_parser.parse_config(config)['mapServices']['services'][0], {
                                                             'input': 'map',
                                                             'root_level': 'root',
                                                             'type_level': 'type',
                                                             'properties': {
                                                                 'myRootProp': 'someValue',
                                                                 'myTypeProp': 'someOtherValue',
                                                                 'myServiceProp': 'someThirdValue'
                                                             }
                                                         })

    def check_missing_key(self, config):
        self.config_parser.config = config
        with self.assertRaises(KeyError):
            self.config_parser.check_required_keys(config)

    def test_raises_for_missing_server_url(self):
        self.check_missing_key( {
            'mapServices': {
                'services': [{'input': 'foo'}]
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })

    def test_raises_for_missing_input(self):
        self.check_missing_key( {
            'mapServices': {
                'services': [{'serverUrl': 'foo'}]
            },
            'gpServices': {
                'services': []
            },
            'imageServices': {
                'services': []
            }
        })

    def test_merge_json_dict(self):
        default_json = {
            "type": "MapServer",
            "capabilities": "Map,Query,Data",
            "properties": {
                "outputDir": "c:\\arcgis\\arcgisoutput",
                "virtualOutputDir": "/rest/directories/arcgisoutput"
            },
        }
        config_json = {
            "capabilities": "Map,Query",
            "properties": {
                "schemaLockingEnabled": False
            }
        }
        expected = {
            "type": "MapServer",
            "capabilities": "Map,Query",
            "properties": {
                "schemaLockingEnabled": False,
                "outputDir": "c:\\arcgis\\arcgisoutput",
                "virtualOutputDir": "/rest/directories/arcgisoutput"
            }
        }
        self.assertEqual(expected, self.config_parser.merge_json(default_json, config_json))

    def test_merge_json_string(self):
        default_json_string = '{"type": "MapServer","capabilities": "Map,Query,Data",' \
                              '"properties": {"outputDir": "c:\\\\arcgis\\\\arcgisoutput","virtualOutputDir": ' \
                              '"/rest/directories/arcgisoutput"}}'
        config_json = {
            "capabilities": "Map,Query",
            "properties": {
                "schemaLockingEnabled": False
            }
        }
        expected = {
            "type": "MapServer",
            "capabilities": "Map,Query",
            "properties": {
                "schemaLockingEnabled": False,
                "outputDir": "c:\\arcgis\\arcgisoutput",
                "virtualOutputDir": "/rest/directories/arcgisoutput"
            }
        }
        self.assertEqual(self.config_parser.merge_json(default_json_string, config_json), expected)