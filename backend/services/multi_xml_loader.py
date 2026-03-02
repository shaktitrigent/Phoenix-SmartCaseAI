from typing import Iterable

from services.xmlparser import XMLParser


class MultiXMLLoader:
    def __init__(self):
        self.parser = XMLParser()

    def load_files(self, file_paths: Iterable[str]) -> str:
        parsed = []
        for file_path in file_paths:
            try:
                parsed.append(self.parser.parse_xml_file(file_path))
            except Exception:
                continue
        return "\n\n".join([x for x in parsed if x]).strip()

