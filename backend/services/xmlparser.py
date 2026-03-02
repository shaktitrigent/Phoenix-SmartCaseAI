import xml.etree.ElementTree as ET


class XMLParser:
    def parse_xml_string(self, xml_content: str) -> str:
        root = ET.fromstring(xml_content)
        lines = []
        self._walk(root, path=root.tag, out=lines)
        return "\n".join(lines).strip()

    def parse_xml_file(self, file_path: str) -> str:
        tree = ET.parse(file_path)
        root = tree.getroot()
        lines = []
        self._walk(root, path=root.tag, out=lines)
        return "\n".join(lines).strip()

    def _walk(self, node, path, out):
        text = (node.text or "").strip()
        if text:
            out.append(f"{path}: {text}")

        for key, value in node.attrib.items():
            out.append(f"{path}.@{key}: {value}")

        for child in list(node):
            child_path = f"{path}.{child.tag}"
            self._walk(child, child_path, out)

