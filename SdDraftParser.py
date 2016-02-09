import xml.etree.ElementTree as ET


class SdDraftParser:
    _tree = None
    _path_to_sd_draft = None

    def __init__(self):
        pass

    def parse_sd_draft(self, path_to_sd_draft):
        self._path_to_sd_draft = path_to_sd_draft
        self._tree = ET.parse(path_to_sd_draft)

    def save_sd_draft(self):
        self.set_namespaces()
        with open(self._path_to_sd_draft, 'w') as f:
            self._tree.write(f, xml_declaration=True, encoding="utf-8")

    def set_namespaces(self):
        root = self._tree.getroot()
        root.set("xmlns:typens", "http://www.esri.com/schemas/ArcGIS/10.1")
        root.set("xmlns:xs", "http://www.w3.org/2001/XMLSchema")

    def set_as_replacement_service(self):
        for node in self._tree.findall("Type"):  # All 'Type' nodes that are children of root
            node.text = 'esriServiceDefinitionType_Replacement'

    def disable_schema_locking(self):
        self.set_configuration_property('schemaLockingEnabled', 'false')

    def set_configuration_property(self, key, value):
        for node in self._tree.findall(str.format("./Configurations/SVCConfiguration/Definition/ConfigurationProperties/"
                                       "PropertyArray/PropertySetProperty[Key='{}']/Value", key)):
            node.text = value