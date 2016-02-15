import os
import unittest
from unittest import TestCase
from ags_publishing_tools.ConfigParser import ConfigParser


class TestSdDraftParser(TestCase):
    m = None

    def setUp(self):
        self.m = ConfigParser()
        self.m.config = {
            'connectionFilePath': 'my/connection',
            'mapServices': {
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }

    def connection_file_paths_match(self, path, config):
        self.assertEqual(os.getcwd() + '\\' +  path, self.m.get_connection_file_path('mapServices', config))


    def test_get_top_level_connection_file_path(self):
        self.connection_file_paths_match('my/connection', {'input': 'foo'})


    def test_get_type_level_connection_file_path(self):
        self.m.config = {
            'mapServices': {
                'connectionFilePath': 'my/type/connection',
                'services': [
                    {
                        'input': 'foo'
                    }
                ]
            }
        }
        self.connection_file_paths_match('my/type/connection', {'input': 'foo'})


    def test_get_service_level_connection_file_path(self):
        self.m.config = {
            'mapServices': {
                'services': [
                    {
                        'input': 'foo',
                        'connectionFilePath': 'my/service/connection'
                    }
                ]
            }
        }
        self.connection_file_paths_match('my/service/connection', {
            'input': 'foo',
            'connectionFilePath': 'my/service/connection'
        })
