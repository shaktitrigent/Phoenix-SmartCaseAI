import os
from typing import List

import pandas as pd
from PyPDF2 import PdfReader
from docx import Document

from services.multi_xml_loader import MultiXMLLoader


class DocumentParser:
    def __init__(self):
        self.xml_loader = MultiXMLLoader()

    def parse_file(self, file_path: str) -> str:
        extension = os.path.splitext(file_path)[1].lower()
        try:
            if extension == ".pdf":
                return self._parse_pdf(file_path)
            if extension == ".docx":
                return self._parse_docx(file_path)
            if extension in [".xlsx", ".xls"]:
                return self._parse_excel(file_path)
            if extension == ".csv":
                return self._parse_csv(file_path)
            if extension == ".xml":
                return self._parse_xml(file_path)
            if extension in [".txt", ".log", ".md", ".json", ".yaml", ".yml", ".html", ".htm", ".rtf"]:
                return self._parse_text(file_path)
            return ""
        except Exception:
            return ""

    def parse_files(self, file_paths: List[str]) -> List[str]:
        return [self.parse_file(path) for path in file_paths if path]

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text]).strip()

    @staticmethod
    def _parse_excel(file_path: str) -> str:
        sheets = pd.read_excel(file_path, sheet_name=None)
        chunks = []
        for sheet_name, frame in sheets.items():
            chunks.append(f"Sheet: {sheet_name}")
            chunks.append(frame.fillna("").to_csv(index=False))
        return "\n".join(chunks).strip()

    @staticmethod
    def _parse_csv(file_path: str) -> str:
        frame = pd.read_csv(file_path)
        return frame.fillna("").to_csv(index=False).strip()

    def _parse_xml(self, file_path: str) -> str:
        return self.xml_loader.load_files([file_path])

    @staticmethod
    def _parse_text(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            return fp.read().strip()
