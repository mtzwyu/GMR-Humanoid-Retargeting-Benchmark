"""Sinh report/bao_cao.pdf tu report/bao_cao.md.

Cach chay (tai thu muc goc repo):
    python report/make_report.py

Yeu cau:
    - Python 3.10+ voi: markdown, beautifulsoup4, python-docx, pillow, pypdf
      (pip install markdown beautifulsoup4 python-docx pillow pypdf)
    - LibreOffice (Writer) de xuat PDF. Mac dinh tim:
        C:/Program Files/LibreOffice/program/soffice.com
      hoac dat bien moi truong SOFFICE_BIN tro toi soffice.com/soffice.exe.

Vi sao dung LibreOffice: repo khong luu file .docx; script dung python-docx
dung DOCX tam (A4, Times New Roman, so trang), roi goi LibreOffice xuat PDF.
Dung soffice.com (ban console) de subprocess cho LibreOffice chay xong;
soffice.exe tren Windows tra ve ngay va khong bao loi.

Luu y: bang muc luc nam trong bao_cao.md. Neu sua noi dung lam cac muc doi
trang, cap nhat cot "Trang" cua muc luc trong md roi chay lai script.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "report", "bao_cao.md")
OUT_PDF = os.path.join(ROOT, "report", "bao_cao.pdf")
EXPECTED_PAGES = 15

BODY_PT = 11.0
TABLE_PT = 8.5
FIG_CM = 15.5
BODY_FONT = "Times New Roman"
HEAD_FONT = "Arial"
CODE_FONT = "Consolas"
DARK = RGBColor(0x06, 0x34, 0x3C)


def find_soffice() -> str:
    candidates = [
        os.environ.get("SOFFICE_BIN", ""),
        r"C:\Program Files\LibreOffice\program\soffice.com",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        "/usr/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise FileNotFoundError(
        "Khong tim thay LibreOffice. Cai LibreOffice hoac dat SOFFICE_BIN "
        "tro toi soffice.com/soffice.exe."
    )


def shade_paragraph(p, hex_fill):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    pPr.append(shd)


def shade_cell(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def add_runs(paragraph, node, bold=False, italic=False, code=False):
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if not text:
                continue
            run = paragraph.add_run(text)
            run.bold = bold or None
            run.italic = italic or None
            run.font.name = CODE_FONT if code else BODY_FONT
            run.font.size = Pt(BODY_PT * 0.9) if code else Pt(BODY_PT)
        elif isinstance(child, Tag):
            if child.name == "br":
                paragraph.add_run().add_break()
            else:
                add_runs(
                    paragraph,
                    child,
                    bold=bold or child.name in ("strong", "b"),
                    italic=italic or child.name in ("em", "i"),
                    code=code or child.name == "code",
                )


def add_heading(doc, text, level, first=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.page_break_before = (level == 1 and not first)
    pf.space_before = Pt(0 if level == 1 else (9 if level == 2 else 6))
    pf.space_after = Pt(4 if level <= 2 else 3)
    pf.keep_with_next = True
    run = p.add_run(text)
    run.font.name = HEAD_FONT
    run.element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_FONT)
    run.bold = True
    run.font.color.rgb = DARK if level in (2, 3) else RGBColor(0, 0, 0)
    run.font.size = Pt({1: 16, 2: 13.5, 3: 11.5, 4: 10.5}.get(level, 10.5))


def add_paragraph(doc, node, style="body"):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(3)
    pf.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
        if style in ("quote", "cover")
        else WD_ALIGN_PARAGRAPH.JUSTIFY
    )
    if style == "quote":
        pf.left_indent = Cm(0.3)
        pf.space_before = Pt(3)
        pf.space_after = Pt(5)
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        left = OxmlElement("w:left")
        left.set(qn("w:val"), "single")
        left.set(qn("w:sz"), "12")
        left.set(qn("w:space"), "4")
        left.set(qn("w:color"), "028090")
        pBdr.append(left)
        pPr.append(pBdr)
        shade_paragraph(p, "F2F8F9")
    add_runs(p, node)
    return p


def add_list(doc, node, ordered):
    items = [li for li in node.find_all("li", recursive=False)]
    for i, li in enumerate(items, 1):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(0.6)
        pf.first_line_indent = Cm(-0.45)
        pf.space_after = Pt(2)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.add_run(("%d. " % i) if ordered else "\u2022  ")
        for child in li.children:
            if isinstance(child, Tag) and child.name in ("ul", "ol"):
                continue
            if isinstance(child, NavigableString):
                wrapper = BeautifulSoup("<span>%s</span>" % str(child), "html.parser").span
                add_runs(p, wrapper)
            elif isinstance(child, Tag):
                add_runs(p, child)


def add_table(doc, node, content_width_cm=17.0):
    rows = node.find_all("tr")
    if not rows:
        return
    ncol = max(len(r.find_all(["th", "td"])) for r in rows)
    table = doc.add_table(rows=0, cols=ncol)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    texts = [[c.get_text(" ", strip=True) for c in r.find_all(["th", "td"])] for r in rows]
    raw = []
    for ci in range(ncol):
        longest = max((len(row[ci]) for row in texts if ci < len(row)), default=3)
        raw.append(max(4, min(longest, 90)))
    header_tokens = [
        max((len(x) for x in (texts[0][ci] if ci < len(texts[0]) else "").split()), default=1)
        for ci in range(ncol)
    ]
    mins = []
    for ci in range(ncol):
        token = header_tokens[ci]
        for row in texts:
            if ci < len(row):
                token = max(token, max((len(x) for x in row[ci].split()), default=1))
        mins.append(max(1.3, 0.19 * min(token, 22) + 0.45))

    if sum(mins) >= content_width_cm:
        scale = content_width_cm / sum(mins)
        widths = [m * scale for m in mins]
    else:
        extra = content_width_cm - sum(mins)
        total = float(sum(raw))
        widths = [m + extra * r / total for m, r in zip(mins, raw)]

    for ri, tr in enumerate(rows):
        cells = tr.find_all(["th", "td"])
        row = table.add_row()
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if ri == 0:
            header = OxmlElement("w:tblHeader")
            header.set(qn("w:val"), "true")
            trPr.append(header)
        for ci in range(ncol):
            cell = row.cells[ci]
            cell.width = Cm(widths[ci])
            cell.margin_left = Cm(0.06)
            cell.margin_right = Cm(0.06)
            cell.margin_top = Cm(0.02)
            cell.margin_bottom = Cm(0.02)
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
            cell.paragraphs[0].paragraph_format.line_spacing = 1.0
            if ri == 0:
                cell.paragraphs[0].paragraph_format.keep_with_next = True
            if ci < len(cells):
                p = cell.paragraphs[0]
                add_runs(p, cells[ci])
                for run in p.runs:
                    run.font.name = HEAD_FONT
                    run.font.size = Pt(TABLE_PT)
                    run.element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_FONT)
                if cells[ci].name == "th":
                    for run in p.runs:
                        run.bold = True
            if ri == 0:
                shade_cell(cell, "DCECEE")
    for ci, width in enumerate(widths):
        table.columns[ci].width = Cm(width)

    gap = doc.add_paragraph()
    gap.paragraph_format.space_before = Pt(0)
    gap.paragraph_format.space_after = Pt(0)
    gap.paragraph_format.line_spacing = Pt(3)
    gap.add_run("").font.size = Pt(2)


def add_image(doc, node):
    src = node.get("src", "")
    path = src if os.path.isabs(src) else os.path.join(ROOT, src)
    if not os.path.exists(path):
        print("CANH BAO: thieu anh", path)
        return
    iw, ih = Image.open(path).size
    width_cm = FIG_CM
    height_cm = width_cm * ih / iw
    if height_cm > 11.5:
        height_cm = 11.5
        width_cm = height_cm * iw / ih
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width_cm))


def build_docx(docx_path):
    source = open(MD, "r", encoding="utf-8").read()
    body_html = markdown.markdown(
        source,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
        output_format="html5",
    )
    soup = BeautifulSoup(body_html, "html.parser")

    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21.0), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.0)
    section.left_margin = section.right_margin = Cm(2.0)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_PT)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(2.0)
    normal.paragraph_format.line_spacing = 1.06

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    run.font.name = BODY_FONT
    run.font.size = Pt(9)

    h1_count = 0
    cover = True
    blocks = [e for e in soup.children if isinstance(e, Tag)]
    for index, element in enumerate(blocks):
        name = element.name
        next_is_table = index + 1 < len(blocks) and blocks[index + 1].name == "table"
        if name in ("h1", "h2", "h3", "h4"):
            level = int(name[1])
            text = element.get_text(" ", strip=True)
            add_heading(doc, text, level, first=(level == 1 and h1_count == 0))
            if level == 1:
                h1_count += 1
                if text.startswith("MỤC LỤC"):
                    cover = False
        elif name == "p":
            if element.find("img") and not element.get_text(strip=True):
                add_image(doc, element.find("img"))
            else:
                p = add_paragraph(doc, element, style=("cover" if cover else "body"))
                if next_is_table:
                    p.paragraph_format.keep_with_next = True
        elif name in ("ul", "ol"):
            add_list(doc, element, ordered=(name == "ol"))
        elif name == "blockquote":
            for pnode in element.find_all("p", recursive=False) or [element]:
                add_paragraph(doc, pnode, style="quote")
        elif name == "table":
            add_table(doc, element)

    doc.save(docx_path)


def count_pages(pdf_path):
    try:
        from pypdf import PdfReader

        return len(PdfReader(pdf_path).pages)
    except Exception:
        return None


def main():
    if not os.path.exists(MD):
        sys.exit("Khong thay %s" % MD)
    soffice = find_soffice()
    workdir = tempfile.mkdtemp(prefix="bao_cao_")
    docx_path = os.path.join(workdir, "bao_cao.docx")
    try:
        print("Doc", MD)
        build_docx(docx_path)
        print("Goi LibreOffice:", soffice)
        result = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", workdir, docx_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.returncode != 0:
            sys.exit("LibreOffice loi (exit %d): %s" % (result.returncode, result.stderr))
        pdf_tmp = os.path.join(workdir, "bao_cao.pdf")
        if not os.path.exists(pdf_tmp):
            sys.exit("LibreOffice khong tao PDF: %s" % result.stderr)
        os.replace(pdf_tmp, OUT_PDF)
        pages = count_pages(OUT_PDF)
        if pages is None:
            print("Da ghi", OUT_PDF)
        else:
            print("Da ghi %s (%d trang)" % (OUT_PDF, pages))
            if pages != EXPECTED_PAGES:
                print(
                    "CANH BAO: bao cao %d trang, hop dong la %d trang. Kiem tra lai "
                    "noi dung/anh va cap nhat muc luc trong bao_cao.md." % (pages, EXPECTED_PAGES)
                )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
