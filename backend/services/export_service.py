import io
import os
import html
from datetime import datetime
from typing import Dict, List

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer


class ExportService:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    @staticmethod
    def _to_dataframe(test_cases: List[Dict]) -> pd.DataFrame:
        records = []
        for case in test_cases:
            records.append(
                {
                    "Test Case ID": case.get("test_case_id", ""),
                    "Title": case.get("title", ""),
                    "Preconditions": case.get("preconditions", ""),
                    "Steps": "\n".join(case.get("steps", [])),
                    "Expected Result": case.get("expected_result", ""),
                    "Test Type": case.get("test_type", ""),
                    "Priority": case.get("priority", ""),
                }
            )
        return pd.DataFrame(records)

    def export_excel_bytes(self, test_cases: List[Dict]) -> bytes:
        df = self._to_dataframe(test_cases)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TestCases", index=False)
        return buffer.getvalue()

    def export_pdf_bytes(self, test_cases: List[Dict]) -> bytes:
        def _safe(value) -> str:
            text = str(value or "-")
            return html.escape(text).replace("\n", "<br/>")

        styles = getSampleStyleSheet()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            textColor=colors.HexColor("#4A5D8A"),
            fontSize=10,
            spaceAfter=14,
        )
        case_title_style = ParagraphStyle(
            "CaseTitle",
            parent=styles["Heading3"],
            textColor=colors.HexColor("#1B2A4A"),
            spaceBefore=10,
            spaceAfter=6,
        )
        label_style = ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#243B6B"),
            spaceAfter=2,
        )
        value_style = ParagraphStyle(
            "Value",
            parent=styles["Normal"],
            leading=14,
            spaceAfter=6,
        )

        elements = [
            Paragraph("Generated Test Cases", styles["Title"]),
            Paragraph(
                f"Total Cases: {len(test_cases)} | Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                subtitle_style,
            ),
            Spacer(1, 12),
        ]

        for idx, case in enumerate(test_cases, start=1):
            case_id = case.get("test_case_id", f"TC-{idx}")
            case_title = case.get("title", "Untitled test case")
            steps = case.get("steps", [])

            steps_text = "<br/>".join(
                f"{step_idx}. {_safe(step)}"
                for step_idx, step in enumerate(steps, start=1)
            ) or "-"

            elements.extend(
                [
                    Paragraph(f"{idx}. {_safe(case_id)} - {_safe(case_title)}", case_title_style),
                    Paragraph("Preconditions", label_style),
                    Paragraph(_safe(case.get("preconditions", "-")), value_style),
                    Paragraph("Test Steps", label_style),
                    Paragraph(steps_text, value_style),
                    Paragraph("Expected Result", label_style),
                    Paragraph(_safe(case.get("expected_result", "-")), value_style),
                    Paragraph(
                        f"<b>Type:</b> {_safe(case.get('test_type', '-'))} &nbsp;&nbsp;&nbsp; "
                        f"<b>Priority:</b> {_safe(case.get('priority', '-'))}",
                        value_style,
                    ),
                    Spacer(1, 6),
                    HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#C7D3EC")),
                    Spacer(1, 8),
                ]
            )

        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def export_gherkin_bytes(test_cases: List[Dict]) -> bytes:
        lines = [
            "Feature: Generated Jira Test Cases",
            "",
            "  # Auto-generated scenarios from Jira content",
            "",
        ]

        for idx, case in enumerate(test_cases, start=1):
            case_id = str(case.get("test_case_id", f"TC-{idx:03d}")).strip()
            title = str(case.get("title", "Generated test case")).strip()
            preconditions = str(case.get("preconditions", "")).strip()
            expected = str(case.get("expected_result", "Expected result is achieved.")).strip()
            steps = case.get("steps", []) or []

            lines.append(f"  Scenario: {case_id} - {title}")
            if preconditions:
                lines.append(f"    Given {preconditions}")
            else:
                lines.append("    Given the system is ready for execution")

            if steps:
                for step_idx, step in enumerate(steps):
                    clean_step = str(step).strip() or f"step {step_idx + 1} is executed"
                    keyword = "When" if step_idx == 0 else "And"
                    lines.append(f"    {keyword} {clean_step}")
            else:
                lines.append("    When the test flow is executed")

            lines.append(f"    Then {expected or 'the expected behavior is observed'}")
            lines.append("")

        return "\n".join(lines).encode("utf-8")
