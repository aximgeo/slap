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
