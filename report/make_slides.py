"""Sinh report/slides.pptx (16:9) tu report/slides.md.

Chay: python report/make_slides.py
- 16 slide theo dung thu tu va thoi luong trong slides.md
- Moi slide: tieu de + 3-5 gach dau dong
- Ghi chu (notes): so slide, nguoi noi, thoi luong, thong diep
"""
import io
import os
import re

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "report", "slides.md")
OUT = os.path.join(ROOT, "report", "slides.pptx")

ACCENT = RGBColor(0x1F, 0x4E, 0x79)
GREY = RGBColor(0x59, 0x59, 0x59)
DARK = RGBColor(0x1A, 0x1A, 0x1A)


def clean(text):
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def parse_timing(lines):
    timing = {}
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0].isdigit():
            timing[int(cells[0])] = {"name": cells[1], "start": cells[2], "dur": cells[3], "who": cells[4]}
    return timing


def parse_slides(text):
    blocks = re.split(r"\n(?=## \d+\.)", text)
    slides = []
    for b in blocks:
        m = re.match(r"## (\d+)\.\s*(.+)", b.strip())
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()
        dur = None
        mm = re.search(r"—\s*([0-9:]+)\s*$", title)
        if mm:
            dur = mm.group(1)
            title = title[: mm.start()].strip()
        msg = ""
        bullets = []
        for line in b.splitlines():
            s = line.strip()
            if s.startswith("**Thông điệp:**"):
                msg = clean(s.replace("**Thông điệp:**", ""))
            elif s.startswith("- "):
                item = clean(s[2:])
                if item and not item.startswith("[") and len(item) > 2:
                    bullets.append(item)
        slides.append({"num": num, "title": clean(title), "dur": dur, "msg": msg, "bullets": bullets})
    return slides


def add_footer(slide, num):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(7.05), Inches(9), Inches(0.3))
    p = box.text_frame.paragraphs[0]
    p.text = "Nhóm 01 · HR04 · 15DHTH07 · GMR"
    p.font.size = Pt(10)
    p.font.color.rgb = GREY
    box2 = slide.shapes.add_textbox(Inches(12.2), Inches(7.05), Inches(0.7), Inches(0.3))
    p2 = box2.text_frame.paragraphs[0]
    p2.text = str(num)
    p2.alignment = PP_ALIGN.RIGHT
    p2.font.size = Pt(10)
    p2.font.color.rgb = GREY


def build():
    lines = io.open(MD, encoding="utf-8").read().splitlines()
    timing = parse_timing(lines)
    slides = parse_slides(io.open(MD, encoding="utf-8").read())
    slides = [s for s in slides if 1 <= s["num"] <= 16]

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    for s in slides:
        slide = prs.slides.add_slide(blank)
        # thanh mau tren cung
        bar = slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACCENT
        bar.line.fill.background()

        # tieu de
        tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "%d. %s" % (s["num"], s["title"])
        p.font.size = Pt(30 if s["num"] not in (1,) else 36)
        p.font.bold = True
        p.font.color.rgb = ACCENT

        # thong diep
        top = 1.45
        if s["msg"]:
            mb = slide.shapes.add_textbox(Inches(0.6), Inches(1.35), Inches(12.1), Inches(0.6))
            mp = mb.text_frame.paragraphs[0]
            mp.text = s["msg"]
            mp.font.size = Pt(16)
            mp.font.italic = True
            mp.font.color.rgb = GREY
            top = 2.0

        # bullets
        bullets = s["bullets"][:5]
        if not bullets:
            bullets = ["(xem báo cáo)"]
        body = slide.shapes.add_textbox(Inches(0.8), Inches(top + 0.2), Inches(11.8), Inches(4.5))
        btf = body.text_frame
        btf.word_wrap = True
        for i, item in enumerate(bullets):
            p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(18 if len(item) < 90 else 16)
            p.font.color.rgb = DARK
            p.space_after = Pt(8)

        add_footer(slide, s["num"])

        # notes
        t = timing.get(s["num"], {})
        notes = []
        notes.append("Slide %d/%d" % (s["num"], len(slides)))
        if t:
            notes.append("Người nói: %s" % t["who"])
            notes.append("Thời lượng: %s (bắt đầu %s)" % (t["dur"], t["start"]))
        if s["msg"]:
            notes.append("Thông điệp: " + s["msg"])
        slide.notes_slide.notes_text_frame.text = "\n".join(notes)

    prs.save(OUT)
    print("saved", OUT, "slides", len(slides))
    for s in slides:
        print(s["num"], s["title"], "| bullets", len(s["bullets"]), "| dur", s["dur"])


if __name__ == "__main__":
    build()
