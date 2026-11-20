"""Dựng video demo HR-04 bằng ffmpeg + PIL, thời lượng tính từ manifest.

    python scripts/build_demo.py --media-dir <dir> --figures-dir <dir> \
        --script-doc report/video_script.md

Nguồn kịch bản: docs/ke_hoach/video_demo.md (05cd5da) và
results/media/demo_manifest.md (327d1cf). Thời lượng/timecode của S1–S4 đọc
từ khối ```csv``` trong manifest, KHÔNG cộng thêm cho đủ 90 giây. S0/S5/S6
không có trong manifest nên lấy DEFAULTS (ghi đè được qua --set/manifest
`key = value`). Phụ đề lấy từ report/video_script.md nếu có.

Xuất ra results/media/demo/: demo_v6_720p.mp4 (CRF 23) và
demo_v6_thumbnail.png. Chỉ xuất bản 720p; không còn bản 540p. Tên thiếu "90s"
là cố ý: thời lượng thực tế theo manifest (~77 s khi có cảnh bảng V6). S5 ưu
tiên ảnh v6_noise_slide.png (3 panel dọc); nếu chưa có thì dùng ảnh rộng nhưng
scale-to-fit + viền đen, KHÔNG crop. Sau S5 có cảnh bảng V6 sinh từ
results/v6_noise_sweep.csv. Script idempotent: lần chạy sau xoá và ghi đè sạch
kết quả cũ.

Ràng buộc ffmpeg 9 trên máy nhóm: không dùng -vsync (dùng -fps_mode cfr);
drawtext chạy với đường dẫn tương đối trong work dir để khỏi escape `C\\:`;
env gmr không có ffprobe nên summary fallback về `ffmpeg -i`.
"""

import argparse
import csv
import io
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
FONT_REGULAR = Path("C:/Windows/Fonts/segoeui.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
FONT_SLIDE_TITLE = Path("C:/Windows/Fonts/cambriab.ttf")
FONT_SLIDE_BODY = Path("C:/Windows/Fonts/calibri.ttf")
FONT_SLIDE_BODY_BOLD = Path("C:/Windows/Fonts/calibrib.ttf")
KNOWN_FFMPEG = (
    Path.home()
    / "miniconda3/envs/gmr/Lib/site-packages/imageio_ffmpeg/binaries"
    / "ffmpeg-win-x86_64-v9.0.2.exe"
)

# Chỉ dùng cho cảnh không có trong manifest (S0, S5, S6) và làm giá trị mặc
# định khi chưa có manifest/video_script. Ghi đè: manifest key = value, --set.
DEFAULTS = {
    "transition": "0.4",
    "subtitle_y": "h-th-34",
    "duration_s0": "5",
    "duration_s1": "10",
    "duration_s2": "10",
    "duration_s3": "10",
    "duration_s4": "10",
    "duration_s5": "14",
    "duration_v6_table": "10",
    "duration_s6": "8",
    # S0
    "s0_kicker": "HK1 2026–2027 · ĐH Công Thương TP.HCM",
    "s0_title": "GMR — Ánh xạ chuyển động người\nsang robot hình người",
    "s0_sub": "Nhóm 01 · HR04 · 15DHTH07",
    "s0_meta": "GMR commit 25f56db · Giấy phép MIT",
    # S1–S5: phụ đề mặc định, sẽ bị video_script.md ghi đè nếu có.
    "s1_sub": "Một clip chuyển động người: 7.840 frame, 261,3 giây",
    "s2_sub": (
        "Retarget sang Unitree G1: 17,3 ms/frame\n"
        "cả tiến trình (cận trên) · 2× thời gian thực"
    ),
    "s3_sub": (
        "Trái: clip gốc khom lưng (không phải lỗi retarget)\n"
        "Phải: clip đi bộ chuẩn"
    ),
    "s4_sub": (
        "Cùng một chuyển động, 3 robot:\n"
        "G1 17,0 · T1 13,0 · PM01 35,5 ms/frame\n"
        "cả tiến trình (cận trên)"
    ),
    "s5_sub": (
        "Nhiễu khớp 0,5 độ vẫn an toàn\n"
        "2 độ đã hỏng 88 phần trăm frame\n"
        "Trễ 1–5 frame vô hại"
    ),
    "v6_table_csv": "results/v6_noise_sweep.csv",
    "v6_table_title": "V6 — bảng đối chiếu nhiễu",
    "v6_table_kicker": "V6 · ĐỘ BỀN THEO NHIỄU · đọc trực tiếp từ results/v6_noise_sweep.csv",
    "v6_table_conclusion": "Nhiễu không tích lũy theo thời gian; ngưỡng hỏng nằm giữa σ 1° và 2°",
    # S4 nhãn nhỏ trên hình
    "s4_label1": "G1",
    "s4_label2": "T1",
    "s4_label3": "PM01",
    # S5
    "s5_image": "v6_noise_vs_deviation.png",
    "s5_slide_image": "v6_noise_slide.png",
    # S6
    "s6_kicker": "KẾT LUẬN",
    "s6_title": "TÁI LẬP MỘT PHẦN",
    "s6_m1_value": "17,3 ms",
    "s6_m1_label": "ms/frame · cả tiến trình (cận trên)",
    "s6_m2_value": "2×",
    "s6_m2_label": "thời gian thực (cận trên)",
    "s6_m3_value": "3 robot",
    "s6_m3_label": "sim2sim · G1 · T1 · PM01",
    "s6_footer": "Phần thời gian thực tái lập được · số của paper thì không",
}

SIZE_LIMITS_MB = {"720p": 25.0}
FPS = 30
SHOT_KEYS = ("S1", "S2", "S3a", "S3b", "S4a", "S4b", "S4c")


def log(message):
    print(f"[demo] {message}", flush=True)


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(" ".join(str(part) for part in cmd) + "\n")
        sys.stderr.write(result.stderr[-4000:] + "\n")
        raise SystemExit(f"ffmpeg loi (exit {result.returncode})")
    return result


def find_ffmpeg(explicit):
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise SystemExit(f"khong thay ffmpeg: {path}")
        return path
    try:
        import imageio_ffmpeg

        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError as exc:
        log(f"khong import duoc imageio_ffmpeg ({exc}); thu duong dan co dinh/PATH")
    if KNOWN_FFMPEG.exists():
        return KNOWN_FFMPEG
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)
    raise SystemExit("khong tim thay ffmpeg (dat --ffmpeg)")


def find_ffprobe(ffmpeg):
    for name in ("ffprobe.exe", "ffprobe"):
        candidate = ffmpeg.with_name(name)
        if candidate.exists():
            return candidate
    found = shutil.which("ffprobe")
    return Path(found) if found else None


def parse_ffmpeg_info(ffmpeg, path):
    probe = find_ffprobe(ffmpeg)
    if probe:
        result = subprocess.run(
            [
                str(probe), "-v", "error", "-select_streams", "v:0",
                "-show_entries",
                "stream=width,height,codec_name,avg_frame_rate:format=duration,size",
                "-of", "default=noprint_wrappers=1", str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        fields = dict(
            line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
        )
        num, _, den = fields["avg_frame_rate"].partition("/")
        return {
            "duration": float(fields["duration"]),
            "width": int(fields["width"]),
            "height": int(fields["height"]),
            "codec": fields["codec_name"],
            "fps": float(num) / float(den or 1),
            "size": int(fields["size"]),
        }

    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
    )
    text = result.stderr
    duration = 0.0
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", text)
    if match:
        hours, minutes, seconds = match.groups()
        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    stream = re.search(
        r"Video: (\w+).*? (\d{2,5})x(\d{2,5}).*? (\d+(?:\.\d+)?) fps", text
    )
    if not stream:
        raise SystemExit(f"khong doc duoc thong tin video: {path}")
    codec, width, height, fps = stream.groups()
    return {
        "duration": duration,
        "width": int(width),
        "height": int(height),
        "codec": codec,
        "fps": float(fps),
        "size": path.stat().st_size,
    }


def has_audio(ffmpeg, path):
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
    )
    return "Audio:" in result.stderr


def parse_manifest(path):
    """Trả (values, shots). shots lấy từ khối ```csv``` của manifest."""
    values, shots = {}, {}
    if not path.exists():
        return values, shots
    text = path.read_text(encoding="utf-8")
    block = re.search(r"```csv\s*\n(.*?)```", text, re.S)
    if block:
        reader = csv.DictReader(io.StringIO(block.group(1).strip()))
        for row in reader:
            shot = (row.get("shot") or "").strip()
            if shot:
                shots[shot] = {
                    "source": row["source"].strip(),
                    "start": float(row["start_s"]),
                    "duration": float(row["duration_s"]),
                }
        text = text.replace(block.group(0), "")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values, shots


def parse_script_doc(path):
    """Đọc phụ đề từ report/video_script.md: khối ``` đầu tiên sau '## S<n>'."""
    subtitles = {}
    if not path.exists():
        return subtitles
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"^##\s*(S\d)\s*[—-]", text, re.M):
        shot = match.group(1)
        following = text[match.end() :]
        block = re.search(r"```[^\n]*\n(.*?)```", following, re.S)
        if not block:
            continue
        lines = [line.strip() for line in block.group(1).splitlines() if line.strip()]
        if lines:
            subtitles[f"{shot.lower()}_sub"] = "\n".join(lines)
    return subtitles


def build_settings(args):
    settings = dict(DEFAULTS)
    manifest_values, shots = parse_manifest(Path(args.manifest).resolve())
    settings.update(manifest_values)

    script_doc = Path(args.script_doc).resolve()
    subtitles = parse_script_doc(script_doc)
    if subtitles:
        settings.update(subtitles)
        log(f"phu de: {script_doc}")
        # video_script.md có thể ghi "17,3 ms/frame" cho số process; định nghĩa
        # §1.1 cấm gọi tên trần như vậy. Thay bằng bản đã ghi rõ "cả tiến trình".
        for key in ("s2_sub", "s4_sub"):
            text = settings.get(key, "")
            if "ms/frame" in text and "cả tiến trình" not in text:
                log(
                    f"CANH BAO: {key} trong {script_doc.name} ghi 'ms/frame' "
                    "nhung so la process -> dung ban da sua "
                    "(can Writing sua video_script.md)"
                )
                settings[key] = DEFAULTS[key]
    elif not script_doc.exists():
        log(f"khong thay {script_doc} -> dung phu de mac dinh")

    # --set phải thắng mọi nguồn phía trên, kể cả duration lấy từ shot trong manifest.
    for pair in args.set:
        key, _, value = pair.partition("=")
        key = key.strip()
        if key not in DEFAULTS:
            raise SystemExit(f"--set: khong biet khoa '{key}'")
        if key in manifest_values:
            source = "manifest"
        elif key.startswith("duration_s") and {
            "duration_s1": "S1",
            "duration_s2": "S2",
            "duration_s3": "S3a",
            "duration_s4": "S4a",
        }.get(key) in shots:
            source = "manifest (shot)"
        elif key in subtitles:
            source = "video_script.md"
        else:
            source = "DEFAULTS"
        settings[key] = value.strip()
        log(f"--set {key}={value.strip()} (de len {source})")

    # Thời lượng S1-S4 lấy từ shot trong manifest, trừ khi bị --set ghi đè.
    set_keys = {pair.partition("=")[0].strip() for pair in args.set}
    for shot, index in (("S1", 1), ("S2", 2), ("S3a", 3), ("S4a", 4)):
        key = f"duration_s{index}"
        if key not in set_keys and shot in shots:
            settings[key] = f"{shots[shot]['duration']:g}"

    return settings, shots


def require_shot(shots, key):
    if key not in shots:
        raise SystemExit(f"manifest thieu shot {key}")
    return shots[key]


def resolve_source(value, media_dir):
    """Manifest ghi đường dẫn repo; ưu tiên --media-dir theo tên file."""
    direct = Path(value)
    if direct.is_absolute():
        return direct
    candidate = media_dir / Path(value).name
    if candidate.exists():
        return candidate
    repo_path = REPO_ROOT / direct
    if repo_path.exists():
        return repo_path
    return candidate  # báo lỗi tại nơi Run nên đặt file


def num(settings, key):
    return float(settings[key])


def load_font(path, size):
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def wrap(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def gradient(size, top, bottom):
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(size[1]):
        ratio = y / max(size[1] - 1, 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (size[0], y)], fill=color)
    return image


def make_title_card(settings, out_path):
    width, height = 1280, 720
    image = gradient((width, height), (10, 16, 32), (17, 30, 56))
    draw = ImageDraw.Draw(image)
    draw.rectangle([(64, 96), (72, 624)], fill=(34, 211, 238))
    draw.text(
        (108, 96),
        settings["s0_kicker"],
        font=load_font(FONT_REGULAR, 26),
        fill=(148, 163, 184),
    )
    title_font = load_font(FONT_BOLD, 56)
    y = 176
    for line in wrap(draw, settings["s0_title"], title_font, width - 220):
        draw.text((108, y), line, font=title_font, fill=(241, 245, 249))
        y += 72
    y += 24
    draw.text(
        (108, y),
        settings["s0_sub"],
        font=load_font(FONT_BOLD, 32),
        fill=(34, 211, 238),
    )
    draw.text(
        (108, y + 60),
        settings["s0_meta"],
        font=load_font(FONT_REGULAR, 26),
        fill=(148, 163, 184),
    )
    image.save(out_path)


def make_conclusion_card(settings, out_path):
    width, height = 1280, 720
    image = gradient((width, height), (10, 16, 32), (17, 30, 56))
    draw = ImageDraw.Draw(image)
    draw.rectangle([(64, 72), (72, 648)], fill=(34, 211, 238))
    draw.text(
        (108, 72),
        settings["s6_kicker"],
        font=load_font(FONT_BOLD, 26),
        fill=(148, 163, 184),
    )
    rows = [
        (settings["s6_m1_value"], settings["s6_m1_label"]),
        (settings["s6_m2_value"], settings["s6_m2_label"]),
        (settings["s6_m3_value"], settings["s6_m3_label"]),
    ]
    y = 140
    for value, label in rows:
        draw.rectangle([(108, y), (1172, y + 108)], fill=(15, 23, 42))
        draw.text(
            (136, y + 22),
            value,
            font=load_font(FONT_BOLD, 52),
            fill=(34, 211, 238),
        )
        draw.text(
            (1150, y + 48),
            label,
            font=load_font(FONT_REGULAR, 28),
            fill=(203, 213, 225),
            anchor="ra",
        )
        y += 124
    draw.text(
        (108, y + 18),
        settings["s6_title"],
        font=load_font(FONT_BOLD, 46),
        fill=(241, 245, 249),
    )
    draw.text(
        (108, y + 82),
        settings["s6_footer"],
        font=load_font(FONT_REGULAR, 24),
        fill=(148, 163, 184),
    )
    image.save(out_path)


def make_placeholder(text, out_path):
    width, height = 1280, 720
    image = gradient((width, height), (10, 16, 32), (17, 30, 56))
    draw = ImageDraw.Draw(image)
    font = load_font(FONT_BOLD, 40)
    for index, line in enumerate(wrap(draw, text, font, 1000)):
        draw.text((140, 300 + index * 56), line, font=font, fill=(148, 163, 184))
    image.save(out_path)


def vn_trim(value, digits):
    """Số thập phân kiểu Việt Nam, bỏ các số 0 thừa ở cuối (100.00 -> 100)."""
    step = Decimal(1).scaleb(-digits)
    text = str(Decimal(str(value)).quantize(step, rounding=ROUND_HALF_UP))
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


def vn_fixed(value, digits):
    step = Decimal(1).scaleb(-digits)
    return str(Decimal(str(value)).quantize(step, rounding=ROUND_HALF_UP)).replace(
        ".", ","
    )


def fit_text(draw, text, path, size, max_width, min_size=12):
    while size > min_size:
        font = load_font(path, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
        size -= 1
    return load_font(path, min_size)


def make_v6_table_card(csv_path, out_path, settings):
    """Card bảng V6; mọi số đọc từ results/v6_noise_sweep.csv, không viết tay."""
    with open(csv_path, encoding="utf-8-sig") as handle:
        data = list(csv.DictReader(handle))

    def value(mode, level, field):
        for row in data:
            if row["mode"] == mode and abs(float(row["level"]) - level) < 1e-9:
                return float(row[field])
        raise SystemExit(f"v6 csv thieu {mode} level {level}")

    threshold = [value("n1", level, "pct_frames_gt5deg") for level in (0.5, 1, 2, 5)]
    delay_dq = value("n2", 1, "dq_mean")
    delay_dr = value("n2", 1, "dr_rmse_mm")
    dropped = [value("n3", level, "dq_mean") for level in (1, 5, 10)]
    scale_low = value("n4", -20, "pct_frames_gt5deg")
    scale_high = value("n4", 20, "pct_frames_gt5deg")

    rows = [
        ("Phép thử", "Mức", "Kết quả đo", "Đọc"),
        (
            "N1 · nhiễu khớp",
            "σ = 0,5 / 1 / 2 / 5°",
            " / ".join(vn_trim(item, 2) for item in threshold) + " %",
            "hỏng từ 2°",
        ),
        (
            "N2 · trễ điều khiển",
            "k = 1…5 frame",
            f"dq {vn_trim(delay_dq, 3)}° · dr {vn_trim(delay_dr, 2)} mm",
            "vô hại",
        ),
        (
            "N3 · mất frame",
            "1 / 5 / 10 %",
            " / ".join(vn_trim(item, 3) for item in dropped) + "°",
            "vô hại",
        ),
        (
            "N4 · lệch tỉ lệ người",
            "±20 %",
            f"{vn_fixed(scale_low, 1)} – {vn_fixed(scale_high, 1)} % frame",
            "hỏng nặng",
        ),
    ]

    image = Image.new("RGB", (1280, 720), (0xF7, 0xFA, 0xFB))
    draw = ImageDraw.Draw(image)
    teal = (0x02, 0x80, 0x90)
    dark = (0x06, 0x34, 0x3C)
    text = (0x12, 0x34, 0x3B)
    muted = (0x4E, 0x6A, 0x70)
    draw.rectangle([(56, 48), (66, 672)], fill=teal)

    draw.text((88, 44), settings["v6_table_kicker"],
              font=load_font(FONT_SLIDE_BODY, 18), fill=muted)
    draw.text((88, 80), settings["v6_table_title"],
              font=load_font(FONT_SLIDE_TITLE, 46), fill=dark)

    x0, y0, table_w = 76, 176, 1128
    header_h, row_h = 52, 94
    widths = [280, 250, 380, table_w - 280 - 250 - 380]
    edges = [x0]
    for width in widths:
        edges.append(edges[-1] + width)

    draw.rectangle([(x0, y0), (x0 + table_w, y0 + header_h)], fill=teal)
    for index, cell in enumerate(rows[0]):
        font = fit_text(draw, cell, FONT_SLIDE_BODY_BOLD, 21,
                        widths[index] - 24)
        draw.text((edges[index] + 12, y0 + header_h / 2), cell,
                  font=font, fill=(0xFF, 0xFF, 0xFF), anchor="lm")

    for row_index, row in enumerate(rows[1:]):
        top = y0 + header_h + row_index * row_h
        fill = (0xFF, 0xFF, 0xFF) if row_index % 2 == 0 else (0xED, 0xF6, 0xF7)
        draw.rectangle([(x0, top), (x0 + table_w, top + row_h)], fill=fill)
        for col_index, cell in enumerate(row):
            bold = col_index == 0
            path = FONT_SLIDE_BODY_BOLD if bold else FONT_SLIDE_BODY
            font = fit_text(draw, cell, path, 21, widths[col_index] - 24)
            color = teal if col_index == 3 else text
            draw.text((edges[col_index] + 12, top + row_h / 2), cell,
                      font=font, fill=color, anchor="lm")
        draw.line([(x0, top + row_h), (x0 + table_w, top + row_h)],
                  fill=(0xD5, 0xE6, 0xE8), width=1)

    for edge in edges[1:-1]:
        draw.line([(edge, y0 + header_h), (edge, y0 + header_h + 4 * row_h)],
                  fill=(0xD5, 0xE6, 0xE8), width=1)
    draw.rectangle([(x0, y0), (x0 + table_w, y0 + header_h + 4 * row_h)],
                   outline=(0x9F, 0xC9, 0xCE), width=2)

    conclusion = settings["v6_table_conclusion"]
    conclusion_font = fit_text(draw, conclusion, FONT_SLIDE_BODY_BOLD, 24,
                               table_w)
    draw.text((x0, y0 + header_h + 4 * row_h + 28), conclusion,
              font=conclusion_font, fill=teal)
    image.save(out_path)


class Builder:
    def __init__(self, ffmpeg, workdir, settings):
        self.ffmpeg = ffmpeg
        self.workdir = workdir
        self.settings = settings
        self.scenes = []

    def subtitle(self, key, sequential=False, duration=None, y=None):
        lines = [line for line in self.settings[key].split("\n") if line.strip()]
        common = (
            "drawtext=fontfile=segoeui.ttf"
            ":fontcolor=white:fontsize=36:box=1:boxcolor=black@0.55"
            ":boxborderw=12:x=(w-text_w)/2"
        )
        line_height, bottom = 46, 16
        if y is None:
            y_single = self.settings["subtitle_y"]
        else:
            y_single = y
        if sequential and len(lines) > 1:
            step = duration / len(lines)
            filters = []
            for index, line in enumerate(lines):
                name = f"{key}_{index}.txt"
                (self.workdir / name).write_text(line, encoding="utf-8")
                start, end = index * step, (index + 1) * step
                filters.append(
                    f"{common}:textfile={name}:y={y_single}"
                    f":enable='between(t,{start:.3f},{end:.3f})'"
                )
            return ",".join(filters)
        if len(lines) == 1:
            name = f"{key}.txt"
            (self.workdir / name).write_text(lines[0], encoding="utf-8")
            return f"{common}:textfile={name}:y={y_single}"
        # Nhiều dòng: mỗi dòng một drawtext, xếp từ dưới lên để không tràn khung.
        filters = []
        for index, line in enumerate(lines):
            name = f"{key}_{index}.txt"
            (self.workdir / name).write_text(line, encoding="utf-8")
            offset = (len(lines) - index) * line_height + bottom
            filters.append(f"{common}:textfile={name}:y=h-{offset}")
        return ",".join(filters)

    def label(self, text, name, x="10", y="12", size="24"):
        (self.workdir / name).write_text(text, encoding="utf-8")
        return (
            f"drawtext=fontfile=segoeui.ttf:textfile={name}"
            f":fontcolor=white:fontsize={size}:box=1:boxcolor=black@0.6"
            f":boxborderw=10:x={x}:y={y}"
        )

    def encode(self, out_name, inputs, vf, duration, graph=None):
        out = self.workdir / "scenes" / out_name
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [str(self.ffmpeg), "-y", "-hide_banner", "-loglevel", "error"]
        cmd += inputs
        if graph:
            cmd += ["-filter_complex", graph, "-map", "[v]"]
        else:
            cmd += ["-vf", vf]
        cmd += [
            "-t", f"{duration:.3f}",
            "-r", str(FPS),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-fps_mode", "cfr",
            "-an",
            str(out),
        ]
        run(cmd, self.workdir)
        self.scenes.append(out)
        log(f"{out_name}: {duration:.2f}s")

    def still_scene(self, image, out_name, duration, subtitle_key=None):
        filters = ["fps=30"]
        if subtitle_key:
            filters.append(self.subtitle(subtitle_key))
        filters += ["setsar=1", "format=yuv420p"]
        self.encode(
            out_name, ["-loop", "1", "-i", str(image)], ",".join(filters), duration
        )

    def fit_scene(self, image, out_name, duration, subtitle_key, sequential=False):
        """Scale-to-fit, chừa dải đen 100 px dưới cho phụ đề; KHÔNG crop."""
        band = 100
        filters = [
            f"scale=1280:{720 - band}:force_original_aspect_ratio=decrease",
            "pad=1280:720:x='(ow-iw)/2':y='(oh-ih-100)/2':color=black",
            "fps=30",
            self.subtitle(
                subtitle_key, sequential=sequential, duration=duration, y="h-72"
            ),
            "setsar=1",
            "format=yuv420p",
        ]
        self.encode(
            out_name, ["-loop", "1", "-i", str(image)], ",".join(filters), duration
        )

    def clip_scene(self, clip, start, out_name, duration, subtitle_key):
        info = parse_ffmpeg_info(self.ffmpeg, clip)
        filters = [
            "scale=1280:720:force_original_aspect_ratio=decrease",
            "pad=1280:720:(ow-iw)/2:(oh-ih)/2",
            "fps=30",
            self.subtitle(subtitle_key),
            "setsar=1",
            "format=yuv420p",
        ]
        inputs = ["-ss", f"{start:.3f}", "-i", str(clip)]
        if info["duration"] < start + duration:
            source_length = max(info["duration"] - start, 0.1)
            ratio = duration / source_length
            inputs = ["-ss", f"{start:.3f}", "-i", str(clip)]
            filters.insert(0, f"setpts=PTS*{ratio:.6f}")
            log(f"{clip.name}: {source_length:.1f}s -> keo thanh {duration:.2f}s")
        self.encode(out_name, inputs, ",".join(filters), duration)

    def split_scene(self, left, left_start, right, right_start, duration):
        side = "scale=1280:720,crop=640:720:320:0"
        graph = (
            f"[0:v]{side}[l];[1:v]{side}[r];"
            f"[l][r]hstack=inputs=2,fps=30,{self.subtitle('s3_sub')},"
            "setsar=1,format=yuv420p[v]"
        )
        self.encode(
            "s3.mp4",
            [
                "-ss", f"{left_start:.3f}", "-i", str(left),
                "-ss", f"{right_start:.3f}", "-i", str(right),
            ],
            None,
            duration,
            graph=graph,
        )

    def columns_scene(self, sources, starts, duration, subtitle_key):
        """S4: 3 robot cạnh nhau, mỗi cột 426/427/427 x 720 -> 1280x720."""
        widths = [426, 426, 428]
        labels = [
            self.settings["s4_label1"],
            self.settings["s4_label2"],
            self.settings["s4_label3"],
        ]
        parts = []
        for index, width in enumerate(widths):
            crop_x = (1280 - width) // 2
            label = self.label(labels[index], f"s4_l{index}.txt")
            parts.append(
                f"[{index}:v]crop={width}:720:{crop_x}:0,{label}[c{index}]"
            )
        parts.append(
            "[c0][c1][c2]hstack=inputs=3,fps=30,"
            f"{self.subtitle(subtitle_key)},setsar=1,format=yuv420p[v]"
        )
        inputs = []
        for source, start in zip(sources, starts):
            inputs += ["-ss", f"{start:.3f}", "-i", str(source)]
        self.encode("s4.mp4", inputs, None, duration, graph=";".join(parts))

    def assemble(self, output, crf, visible, transition):
        offsets = []
        elapsed = 0.0
        for value in visible[:-1]:
            elapsed += value
            offsets.append(elapsed)
        parts = []
        previous = "[0:v]"
        for index, offset in enumerate(offsets, start=1):
            label = f"[x{index}]"
            parts.append(
                f"{previous}[{index}:v]xfade=transition=fade:"
                f"duration={transition}:offset={offset:.3f}{label}"
            )
            previous = label
        cmd = [str(self.ffmpeg), "-y", "-hide_banner", "-loglevel", "error"]
        for scene in self.scenes:
            cmd += ["-i", str(scene)]
        cmd += [
            "-filter_complex", ";".join(parts),
            "-map", previous,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", str(crf),
            "-preset", "medium",
            "-fps_mode", "cfr",
            "-an",
            str(output),
        ]
        run(cmd, self.workdir)


def require(path):
    if not path.exists():
        raise SystemExit(f"thieu asset bat buoc: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Dung video demo HR-04 bang ffmpeg + PIL, thoi luong tu manifest."
    )
    parser.add_argument("--media-dir", default=str(REPO_ROOT / "results/media"))
    parser.add_argument("--figures-dir", default=str(REPO_ROOT / "results/figures"))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "results/media/demo"))
    parser.add_argument(
        "--cards-dir",
        default=str(REPO_ROOT / "results/figures/demo_cards"),
        help="Noi ghi card S0/S6 (tach khoi --figures-dir).",
    )
    parser.add_argument(
        "--manifest",
        default=str(REPO_ROOT / "results/media/demo_manifest.md"),
        help="Manifest co khoi ```csv``` (shot,source,start_s,duration_s,...).",
    )
    parser.add_argument(
        "--script-doc",
        default=str(REPO_ROOT / "report/video_script.md"),
        help="Phu de cua Writing; doc khoi code dau tien sau moi '## S<n>'.",
    )
    parser.add_argument(
        "--set", action="append", default=[], metavar="KEY=VALUE",
        help="Ghi de mot khoa trong DEFAULTS, vd --set duration_s5=10.",
    )
    parser.add_argument("--ffmpeg", default=None)
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Chi in ke hoach + sinh card PNG, khong goi ffmpeg.",
    )
    args = parser.parse_args(argv)

    settings, shots = build_settings(args)
    media_dir = Path(args.media_dir).resolve()
    figures_dir = Path(args.figures_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    cards_dir = Path(args.cards_dir).resolve()
    manifest = Path(args.manifest).resolve()
    if not shots:
        log(f"khong thay manifest {manifest} -> dung placeholder cho S1-S4")

    # Thời lượng đã được build_settings chốt: shot trong manifest, trừ khi --set.
    labels = ["S0", "S1", "S2", "S3", "S4", "S5", "V6T", "S6"]
    visible = [num(settings, f"duration_s{i}") for i in range(6)]
    visible.append(num(settings, "duration_v6_table"))
    visible.append(num(settings, "duration_s6"))
    transition = num(settings, "transition")
    log(
        "ke hoach: "
        + " + ".join(f"{name} {value:g}s" for name, value in zip(labels, visible))
        + f" (xfade {transition:g}s) = {sum(visible):.2f}s"
    )

    cards_dir.mkdir(parents=True, exist_ok=True)
    card_s0 = cards_dir / "S0.png"
    card_s6 = cards_dir / "S6.png"
    card_table = cards_dir / "S5_table.png"
    make_title_card(settings, card_s0)
    make_conclusion_card(settings, card_s6)
    make_v6_table_card(
        REPO_ROOT / settings["v6_table_csv"], card_table, settings
    )
    log(f"card: {card_s0} | {card_table} | {card_s6}")

    if args.dry_run:
        return 0

    ffmpeg = find_ffmpeg(args.ffmpeg)
    log(f"ffmpeg: {ffmpeg}")
    require(FONT_REGULAR)

    workdir = Path(tempfile.mkdtemp(prefix="gmr_demo_"))
    shutil.copyfile(FONT_REGULAR, workdir / "segoeui.ttf")
    builder = Builder(ffmpeg, workdir, settings)
    encoded = [
        value + transition if index < len(visible) - 1 else value
        for index, value in enumerate(visible)
    ]

    builder.still_scene(card_s0, "s0.mp4", encoded[0])

    s1 = require_shot(shots, "S1")
    s1_clip = resolve_source(s1["source"], media_dir)
    if not s1_clip.exists():
        raise SystemExit(
            f"thieu clip S1: {s1_clip}. Can quay/chuyen s1_human_input.mp4; "
            "khong dung anh robot thay the vi se gay hieu sai."
        )
    builder.clip_scene(s1_clip, s1["start"], "s1.mp4", encoded[1], "s1_sub")

    s2 = require_shot(shots, "S2")
    s2_clip = resolve_source(s2["source"], media_dir)
    require(s2_clip)
    builder.clip_scene(s2_clip, s2["start"], "s2.mp4", encoded[2], "s2_sub")

    s3a, s3b = require_shot(shots, "S3a"), require_shot(shots, "S3b")
    if abs(s3a["duration"] - s3b["duration"]) > 1e-6:
        raise SystemExit("S3a va S3b phai cung duration de hstack")
    s3_left = resolve_source(s3a["source"], media_dir)
    s3_right = resolve_source(s3b["source"], media_dir)
    require(s3_left)
    require(s3_right)
    builder.split_scene(
        s3_left, s3a["start"], s3_right, s3b["start"], encoded[3]
    )

    s4 = [require_shot(shots, key) for key in ("S4a", "S4b", "S4c")]
    if len({round(item["duration"], 3) for item in s4}) != 1:
        raise SystemExit("S4a/S4b/S4c phai cung duration de ghep 3 cot")
    s4_sources = [resolve_source(item["source"], media_dir) for item in s4]
    for source in s4_sources:
        require(source)
    builder.columns_scene(
        s4_sources,
        [item["start"] for item in s4],
        encoded[4],
        "s4_sub",
    )

    s5_slide = figures_dir / settings["s5_slide_image"]
    s5_wide = figures_dir / settings["s5_image"]
    if s5_slide.exists():
        s5_image = s5_slide
        log(f"S5: {s5_slide.name}")
    elif s5_wide.exists():
        s5_image = s5_wide
        log(f"S5: {s5_wide.name} (scale-to-fit, khong crop)")
    else:
        s5_image = workdir / "s5_placeholder.png"
        make_placeholder("Đang chờ đồ thị độ bền V6", s5_image)
        log("thieu anh S5 -> dung placeholder")
    builder.fit_scene(s5_image, "s5.mp4", encoded[5], "s5_sub", sequential=True)
    builder.still_scene(card_table, "s5b.mp4", encoded[6])
    builder.still_scene(card_s6, "s6.mp4", encoded[7])

    if len(builder.scenes) != 8:
        raise SystemExit(f"thieu canh: {len(builder.scenes)}/8")

    out_dir.mkdir(parents=True, exist_ok=True)
    master = out_dir / "demo_v6_720p.mp4"
    thumb = out_dir / "demo_v6_thumbnail.png"
    for path in (master, thumb):
        path.unlink(missing_ok=True)
    # Dọn bản 540p và tên cũ để thư mục không còn file gây nhầm.
    for legacy in (
        "demo_v6_540p.mp4",
        "demo_90s_720p.mp4",
        "demo_90s_540p.mp4",
        "demo_90s_thumbnail.png",
    ):
        (out_dir / legacy).unlink(missing_ok=True)

    builder.assemble(master, 23, visible, transition)
    log(f"xuat: {master}")

    run(
        [
            str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error",
            "-ss", "20", "-i", str(master),
            "-frames:v", "1", "-update", "1",
            "-vf", "scale=1280:720", str(thumb),
        ],
        workdir,
    )
    if not thumb.exists():
        raise SystemExit("ffmpeg khong tao duoc thumbnail (video qua ngan?)")
    with Image.open(thumb) as thumb_image:
        thumb_size = thumb_image.size
    log(
        f"thumbnail: {thumb_size[0]}x{thumb_size[1]}, "
        f"{thumb.stat().st_size / 1024:.0f} KB"
    )

    expected = sum(visible)
    ok = True
    summary = []
    for label, path, width, height, limit in (
        ("720p", master, 1280, 720, SIZE_LIMITS_MB["720p"]),
    ):
        info = parse_ffmpeg_info(ffmpeg, path)
        size_mb = info["size"] / 1024**2
        checks = [
            (abs(info["duration"] - expected) <= 1.0, f"duration {expected:.1f}+-1s"),
            (info["width"] == width and info["height"] == height, "resolution"),
            (info["codec"] == "h264", "codec h264"),
            (size_mb <= limit, f"size <= {limit:g} MB"),
            (not has_audio(ffmpeg, path), "khong audio"),
        ]
        passed = all(result for result, _ in checks)
        ok = ok and passed
        failed = [name for result, name in checks if not result]
        summary.append(
            f"{path.name}: {info['duration']:.2f}s, "
            f"{info['width']}x{info['height']}, {info['fps']:.1f} fps, "
            f"{info['codec']}, {size_mb:.2f} MB "
            f"({'PASS' if passed else 'FAIL: ' + '; '.join(failed)})"
        )

    if not args.keep_work:
        shutil.rmtree(workdir, ignore_errors=True)

    log("ffmpeg summary:")
    for line in summary:
        print("  " + line)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
