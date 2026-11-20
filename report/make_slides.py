"""Dung report/slides.pptx theo he mau Teal Trust (16:9, 16 slide, 13:00).

Chay: python report/make_slides.py
Sau do QA bang LibreOffice -> PDF -> PNG (xem README/lenh trong phan bao cao).
"""
import csv
import os

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
    (2, "0:40", "Duy", "tuyên bố nằm ở README, không nằm trong bài báo"),
    (3, "1:00", "Duy", "retargeting là ánh xạ hình thái, không copy góc khớp"),
    (4, "1:00", "Duy", "paper đánh giá retargeter bằng 84 policy phía sau"),
    (5, "0:50", "Duy", "paper không có số tốc độ → phương án C"),
    (6, "0:40", "Duy", "một câu chốt, một ngưỡng đặt trước"),
    (7, "1:10", "Mạnh", "7 sự cố, 1 quyết định: bỏ SMPL-X sang BVH LAFAN1"),
    (8, "0:50", "Mạnh", "tách ms_per_frame và ms_per_frame_process"),
    (9, "0:50", "Mạnh", "5 lần đo, tất cả dưới 33,33 ms"),
    (10, "0:40", "Duy", "process ≤ 33,33 ms là điều kiện đủ"),
    (11, "1:00", "Trường", "cùng motion, 3 robot, 2/3 dưới ngưỡng"),
    (12, "0:30", "Trường", "PM01 chậm nhất dù ít khớp nhất"),
    (13, "1:00", "Trương Thái Vỹ + Hà Mạnh Trường", "khối lượng không đổi pkl → thay bằng N1–N4"),
    (14, "0:50", "Duy", "tốc độ tái lập được, chất lượng một phần"),
    (15, "0:40", "Duy", "ba bài học và việc còn mở"),
    (16, "1:00", "cả nhóm", "mời hỏi, 7 câu đã chuẩn bị"),
]

START = ["0:00", "0:20", "1:00", "2:00", "3:00", "3:50", "4:30", "5:40",
         "6:30", "7:20", "8:00", "9:00", "9:30", "10:30", "11:20", "12:00"]


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

    # 1 — bìa
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

    # 2 — hook
    s = new()
    title(s, "Hook — một câu của repo")
    message(s, "Tuyên bố nằm ở README, không nằm trong bài báo — và đó là chỗ bắt đầu")
    card(s, 0.7, 2.05, 7.2, 1.55, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 2.25, 6.7, 1.2,
       "“Retarget human motions into diverse humanoid robots in real time on CPU”",
       size=21, color=TEXT, italic=True)
    tb(s, 0.95, 3.42, 6.7, 0.3, "— README của YanjieZe/GMR", size=12, color=MUTED)
    bullets(s, [
        "Bài báo 9 trang: không có một con số ms/frame hay FPS nào",
        "Repo lại tuyên bố “real time on CPU” — kiểm chứng được",
        "Câu hỏi của nhóm: tuyên bố đó đứng được trên máy CPU phổ thông?",
    ], 0.7, 4.0, 7.0, 2.2, size=15, gap=14)
    picture(s, os.path.join(FIG, "v3_render_mujoco_g1_2026-11-20.png"),
            8.2, 1.95, 4.5, 4.3, caption="G1 trong MuJoCo — ảnh do nhóm chạy")
    footer(s, 2)
    notes(s, 2)

    # 3 — bài toán
    s = new()
    title(s, "Bài toán retargeting")
    message(s, "Ánh xạ hình thái, không phải copy góc khớp")
    steps = [("Người", "mocap · 3D joints"), ("Retargeting", "tối ưu IK"), ("Robot", "qpos 29 DoF")]
    for i, (head, sub) in enumerate(steps):
        x = 0.7 + i * 4.15
        card(s, x, 2.0, 3.7, 1.25, fill=CARD)
        tb(s, x + 0.2, 2.14, 3.3, 0.45, head, size=22, color=PRIMARY, bold=True, font=HEAD)
        tb(s, x + 0.2, 2.62, 3.3, 0.4, sub, size=13, color=MUTED)
        if i < 2:
            tb(s, x + 3.72, 2.3, 0.45, 0.5, "→", size=26, color=ACCENT, bold=True)
    bullets(s, [
        "Embodiment gap: cùng chuyển động, khác chiều dài khâu và DOF",
        "Ràng buộc vật lý: sàn, tự cắt, giật — không chỉ khớp góc",
        "Thời gian thực: ngân sách 33,33 ms/frame ở nguồn 30 fps",
    ], 0.7, 3.65, 8.6, 2.4, size=16, gap=16)
    stat(s, "33,33", "ms/frame ngân sách", 9.9, 3.8, 2.7, 1.4, number_size=38)
    tb(s, 9.9, 5.35, 2.7, 0.8,
       "Ngân sách của dữ liệu nguồn, không phải ngưỡng của paper.",
       size=11, color=MUTED, italic=True)
    footer(s, 3)
    notes(s, 3)

    # 4 — paper làm gì
    s = new()
    title(s, "Paper làm gì")
    message(s, "Paper không so retargeter bằng mắt, mà bằng policy chạy phía sau")
    bullets(s, [
        "4 nguồn: GMR · PHC · ProtoMotions · Unitree (closed)",
        "Cùng 21 clip LAFAN1, cùng Unitree G1",
        "Mỗi file retarget huấn luyện một policy BeyondMimic",
        "100 / 4096 / 100 rollout; ba bảng success · error · start frame",
    ], 0.7, 2.1, 8.1, 3.4, size=16, gap=16)
    stat(s, "84", "policy = 21 clip × 4 phương pháp", 9.1, 2.0, 3.5, 1.7, number_size=72)
    tb(s, 9.1, 3.95, 3.5, 1.3,
       "Cần GPU + IsaacSim + 84 policy — ngoài phạm vi 10 ngày.",
       size=14, color=TEXT)
    card(s, 0.7, 5.5, 11.9, 1.0, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 5.72, 11.4, 0.6,
       "Ba bảng I/II/III đều đo policy đã train — không đo tốc độ retargeting.",
       size=15, color=TEXT, bold=True)
    footer(s, 4)
    notes(s, 4)

    # 5 — nghịch lý
    s = new()
    title(s, "Nghịch lý: paper không có số tốc độ")
    message(s, "Muốn kiểm chứng bài báo, nhưng bài báo không có số FPS → phương án C")
    rows = [
        ["", "Nội dung", "Vấn đề"],
        ["A", "Chỉ đo real-time, ghi paper không nêu", "Yếu chữ “trong bài báo”"],
        ["B", "Chuyển sang Bảng II (104,1 mm)", "Gần chắc chắn thất bại, không có số mới"],
        ["C", "Đo real-time + trình bày 3 bảng paper", "Báo cáo dài thêm ~1 trang"],
    ]
    table(s, rows, 0.7, 2.0, 11.9, 2.3, [0.7, 6.5, 4.7], font_size=14, header_size=13, highlight_row=3)
    tb(s, 0.7, 4.4, 11.9, 0.5,
       "Ghi chú: không gọi clip 261,3 s là “Walk 1” của Bảng I (33 s).",
       size=14, color=TEXT, italic=True)
    card(s, 0.7, 5.1, 11.9, 1.0, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 5.32, 11.4, 0.55,
       "Nguồn tuyên bố: README repo. Paper chỉ có ba bảng kết quả policy.",
       size=15, color=TEXT, bold=True)
    footer(s, 5)
    notes(s, 5)

    # 6 — tuyên bố + ngưỡng
    s = new()
    title(s, "Tuyên bố + ngưỡng đặt trước")
    message(s, "Một câu chốt, một ngưỡng, một cách đọc duy nhất")
    card(s, 0.7, 2.0, 7.5, 1.9, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 2.18, 7.0, 1.5,
       "GMR tuyên bố retarget chuyển động người sang humanoid “theo thời gian thực trên CPU”.",
       size=19, color=TEXT, bold=True)
    tb(s, 0.7, 4.15, 11.9, 0.5,
       "ms_per_frame ≤ 33,33 ms  ⇔  fps_out ≥ 30  ⇔  realtime_factor ≥ 1,00",
       size=20, color=PRIMARY, bold=True, font=HEAD)
    labels = [
        ("≥ 1,00", "tái lập được"),
        ("0,80 – 0,99", "tái lập một phần"),
        ("< 0,80", "không tái lập được"),
    ]
    for i, (value, label) in enumerate(labels):
        x = 0.7 + i * 4.05
        card(s, x, 4.95, 3.85, 1.15, fill=CARD)
        tb(s, x + 0.2, 5.05, 3.4, 0.45, value, size=24, color=PRIMARY, bold=True, font=HEAD)
        tb(s, x + 0.2, 5.55, 3.4, 0.4, label, size=13, color=MUTED)
    tb(s, 0.7, 6.35, 11.9, 0.4,
       "Ngưỡng chốt trước, không đổi sau khi thấy số.", size=13, color=MUTED, italic=True)
    footer(s, 6)
    notes(s, 6)

    # 7 — cài đặt
    s = new()
    title(s, "V2 — cài đặt trên Windows")
    message(s, "4 lệnh README · 15 mục nhật ký · 7 sự cố — quyết định: bỏ SMPL-X sang BVH LAFAN1")
    stat(s, "4", "lệnh cài đặt theo README", 0.7, 1.95, 3.7, 1.6, number_size=64)
    stat(s, "15", "mục nhật ký cài đặt", 4.8, 1.95, 3.7, 1.6, number_size=64)
    stat(s, "7", "sự cố đã xử lý", 8.9, 1.95, 3.7, 1.6, number_size=64)
    bullets(s, [
        "Timeline: proxsuite · libstdcxx · SMPL-X license · KI-01 · KI-02 · RV-14 · lệch 14 %",
        "SMPL-X cần license → chuyển sang BVH LAFAN1 công khai; H1 bị chặn",
        "Windows 11 · Python 3.10 · MuJoCo 3.17, chạy CPU; log có dòng END",
    ], 0.7, 3.85, 11.9, 1.7, size=15, gap=12)
    picture(s, os.path.join(FIG, "slide_v3_walk4_g1_f900.png"), 0.7, 5.35, 2.6, 1.2,
            caption="KI-01: clip gốc khom lưng")
    picture(s, os.path.join(FIG, "slide_v3_walk1_g1_f900.png"), 3.5, 5.35, 2.6, 1.2,
            caption="walk1: tư thế chuẩn")
    tb(s, 6.4, 5.7, 6.2, 1.2,
       "Bài học KI-02: cột cmd ghi cờ chưa từng truyền — Review phát hiện, không phải người viết.",
       size=13, color=TEXT, italic=True)
    footer(s, 7)
    notes(s, 7)

    # 8 — đo cái gì
    s = new()
    title(s, "Đo cái gì: process vs retarget")
    message(s, "Script chạy retarget và render chung một vòng lặp, nên phải tách hai đại lượng")
    rows = [
        ["Đại lượng", "Đo cái gì", "Dùng để"],
        ["ms_per_frame", "Chỉ vòng lặp retarget()", "Đại lượng của tuyên bố"],
        ["ms_per_frame_process", "Cả tiến trình: init + viewer + render + ghi pkl", "Cận trên bảo thủ; V3 chỉ có số này"],
    ]
    table(s, rows, 0.7, 2.0, 11.9, 1.7, [3.0, 5.0, 3.9], font_size=14, header_size=13, first_col_bold=True)
    bullets(s, [
        "Giai đoạn 1 chỉ có _process (bản đo 13 cột); probe retarget có nhưng chưa chạy lại",
        "Cấm dùng “Actual rendering FPS”; cấm nhân hệ số 0,92",
        "Ngưỡng áp cho ms_per_frame; thiếu số thì dùng bảng bắc cầu",
    ], 0.7, 4.05, 9.6, 2.0, size=15, gap=12)
    stat(s, "33,33", "ngưỡng ms/frame", 10.7, 4.2, 2.0, 1.3, number_size=34)
    footer(s, 8)
    notes(s, 8)

    # 9 — V3
    s = new()
    title(s, "V3 — kết quả đo")
    message(s, "5 lần đo, tất cả dưới ngưỡng 33,33 ms, độ tản mát thấp")
    picture(s, os.path.join(ASSETS, "v3_slide.png"), 0.7, 1.95, 7.4, 4.1,
            caption="Nguồn: results/v3_runtime.csv — 5 lần đo, bỏ warm-up")
    stat(s, "17,349", "ms/frame · mean n=5 · CV 2,13 %", 8.5, 1.95, 4.1, 1.7, number_size=52)
    stat(s, "57,6", "FPS · realtime_factor 1,92", 8.5, 3.8, 4.1, 1.5, number_size=52)
    tb(s, 8.5, 5.45, 4.1, 0.8,
       "5 điểm: 17,522 · 17,246 · 17,852 · 16,853 · 17,272",
       size=12, color=MUTED, italic=True)
    tb(s, 0.7, 6.45, 11.9, 0.4,
       "Mốc README repo: 35–45 FPS (i9-13900K) · 60–70 FPS (Threadripper) — không nêu điều kiện đo.",
       size=12, color=MUTED)
    footer(s, 9)
    notes(s, 9)

    # 10 — bắc cầu
    s = new()
    title(s, "Bắc cầu: được kết luận gì")
    message(s, "process ≤ 33,33 là điều kiện đủ, không phải suy diễn")
    card(s, 0.7, 2.0, 11.9, 1.35, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 2.2, 11.4, 0.9,
       "retarget ≤ process = 17,349 ms ≤ 33,33 ms",
       size=30, color=PRIMARY, bold=True, font=HEAD)
    bullets(s, [
        "Kết luận: tái lập được ở mức cả tiến trình",
        "Không được nói “vòng lặp retarget đạt real-time” — không đo trực tiếp",
        "Hai phiên lệch ≈ 14 % → báo 17,3 ms, không 17,35",
    ], 0.7, 3.6, 11.9, 2.2, size=16, gap=14)
    tb(s, 0.7, 6.0, 11.9, 0.6,
       "Đây là slide phương pháp: không nhân hệ số, không suy ngược từ số không có.",
       size=13, color=MUTED, italic=True)
    footer(s, 10)
    notes(s, 10)

    # 11 — sim2sim
    s = new()
    title(s, "Sim2sim — cùng motion, 3 robot")
    message(s, "Giữ simulator, đổi embodiment, không huấn luyện lại — 2/3 robot dưới ngưỡng")
    picture(s, os.path.join(ASSETS, "v5_slide.png"), 0.7, 1.9, 6.7, 3.5,
            caption="Nguồn: results/v5_sim2sim.csv — mean/median theo CV")
    stat(s, "16,758", "G1 · 1,99×", 7.6, 1.9, 4.9, 1.15, number_size=28)
    stat(s, "13,034", "T1 29dof · 2,56×", 7.6, 3.15, 4.9, 1.15, number_size=28)
    stat(s, "34,975", "PM01 · 0,95× — chưa kết luận", 7.6, 4.4, 4.9, 1.15, number_size=28)
    card(s, 0.7, 5.85, 11.9, 0.95, fill=RGBColor(0xD9, 0xF2, 0xEE))
    tb(s, 0.95, 6.02, 11.4, 0.6,
       "H1 bị chặn trên đường BVH: exit 2 “invalid choice”, không có config, README ghi TBD.",
       size=13, color=TEXT, bold=True)
    footer(s, 11)
    notes(s, 11)

    # 12 — vì sao PM01 chậm
    s = new()
    title(s, "Vì sao PM01 chậm")
    message(s, "Ít khớp nhất mà chậm nhất → số DoF không giải thích được")
    stat(s, "24 DoF", "PM01 · 34,975 ms (mean)", 0.7, 2.0, 4.4, 1.7, number_size=40)
    stat(s, "27 DoF", "T1 29dof · 13,034 ms (median)", 5.4, 2.0, 4.4, 1.7, number_size=40)
    stat(s, "2,8×", "so cùng mean với T1", 10.1, 2.0, 2.5, 1.7, number_size=44)
    hyps = [
        ("Cấu hình IK", "khác tỉ lệ khâu, khác điểm bám"),
        ("Số vòng lặp solver", "hội tụ chậm hơn trên PM01"),
        ("Mô hình nặng", "nhiều geom/mesh hơn"),
    ]
    for i, (head, sub) in enumerate(hyps):
        x = 0.7 + i * 4.05
        card(s, x, 4.15, 3.85, 1.2, fill=CARD)
        tb(s, x + 0.2, 4.28, 3.4, 0.4, head, size=15, color=PRIMARY, bold=True, font=HEAD)
        tb(s, x + 0.2, 4.72, 3.4, 0.5, sub, size=12, color=MUTED)
    tb(s, 0.7, 5.65, 11.9, 0.5,
       "Nhãn đỏ: đây là GIẢ THUYẾT, chưa tách nguyên nhân. Đã kiểm soát thermal (PM01 chạy đầu, 51–57 °C).",
       size=13, color=RGBColor(0xB0, 0x3A, 0x2E), bold=True)
    footer(s, 12)
    notes(s, 12)

    # 13 — nhiễu N1–N4
    s = new()
    title(s, "Nhiễu: vì sao không dùng ±20 % khối lượng")
    message(s, "Đổi khối lượng không đổi một byte pkl → phép thử đó sẽ là bảng giả")
    picture(s, os.path.join(FIG, "v6_noise_slide.png"), 0.6, 1.85, 7.2, 4.05,
            caption="Nguồn: results/v6_noise_sweep.csv — 15 mức, 1 lần/mức")
    bullets(s, [
        "GMR tối ưu động học: không có mass/friction trong vòng tính",
        "SHA256: 40 pkl — 37 thuộc 4 cặp trùng hash, 3 file lẻ",
        "Thay bằng N1–N4: khớp · trễ · mất frame · lệch tỉ lệ người",
        "N1 hỏng từ 2° (87,7 % frame) · N2/N3 vô hại · N4 hỏng từ ±10 %",
        "dr_rmse 719 mm của N4 là scale quỹ đạo, không phải sai tư thế",
    ], 7.95, 1.95, 4.8, 4.6, size=12, gap=10)
    footer(s, 13)
    notes(s, 13)

    # 14 — kết luận
    s = new(True)
    title(s, "Kết luận", dark=True, size=40)
    message(s, "Tách hai vế: tốc độ tái lập được trên CPU; chất lượng ánh xạ chỉ một phần", dark=True)
    tb(s, 0.7, 1.92, 11.9, 0.8, "Tốc độ: tái lập được", size=44, color=ACCENT, bold=True, font=HEAD)
    tb(s, 0.7, 2.68, 11.9, 0.5, "Chất lượng ánh xạ: một phần", size=26, color=WHITE, bold=True, font=HEAD)
    card(s, 0.7, 3.4, 5.85, 2.35, fill=RGBColor(0x0B, 0x45, 0x4E))
    tb(s, 0.95, 3.55, 5.3, 0.4, "TỐC ĐỘ — ĐƯỢC", size=16, color=ACCENT, bold=True, font=HEAD)
    bullets(s, [
        "17,349 ms · 1,92× · 57,6 FPS",
        "2/3 robot dưới ngưỡng 33,33 ms",
        "Đạt tiêu chí đặt trước",
    ], 0.95, 4.0, 5.3, 1.65, dark=True, size=14, gap=8)
    card(s, 6.75, 3.4, 5.85, 2.35, fill=RGBColor(0x0B, 0x45, 0x4E))
    tb(s, 7.0, 3.55, 5.3, 0.4, "CHẤT LƯỢNG — MỘT PHẦN", size=16, color=RGBColor(0xFF, 0xB4, 0xA8), bold=True, font=HEAD)
    bullets(s, [
        "1/3 robot đạt foot_slide ≤ 50 mm/s",
        "T1 xuyên sàn 2,13 % frame",
        "Bảng I/II/III paper: ngoài phạm vi",
    ], 7.0, 4.0, 5.3, 1.65, dark=True, size=14, gap=8)
    tb(s, 0.7, 6.0, 11.9, 0.5,
       "“Tốc độ đạt ngưỡng nhóm đặt; chất lượng ánh xạ một phần; bảng paper không tái lập.”",
       size=15, color=WHITE, italic=True)
    footer(s, 14, dark=True)
    notes(s, 14)

    # 15 — bài học
    s = new()
    title(s, "Ba bài học + việc còn mở")
    message(s, "Giá trị nằm ở quy trình, không chỉ ở con số")
    lessons = [
        ("1", "Tách vai Review", "RV-13 phát hiện cờ giả trong cột cmd"),
        ("2", "Số phải tự truy vết", "dòng END trong từng log, đối chiếu CSV"),
        ("3", "Bất biến đầu ra", "SHA256 chứng minh chênh do máy, không do retarget"),
    ]
    for i, (num, head, sub) in enumerate(lessons):
        x = 0.7 + i * 4.05
        card(s, x, 1.95, 3.85, 2.2, fill=CARD)
        tb(s, x + 0.2, 2.08, 0.7, 0.5, num, size=30, color=ACCENT, bold=True, font=HEAD)
        tb(s, x + 0.2, 2.62, 3.4, 0.45, head, size=17, color=PRIMARY, bold=True, font=HEAD)
        tb(s, x + 0.2, 3.15, 3.4, 0.85, sub, size=12, color=TEXT)
    tb(s, 0.7, 4.5, 11.9, 0.4, "Còn mở", size=16, color=PRIMARY, bold=True, font=HEAD)
    bullets(s, [
        "Kết quả nhiễu mới là một lần/mức — cần lặp để có khoảng tin cậy",
        "min_body_height và foot_slide vẫn là proxy; cần đo theo mesh/geom",
        "Chưa đo trực tiếp ms_per_frame; chưa xác minh trên máy thứ hai",
    ], 0.7, 4.95, 11.9, 1.8, size=14, gap=10)
    footer(s, 15)
    notes(s, 15)

    # 16 — cầu nối Q&A
    s = new()
    title(s, "Cầu nối Q&A")
    message(s, "Mời hỏi — và chủ động đưa câu nhóm muốn được hỏi")
    tb(s, 0.7, 1.85, 5.0, 1.0, "Q&A", size=56, color=PRIMARY, bold=True, font=HEAD)
    tb(s, 0.7, 2.9, 5.0, 0.6, "7 câu đã chuẩn bị", size=22, color=ACCENT, bold=True, font=HEAD)
    picture(s, os.path.join(FIG, "slide_v3_walk1_g1_f900.png"), 0.7, 4.15, 2.35, 1.45,
            caption="walk1 — chuẩn")
    picture(s, os.path.join(FIG, "slide_v3_walk4_g1_f900.png"), 3.2, 4.15, 2.35, 1.45,
            caption="walk4 — khom lưng")
    picture(s, os.path.join(FIG, "slide_v5_sim2sim_f900.png"), 5.7, 4.15, 2.35, 1.45,
            caption="3 robot — sim2sim")
    bullets(s, [
        "Vì sao không đo ms_per_frame?",
        "Vì sao không train 3 seed?",
        "PM01 chậm vì ít khớp?",
        "Nhiễu trễ 36° ở frame 0?",
        "Sim2sim không đúng nhiễu vật lý?",
        "Hai đợt lệch 14 %, tin số nào?",
        "So với paper thế nào?",
    ], 8.4, 1.9, 4.3, 4.6, size=12, gap=8)
    tb(s, 0.7, 6.55, 7.4, 0.4,
       "Đây là toàn bộ demo: walk1 chuẩn · walk4 khom · 3 robot.",
       size=12, color=MUTED, italic=True)
    footer(s, 16)
    notes(s, 16)

    prs.save(OUT)
    print("saved", OUT, "slides", len(prs.slides))


if __name__ == "__main__":
    build()
