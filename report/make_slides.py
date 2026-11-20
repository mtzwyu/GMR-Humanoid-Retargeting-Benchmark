"""Dung report/slides.pptx theo he mau Teal Trust (16:9, 16 slide, 13:00).

Chay: python report/make_slides.py
Sau do QA bang LibreOffice -> PDF -> PNG (xem README/lenh trong phan bao cao).
"""
import os
import csv

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "results", "figures")
OUT = os.path.join(ROOT, "report", "slides.pptx")
ASSETS = os.path.join(ROOT, "report", "assets")

# Teal Trust
LIGHT = RGBColor(0xF7, 0xFA, 0xFB)
DARK = RGBColor(0x06, 0x34, 0x3C)
PRIMARY = RGBColor(0x02, 0x80, 0x90)
SECOND = RGBColor(0x00, 0xA8, 0x96)
ACCENT = RGBColor(0x02, 0xC3, 0x9A)
TEXT = RGBColor(0x12, 0x34, 0x3B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x4E, 0x6A, 0x70)
CARD = RGBColor(0xEA, 0xF4, 0xF5)

HEAD = "Cambria"
BODY = "Calibri"

SLIDES = [
    (1, "0:20", "Duy", "một repo, một tuyên bố, một phép đo"),
    (2, "0:20", "Duy", "13 phút đi từ bài toán đến kết luận"),
    (3, "1:10", "Duy", "paper đánh giá retargeter bằng policy phía sau"),
    (4, "0:50", "Duy", "phương án C: đo real-time và trình bày ba bảng paper"),
    (5, "0:50", "Duy", "chỉ đo được thời gian cả tiến trình, không phải retarget thuần"),
    (6, "0:50", "Duy", "hai cột tách bạch: paper không nêu, nhóm đo được 17,349 ms"),
    (7, "1:00", "Mạnh", "cài được trên Windows sau 4 lệnh và 6 sự cố"),
    (8, "1:00", "Mạnh", "5 lần đo, tất cả dưới ngưỡng 33,33 ms"),
    (9, "0:50", "Trường", "đổi khối lượng không đổi một byte pkl"),
    (10, "1:00", "Trường", "nhiễu khớp hỏng từ 2 độ, trễ và mất frame vô hại"),
    (11, "0:50", "Trường", "chất lượng chỉ so sánh tương đối, không có ngưỡng tuyệt đối"),
    (12, "0:50", "Trường", "2/3 robot dưới ngưỡng, PM01 chưa kết luận được"),
    (13, "0:40", "Trường", "H1 không dùng được trên đường BVH"),
    (14, "0:50", "Duy", "tái lập một phần: tốc độ được, bảng paper không"),
    (15, "0:40", "Duy", "bốn hạn chế phải nói thẳng"),
    (16, "1:00", "cả nhóm", "mời hỏi, 7 câu đã chuẩn bị"),
]

START = ["0:00", "0:20", "0:40", "1:50", "2:40", "3:30", "4:20", "5:20",
         "6:20", "7:10", "8:10", "9:00", "9:50", "10:30", "11:20", "12:00"]


def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def tb(slide, x, y, w, h, text, size=16, color=TEXT, bold=False, font=BODY,
       align=PP_ALIGN.LEFT, italic=False, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font
    r.font.color.rgb = color
    return box


def title(slide, text, dark=False, size=36):
    tb(slide, 0.6, 0.45, 12.1, 1.0, text, size=size,
       color=(WHITE if dark else PRIMARY), bold=True, font=HEAD)


def message(slide, text, dark=False):
    tb(slide, 0.6, 1.42, 12.1, 0.5, text, size=16, color=(ACCENT if dark else MUTED),
       italic=True)


def bullets(slide, items, x, y, w, h, dark=False, size=16, gap=10):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.05
        r = p.add_run()
        r.text = "•  " + item
        r.font.size = Pt(size)
        r.font.name = BODY
        r.font.color.rgb = (WHITE if dark else TEXT)


def flat(shp):
    for el in shp._element.findall(qn("p:style")):
        shp._element.remove(el)


def card(slide, x, y, w, h, fill=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.adjustments[0] = 0.06
    shp.fill.solid()
    shp.fill.fore_color.rgb = (fill if fill is not None else CARD)
    shp.line.fill.background()
    shp.shadow.inherit = False
    flat(shp)
    return shp


def stat(slide, number, label, x, y, w, h, dark=False, number_size=64):
    card(slide, x, y, w, h, fill=(RGBColor(0x0B, 0x45, 0x4E) if dark else CARD))
    tb(slide, x + 0.25, y + 0.18, w - 0.5, h * 0.55, number, size=number_size,
       color=(ACCENT if dark else PRIMARY), bold=True, font=HEAD)
    tb(slide, x + 0.25, y + h - 0.55, w - 0.5, 0.45, label, size=12,
       color=(WHITE if dark else MUTED))


def picture(slide, path, x, y, w, h, caption=None):
    im = Image.open(path)
    iw, ih = im.size
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    px = x + (w - dw) / 2
    py = y + (h - dh) / 2
    slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(dw), Inches(dh))
    if caption:
        tb(slide, x, y + h + 0.05, w, 0.3, caption, size=10, color=MUTED, italic=True)


def table(slide, rows, x, y, w, h, col_widths, header_fill=PRIMARY,
          font_size=11, header_size=11, first_col_bold=False, highlight_row=None):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    for i, cw in enumerate(col_widths):
        tbl.columns[i].width = Inches(cw)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = Inches(0.07)
            cell.margin_right = Inches(0.07)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = str(val)
            run.font.name = BODY
            if r == 0:
                run.font.size = Pt(header_size)
                run.font.bold = True
                run.font.color.rgb = WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_fill
            else:
                run.font.size = Pt(font_size)
                run.font.color.rgb = TEXT
                if first_col_bold and c == 0:
                    run.font.bold = True
                cell.fill.solid()
                if highlight_row is not None and r == highlight_row:
                    cell.fill.fore_color.rgb = RGBColor(0xD9, 0xF2, 0xEE)
                else:
                    cell.fill.fore_color.rgb = (WHITE if r % 2 else RGBColor(0xF1, 0xF7, 0xF8))
    return tbl


def footer(slide, n, dark=False):
    tb(slide, 0.6, 7.12, 8.0, 0.25, "Nhóm 01 · HR04 · 15DHTH07 · GMR", size=10,
       color=(RGBColor(0xB8, 0xD8, 0xD8) if dark else MUTED))
    tb(slide, 11.9, 7.12, 0.8, 0.25, str(n), size=10,
       color=(RGBColor(0xB8, 0xD8, 0xD8) if dark else MUTED), align=PP_ALIGN.RIGHT)


def notes(slide, n):
    _, dur, who, msg = SLIDES[n - 1]
    slide.notes_slide.notes_text_frame.text = (
        "Slide %d/16\nNgười nói: %s\nThời lượng: %s (bắt đầu %s)\nTổng: 13:00\nThông điệp: %s"
        % (n, who, dur, START[n - 1], msg)
    )


def make_charts():
    """Ve lai 2 bieu do voi dau phay thap phan, dung so trong CSV."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    os.makedirs(ASSETS, exist_ok=True)
    comma = FuncFormatter(lambda x, p: ("%.1f" % x).replace(".", ","))

    # V3
    path = os.path.join(ROOT, "results", "v3_runtime.csv")
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8-sig")) if r["phase"].startswith("measure")]
    vals = [float(r["ms_per_frame_process"]) for r in rows]
    fig, ax = plt.subplots(figsize=(7.4, 3.1), dpi=220)
    xs = list(range(1, len(vals) + 1))
    ax.plot(xs, vals, "o-", color="#028090", lw=2.4, ms=5)
    for x, v in zip(xs, vals):
        ax.annotate(("%.2f" % v).replace(".", ","), (x, v), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9, color="#12343B")
    ax.axhline(33.33, ls="--", color="#C0392B", lw=1.2)
    ax.text(len(vals), 34.4, "ngưỡng 33,33 ms", color="#C0392B", ha="right", fontsize=9)
    ax.set_ylim(15, 36)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(i) for i in xs])
    ax.set_xlabel("lần đo")
    ax.set_ylabel("ms/frame (cả tiến trình)")
    ax.yaxis.set_major_formatter(comma)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS, "v3_slide.png"), facecolor="white")
    plt.close(fig)

    # V5
    labels = ["T1 29dof", "G1", "PM01"]
    vals5 = [13.034, 16.758, 34.975]
    colors = ["#02C39A", "#028090", "#C0392B"]
    fig, ax = plt.subplots(figsize=(7.0, 3.2), dpi=220)
    bars = ax.bar(labels, vals5, color=colors)
    for b, v in zip(bars, vals5):
        ax.annotate(("%.3f" % v).replace(".", ","), (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 5), ha="center", fontsize=10,
                    color="#12343B")
    ax.axhline(33.33, ls="--", color="#C0392B", lw=1.2)
    ax.text(-0.45, 35.2, "ngưỡng 33,33 ms", color="#C0392B", ha="left", fontsize=9)
    ax.set_ylim(0, 40)
    ax.set_ylabel("ms/frame (cả tiến trình)")
    ax.yaxis.set_major_formatter(comma)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS, "v5_slide.png"), facecolor="white")
    plt.close(fig)


def build():
    make_charts()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    def new(dark=False):
        s = prs.slides.add_slide(blank)
        bg(s, DARK if dark else LIGHT)
        return s

    # 1 — bia
    s = new(True)
    tb(s, 0.7, 0.9, 11.8, 2.2,
       "GMR: Ánh xạ chuyển động người\nsang robot hình người theo thời gian thực",
       size=40, color=WHITE, bold=True, font=HEAD, spacing=1.0)
    tb(s, 0.7, 3.35, 11.8, 0.5,
       "Kiểm chứng tuyên bố “real time on CPU”", size=22, color=ACCENT, italic=True)
    tb(s, 0.7, 3.95, 11.8, 0.4,
       "Nhóm 01 · HR04 · Lớp 15DHTH07 · HK1 2026–2027", size=16, color=WHITE)
    stat(s, "25f56db", "GMR commit", 0.7, 5.25, 3.6, 1.35, dark=True, number_size=40)
    stat(s, "MIT", "Giấy phép mã nguồn", 4.55, 5.25, 3.6, 1.35, dark=True, number_size=40)
    stat(s, "13:00", "Tổng thời lượng", 8.4, 5.25, 3.6, 1.35, dark=True, number_size=40)
    footer(s, 1, dark=True)
    notes(s, 1)

    # 2 — noi dung
    s = new()
    title(s, "Nội dung 13 phút")
    message(s, "Một mạch: bài toán → cách đo → kết quả → kết luận")
    stat(s, "13:00", "tổng thời lượng trình bày", 9.4, 1.9, 3.2, 1.6, number_size=60)
    items = [
        ("0–3′", "Bài toán, paper và tuyên bố cần kiểm chứng"),
        ("3–6′", "Định nghĩa phép đo, bảng hai cột, V2"),
        ("6–12′", "V3, độ bền nhiễu, chất lượng ánh xạ, sim2sim"),
        ("12–13′", "Kết luận, hạn chế và Q&A"),
    ]
    y = 2.0
    for i, (t, txt) in enumerate(items):
        card(s, 0.7, y, 8.2, 1.05, fill=CARD)
        tb(s, 0.95, y + 0.18, 1.3, 0.4, t, size=18, color=PRIMARY, bold=True, font=HEAD)
        tb(s, 2.2, y + 0.22, 6.4, 0.6, txt, size=15, color=TEXT)
        y += 1.25
    footer(s, 2)
    notes(s, 2)

    # 3 — bai toan + paper
    s = new()
    title(s, "Bài toán & bài báo")
    message(s, "Paper không so retargeter bằng mắt, mà bằng policy chạy phía sau")
    bullets(s, [
        "Retargeting: ánh xạ quỹ đạo người sang quỹ đạo khớp robot",
        "4 nguồn retargeting × 21 clip LAFAN1, cùng Unitree G1",
        "Mỗi file retarget huấn luyện một policy BeyondMimic",
        "Ba bảng I/II/III đều đo policy đã train, không đo tốc độ",
    ], 0.7, 2.15, 8.0, 4.2, size=17, gap=18)
    stat(s, "84", "policy = 21 clip × 4 phương pháp", 9.1, 2.0, 3.5, 1.7, number_size=72)
    tb(s, 9.1, 3.95, 3.5, 1.4,
       "Cần GPU + IsaacSim + 84 policy — ngoài phạm vi 10 ngày.",
       size=14, color=TEXT)
    card(s, 0.7, 5.55, 11.9, 0.95, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 5.75, 11.4, 0.55,
       "Paper không công bố ms/frame, FPS hay cấu hình — chỉ có ba bảng kết quả policy.",
       size=15, color=TEXT, bold=True)
    footer(s, 3)
    notes(s, 3)

    # 4 — tuyen bo
    s = new()
    title(s, "Tuyên bố kiểm chứng — phương án C")
    message(s, "Đo phần đo được, trình bày thẳng phần không tái lập được")
    rows = [
        ["", "Nội dung", "Vấn đề"],
        ["A", "Chỉ đo real-time, ghi paper không nêu", "Yếu chữ “trong bài báo”"],
        ["B", "Chuyển sang Bảng II (104,1 mm)", "Gần chắc chắn thất bại, không có số mới"],
        ["C", "Đo real-time + trình bày 3 bảng paper", "Báo cáo dài thêm ~1 trang"],
    ]
    table(s, rows, 0.7, 2.0, 11.9, 2.3, [0.7, 6.5, 4.7], font_size=14, header_size=13, highlight_row=3)
    tb(s, 0.7, 4.40, 11.9, 0.6,
       "Ngưỡng 33,33 ms là ngưỡng của nhóm (1000/30 từ LAFAN1), không phải ngưỡng của paper.",
       size=15, color=TEXT, italic=True)
    card(s, 0.7, 5.15, 11.9, 0.95, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 5.38, 11.4, 0.5,
       "Nguồn tuyên bố: README/mô tả repo — paper không công bố ms/frame hay FPS.",
       size=15, color=TEXT, bold=True)
    footer(s, 4)
    notes(s, 4)

    # 5 — dinh nghia
    s = new()
    title(s, "Định nghĩa phép đo")
    message(s, "Hai đại lượng khác nghĩa, không được gọi lẫn")
    rows = [
        ["Đại lượng", "Đo cái gì", "Dùng để"],
        ["ms_per_frame", "Chỉ vòng lặp retarget()", "Đại lượng của tuyên bố"],
        ["ms_per_frame_process", "Cả tiến trình: init + viewer + render + ghi pkl", "Cận trên bảo thủ; V3 chỉ có số này"],
    ]
    table(s, rows, 0.7, 2.0, 11.9, 1.7, [3.0, 5.0, 3.9], font_size=14, header_size=13, first_col_bold=True)
    tb(s, 0.7, 4.0, 11.9, 0.4, "Quy tắc thống kê (chốt trước khi đo)", size=16, bold=True, color=PRIMARY)
    bullets(s, [
        "CV ≤ 5 %: báo trung bình — V3 17,349 · G1 16,758 · PM01 34,975",
        "CV > 5 %: báo trung vị — chỉ T1 13,034 (CV 11,32 %)",
        "Ngưỡng 33,33 ms áp cho ms_per_frame; thiếu số thì dùng bảng bắc cầu §6.1",
    ], 0.7, 4.45, 9.5, 1.6, size=15)
    stat(s, "33,33", "ngưỡng ms/frame", 10.7, 4.55, 2.0, 1.3, number_size=34)
    footer(s, 5)
    notes(s, 5)

    # 6 — bang 2 cot
    s = new()
    title(s, "Bảng hai cột: paper và nhóm đo")
    message(s, "Cột paper không nêu tốc độ; cột nhóm chỉ có số cả tiến trình")
    rows = [
        ["Đại lượng", "Bài báo", "Nhóm đo được"],
        ["V3 · ms/frame cả tiến trình", "không nêu", "17,349 ms (mean, n=5, CV 2,13 %)"],
        ["V3 · realtime_factor", "không nêu", "1,92"],
        ["V5 · T1 29dof", "—", "13,034 ms (median) → 2,56"],
        ["V5 · G1", "—", "16,758 ms → 1,99"],
        ["V5 · PM01", "—", "34,975 ms → 0,95"],
        ["Bảng I/II/III của paper", "51 % · 104,1 mm · 64→100 %", "không đo — ngoài phạm vi"],
    ]
    table(s, rows, 0.7, 2.0, 11.9, 3.9, [4.3, 3.6, 4.0], font_size=13, header_size=12, first_col_bold=True)
    tb(s, 0.7, 6.1, 11.9, 0.4, "Dấu “—” nghĩa là paper chỉ dùng G1 và không công bố tốc độ.",
       size=12, color=MUTED, italic=True)
    footer(s, 6)
    notes(s, 6)

    # 7 — V2
    s = new()
    title(s, "V2 — cài đặt trên Windows")
    message(s, "4 lệnh README, 11 mục nhật ký, 6 sự cố — chuyển sang BVH LAFAN1")
    stat(s, "4", "lệnh cài đặt theo README", 0.7, 2.1, 3.7, 1.8, number_size=72)
    stat(s, "11", "mục nhật ký cài đặt", 4.8, 2.1, 3.7, 1.8, number_size=72)
    stat(s, "6", "sự cố đã xử lý", 8.9, 2.1, 3.7, 1.8, number_size=72)
    bullets(s, [
        "Windows 11 · Python 3.10 · MuJoCo 3.17, chạy CPU",
        "SMPL-X cần license → chuyển sang BVH LAFAN1 công khai",
        "requirements.txt 45 dòng, ghim proxsuite 0.7.2.post1",
        "Log từng lần chạy có dòng END để đối chiếu ngược",
    ], 0.7, 4.35, 11.9, 2.3, size=16, gap=12)
    tb(s, 0.7, 6.45, 11.9, 0.3, "Nguồn: logs/nhat_ky_cai_dat.md", size=11, color=MUTED, italic=True)
    footer(s, 7)
    notes(s, 7)

    # 8 — V3
    s = new()
    title(s, "V3 — kết quả đo")
    message(s, "5 lần đo độc lập, tất cả dưới ngưỡng 33,33 ms")
    picture(s, os.path.join(ASSETS, "v3_slide.png"), 0.7, 2.0, 7.6, 4.2,
            caption="Nguồn: results/v3_runtime.csv — 5 lần đo, bỏ warm-up")
    stat(s, "17,349", "ms/frame · mean n=5 · CV 2,13 %", 8.7, 2.0, 3.9, 1.8, number_size=60)
    stat(s, "57,6", "FPS · realtime_factor 1,92", 8.7, 4.05, 3.9, 1.6, number_size=60)
    tb(s, 8.7, 5.85, 3.9, 0.6, "Biên độ 16,853–17,852 ms", size=12, color=MUTED, italic=True)
    footer(s, 8)
    notes(s, 8)

    # 9 — khong physics
    s = new()
    title(s, "Vì sao không thử nhiễu vật lý")
    message(s, "GMR là tối ưu động học: khối lượng không đi vào vòng tính")
    stat(s, "0 byte", "đầu ra thay đổi khi đổi khối lượng", 0.7, 2.0, 4.6, 2.0, number_size=60)
    bullets(s, [
        "Không có mass, friction hay lực tiếp xúc trong vòng lặp",
        "40 file pkl: 37 thuộc 4 cặp trùng hash, 3 file lẻ",
        "Vì vậy bảng “tụt theo ±20 % khối lượng” sẽ là bảng giả",
        "Thay bằng N1–N4: nhiễu khớp, trễ, mất frame, lệch tỉ lệ người",
    ], 5.7, 2.0, 7.0, 3.0, size=15)
    labels = [("N1", "nhiễu khớp"), ("N2", "trễ điều khiển"), ("N3", "mất frame"), ("N4", "lệch tỉ lệ người")]
    for i, (code, name) in enumerate(labels):
        x = 0.7 + i * 3.05
        card(s, x, 5.15, 2.85, 0.9, fill=RGBColor(0xD9, 0xF2, 0xEE))
        tb(s, x + 0.2, 5.28, 0.7, 0.4, code, size=20, color=PRIMARY, bold=True, font=HEAD)
        tb(s, x + 0.9, 5.35, 1.8, 0.5, name, size=13, color=TEXT)
    footer(s, 9)
    notes(s, 9)

    # 10 — V6 nhieu
    s = new()
    title(s, "V6 — độ bền theo nhiễu")
    message(s, "Nhiễu khớp hỏng từ 2°/kênh; trễ và mất frame gần như vô hại")
    picture(s, os.path.join(FIG, "v6_noise_slide.png"), 0.7, 1.95, 7.8, 4.6,
            caption="Nguồn: results/v6_noise_sweep.csv — 15 mức, 1 lần/mức")
    bullets(s, [
        "N1: 0,5° an toàn; 2° làm 87,7 % frame lệch > 5°",
        "N2: trễ 1–5 frame chỉ lệch pha (dq_mean 0,001°)",
        "N3: mất frame ≤ 10 % — pct lệch ≤ 0,31 %",
        "N4: ±10 % bất đối xứng, giãn nặng hơn co",
    ], 8.8, 2.0, 3.9, 4.2, size=14)
    footer(s, 10)
    notes(s, 10)

    # 11 — chat luong
    s = new()
    title(s, "Chất lượng ánh xạ — 3 robot")
    message(s, "foot_slide ≤ 50 mm/s: G1 49,0 đạt sát · T1 83,1 và PM01 118,4 không đạt")
    rows = [
        ["Robot", "foot_slide", "min_body_height (mm)", "ít nhất 1 body <−1mm", "sát giới hạn"],
        ["G1", "49,0", "+9,9", "0 %", "23,8 %"],
        ["T1 29dof", "83,1", "−7,6", "2,13 %", "43,3 %"],
        ["PM01", "118,4", "+43,8", "0 %", "24,1 %"],
    ]
    table(s, rows, 0.6, 2.0, 11.9, 2.1, [2.0, 2.3, 2.0, 2.8, 2.8], font_size=12, header_size=11, first_col_bold=True)
    picture(s, os.path.join(FIG, "v6_quality.png"), 0.6, 4.35, 5.2, 2.1,
            caption="Nguồn: results/v6_quality.csv")
    bullets(s, [
        "foot_slide là proxy, đo ở gốc body bàn chân — không phải “trượt tuyệt đối”",
        "pct frame có ít nhất một body gốc <−1 mm là proxy, không phải bề mặt/mesh",
        "min_body_height phụ thuộc offset nghỉ từng model; ngưỡng đã rút hậu kiểm DEC-03",
    ], 6.0, 4.40, 6.7, 2.2, size=13, gap=8)
    footer(s, 11)
    notes(s, 11)

    # 12 — sim2sim
    s = new()
    title(s, "Sim2sim — cùng motion, 3 robot")
    message(s, "Giữ simulator, đổi embodiment, không huấn luyện lại")
    picture(s, os.path.join(ASSETS, "v5_slide.png"), 0.7, 1.95, 7.2, 4.4,
            caption="Nguồn: results/v5_sim2sim.csv — mean/median theo CV")
    stat(s, "13,034", "T1 29dof · 2,56×", 8.2, 1.95, 4.4, 1.40, number_size=32)
    stat(s, "16,758", "G1 · 1,99×", 8.2, 3.45, 4.4, 1.40, number_size=32)
    stat(s, "34,975", "PM01 · 0,95× — chưa kết luận", 8.2, 4.95, 4.4, 1.40, number_size=32)
    footer(s, 12)
    notes(s, 12)

    # 13 — H1
    s = new()
    title(s, "H1 bị chặn — và H1_2")
    message(s, "Không có config BVH cho H1/H1_2; đường SMPL-X bị license chặn")
    stat(s, "exit 2", "argparse từ chối --robot unitree_h1", 0.7, 2.0, 4.4, 1.8, number_size=54)
    bullets(s, [
        "Không có ik_configs/bvh_lafan1_to_h1.json; README để cột BVH = TBD",
        "Lỗi xảy ra trước khi nạp model — không phải lỗi runtime",
        "H1_2 cũng không có config BVH; Xsens 120 Hz chỉ dùng smoke-test",
        "Vì vậy V5 dừng ở 3 robot: G1, T1 29dof, PM01",
    ], 5.5, 2.0, 7.2, 3.0, size=15)
    card(s, 0.7, 4.55, 11.9, 1.15, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 4.72, 11.4, 0.45,
       "Muốn chạy H1 phải có config BVH hoặc license SMPL-X — cả hai đều ngoài phạm vi giai đoạn 1.",
       size=15, color=TEXT, bold=True)
    tb(s, 0.95, 5.18, 11.4, 0.4,
       "Vì vậy V5 chỉ báo cáo G1, T1 29dof và PM01.", size=14, color=MUTED)
    footer(s, 13)
    notes(s, 13)

    # 14 — ket luan (dark)
    s = new(True)
    title(s, "Kết luận", dark=True, size=40)
    message(s, "Phần thời gian thực tái lập được; ba bảng số của paper thì không", dark=True)
    tb(s, 0.7, 2.1, 11.9, 1.2,
       "Tái lập một phần", size=54, color=ACCENT, bold=True, font=HEAD)
    stat(s, "17,349", "ms/frame · 1,92× · 57,6 FPS", 0.7, 4.35, 3.7, 1.7, dark=True, number_size=40)
    stat(s, "2/3", "robot dưới ngưỡng 33,33 ms", 4.8, 4.35, 3.7, 1.7, dark=True, number_size=40)
    stat(s, "0", "bảng paper tái lập được", 8.9, 4.35, 3.7, 1.7, dark=True, number_size=40)
    footer(s, 14, dark=True)
    notes(s, 14)

    # 15 — han che
    s = new()
    title(s, "Hạn chế & hướng tiếp")
    message(s, "Bốn điều phải nói thẳng — không lấp bằng lời")
    stat(s, "4", "hạn chế đã ghi trong báo cáo", 9.4, 1.95, 3.2, 1.7, number_size=72)
    bullets(s, [
        "Chưa đo ms_per_frame — chỉ có số cả tiến trình",
        "Chất lượng: chỉ 1/3 robot đạt ngưỡng foot_slide ≤ 50 mm/s",
        "Một máy Windows, chưa xác minh CUDA_VISIBLE_DEVICES",
        "N4 còn bất đối xứng chưa tách định lượng",
    ], 0.7, 2.0, 8.3, 3.0, size=15)
    steps = [("Probe", "đo ms_per_frame"), ("Máy 2", "kiểm tra CPU khác"), ("Ngưỡng", "chốt cho chất lượng")]
    for i, (head, sub) in enumerate(steps):
        x = 0.7 + i * 4.05
        card(s, x, 4.95, 3.85, 1.1, fill=RGBColor(0xD9, 0xF2, 0xEE))
        tb(s, x + 0.2, 5.08, 3.4, 0.4, head, size=16, color=PRIMARY, bold=True, font=HEAD)
        tb(s, x + 0.2, 5.5, 3.4, 0.4, sub, size=13, color=TEXT)
    footer(s, 15)
    notes(s, 15)

    # 16 — cam on
    s = new()
    title(s, "Cảm ơn — Q&A")
    message(s, "7 câu đã chuẩn bị; mời hỏi thẳng vào số liệu")
    tb(s, 0.7, 1.9, 5.2, 2.2, "Q&A", size=72, color=PRIMARY, bold=True, font=HEAD)
    tb(s, 0.7, 4.15, 5.2, 0.8, "7 câu", size=60, color=ACCENT, bold=True, font=HEAD)
    bullets(s, [
        "Vì sao không đo ms_per_frame?",
        "Vì sao không train 3 seed?",
        "PM01 chậm vì ít khớp?",
        "Nhiễu trễ có 36° ở frame 0 — lỗi tích lũy?",
        "Sim2sim không đúng nhiễu vật lý?",
        "Hai đợt lệch 14 %, số nào tin?",
        "So với paper thế nào?",
    ], 6.2, 1.95, 6.5, 4.2, size=15, gap=10)
    tb(s, 6.2, 5.75, 6.5, 0.5, "Nhóm 01 · HR04 · 15DHTH07", size=13, color=MUTED)
    footer(s, 16)
    notes(s, 16)

    prs.save(OUT)
    print("saved", OUT, "slides", len(prs.slides))


if __name__ == "__main__":
    build()
