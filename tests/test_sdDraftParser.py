import unittest
import xml.etree.ElementTree as ET
from unittest import TestCase
from ags_publishing_tools.SdDraftParser import SdDraftParser


class TestSdDraftParser(TestCase):

    m = None

    def setUp(self):
        self.m = SdDraftParser()

    def strip_whitespace(self, string):
        return "".join(string.split())

    def test_convert_boolean(self):
        self.assertEqual(self.m.convert_if_boolean(True), 'true')
        self.assertEqual(self.m.convert_if_boolean(False), 'false')
        self.assertEqual(self.m.convert_if_boolean('fooBarBaz'), 'fooBarBaz')
        self.assertEqual(self.m.convert_if_boolean(1), 1)

    def test_raise_exception_when_no_nodes_found(self):
        xml = """
        <SVCManifest>
            <ItemInfo>
            </ItemInfo>
        </SVCManifest>
        """
        self.m._tree = ET.fromstring(xml)
        with self.assertRaises(KeyError):
            self.m._get_nodes("Type")

    def test_set_replacement_service(self):
        xml = """
        <SVCManifest>
            <Type>esriServiceDefinitionType_Foo</Type>
            <ItemInfo>
                <Type/>
            </ItemInfo>
        </SVCManifest>
        """
        expected = """
        <SVCManifest>
            <Type>esriServiceDefinitionType_Replacement</Type>
            <ItemInfo>
                <Type/>
            </ItemInfo>
        </SVCManifest>
        """
        self.m._tree = ET.fromstring(xml)
        self.m.set_as_replacement_service()
        self.assertEqual(self.strip_whitespace(ET.tostring(self.m._tree)), self.strip_whitespace(expected))

    def test_set_schema_locking(self):
        xml = """
        <SVCManifest>
            <Configurations>
                <SVCConfiguration>
                    <Definition>
                        <ConfigurationProperties>
                            <PropertyArray>
                                <PropertySetProperty>
                                    <Key>schemaLockingEnabled</Key>
                                    <Value>true</Value>
                                </PropertySetProperty>
                            </PropertyArray>
                        </ConfigurationProperties>
                    </Definition>
                </SVCConfiguration>
            </Configurations>
        </SVCManifest>
        """
        expected = """
        <SVCManifest>
            <Configurations>
                <SVCConfiguration>
                    <Definition>
                        <ConfigurationProperties>
                            <PropertyArray>
                                <PropertySetProperty>
                                    <Key>schemaLockingEnabled</Key>
                                    <Value>false</Value>
                                </PropertySetProperty>
                            </PropertyArray>
                        </ConfigurationProperties>
                    </Definition>
                </SVCConfiguration>
            </Configurations>
        </SVCManifest>
        """
        self.m._tree = ET.fromstring(xml)
        self.m.disable_schema_locking()
        self.assertEqual(self.strip_whitespace(ET.tostring(self.m._tree)), self.strip_whitespace(expected))
