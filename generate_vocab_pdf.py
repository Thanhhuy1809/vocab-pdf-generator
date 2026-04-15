from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle


def register_vietnamese_font() -> str:
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/tahoma.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]

    font_name = "VNFont"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont(font_name, str(path)))
            return font_name

    return "Helvetica"


def normalize_text(value: str) -> str:
    value = value.strip()
    value = value.replace("\u2014", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip("-* ")


def split_line(line: str) -> Optional[Tuple[str, str, str]]:
    separators = ["=", "->", "", "", ":"]

    # Accept both arrow styles. The duplicated placeholder is replaced below.
    separators = ["=", "->", "→", ":"]

    for sep in separators:
        if sep in line:
            left, right = line.split(sep, 1)
            left = normalize_text(left)
            right = normalize_text(right)
            if left and right:
                return left, right, sep
    return None


def parse_entries(raw_text: str) -> List[Tuple[str, str, str]]:
    entries: List[Tuple[str, str, str]] = []
    pending_left: Optional[str] = None

    for raw_line in raw_text.splitlines():
        line = normalize_text(raw_line)
        if not line:
            continue

        lower = line.lower()
        if "từ vựng" in lower or "tu vung" in lower:
            continue

        arrow_only = re.match(r"^(?:->|→)\s*(.+)$", line)
        if arrow_only and pending_left:
            meaning = normalize_text(arrow_only.group(1))
            entries.append(("Cấu trúc", pending_left, meaning))
            pending_left = None
            continue

        split_result = split_line(line)
        if split_result:
            left, right, sep = split_result
            category = "Cấu trúc" if sep in {"->", "→"} else "Từ vựng"
            entries.append((category, left, right))
            pending_left = None
            continue

        if line.startswith(("->", "→")):
            continue

        pending_left = line

    return entries


def build_pdf(entries: List[Tuple[str, str, str]], title: str, output_path: Path) -> None:
    if not entries:
        raise ValueError("Không tìm thấy dữ liệu hợp lệ để tạo bảng.")

    font_name = register_vietnamese_font()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleVN",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=16,
        leading=20,
        alignment=1,
        spaceAfter=0.4 * cm,
    )

    header_style = ParagraphStyle(
        "HeaderVN",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        leading=13,
        textColor=colors.white,
        alignment=1,
    )

    body_style = ParagraphStyle(
        "BodyVN",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=10,
        leading=13,
    )

    center_style = ParagraphStyle(
        "CenterVN",
        parent=body_style,
        alignment=1,
    )

    table_data = [
        [
            Paragraph("STT", header_style),
            Paragraph("Loại", header_style),
            Paragraph("Từ/Cấu trúc", header_style),
            Paragraph("Nghĩa/Ghi chú", header_style),
        ]
    ]

    for idx, (category, term, meaning) in enumerate(entries, start=1):
        table_data.append(
            [
                Paragraph(str(idx), center_style),
                Paragraph(escape(category), body_style),
                Paragraph(escape(term), body_style),
                Paragraph(escape(meaning), body_style),
            ]
        )

    table = LongTable(
        table_data,
        colWidths=[1.4 * cm, 2.8 * cm, 6.6 * cm, 8.2 * cm],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#7D99B2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FBFF"), colors.HexColor("#EEF4FA")]),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    elements = [Paragraph(escape(title), title_style), Spacer(1, 0.2 * cm), table]
    document.build(elements)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tạo bảng từ vựng/cấu trúc và xuất ra PDF để in."
    )
    parser.add_argument(
        "--input",
        default="vocab_data.txt",
        help="Đường dẫn file văn bản chứa dữ liệu đầu vào (UTF-8).",
    )
    parser.add_argument(
        "--output",
        default="vocab_table.pdf",
        help="Tên file PDF đầu ra.",
    )
    parser.add_argument(
        "--title",
        default="TỪ VỰNG VÀ CẤU TRÚC CẦN CHÚ Ý (101-129)",
        help="Tiêu đề bảng trên PDF.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {input_path}")

    raw_text = input_path.read_text(encoding="utf-8")
    entries = parse_entries(raw_text)
    build_pdf(entries, args.title, output_path)

    print(f"Da tao PDF: {output_path.resolve()} | So dong: {len(entries)}")


if __name__ == "__main__":
    main()
