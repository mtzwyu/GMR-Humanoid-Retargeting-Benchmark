"""Nghiệm thu video demo có lời thuyết minh — kiểm bằng số, exit 1 nếu trượt.

    python tools/kiem_video.py
    python tools/kiem_video.py --video results/media/demo/demo_v6_720p.mp4

Kiểm:
1. duration 77 ± 1 s;
2. có audio stream AAC;
3. RMS từng cửa sổ cảnh > −40 dBFS (có tiếng nói);
4. 0,3 s NGAY TRƯỚC mỗi cảnh < −40 dBFS (không lấn sang cảnh sau);
5. peak toàn file < −1 dBFS (không vỡ tiếng);
6. video stream vẫn 1280×720, 30 fps, duration không đổi.
"""

import argparse
import csv
import io
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

FFMPEG = Path(
    Path.home()
    / "miniconda3/envs/gmr/Lib/site-packages/imageio_ffmpeg"
    / "binaries/ffmpeg-win-x86_64-v9.0.2.exe"
)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / "results/media/demo/demo_v6_720p.mp4"
DEFAULT_SCRIPT = ROOT / "report/video_script.md"
DEFAULT_KICH_BAN = ROOT / "report/kich_ban.md"
RMS_MIN = -40.0
PEAK_MAX = -1.0
GAP = 0.3
EXPECTED_DURATION = 77.0
DURATION_TOL = 1.0


def find_ffmpeg():
    env = os.environ.get("FFMPEG")
    if env and Path(env).exists():
        return Path(env)
    try:
        import imageio_ffmpeg

        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError:
        pass
    if FFMPEG.exists():
        return FFMPEG
    found = shutil.which("ffmpeg")
    if found:
        return Path(found)
    raise SystemExit("khong tim thay ffmpeg (dat bien FFMPEG)")


def parse_kich_ban(path):
    text = Path(path).read_text(encoding="utf-8")
    scenes = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        name = cells[0].replace("*", "").strip()
        if not re.fullmatch(r"S\d+b?", name):
            continue
        start = re.fullmatch(r"(\d+):(\d+)", cells[2].replace(" ", ""))
        end = re.fullmatch(r"(\d+):(\d+)", cells[3].replace(" ", ""))
        if not start or not end:
            raise SystemExit(f"kich_ban.md: timecode sai o {name}")
        scenes.append(
            (
                name,
                int(start.group(1)) * 60 + int(start.group(2)),
                int(end.group(1)) * 60 + int(end.group(2)),
                cells[7].strip(),
            )
        )
    missing = [
        name
        for name in ("S0", "S1", "S2", "S3", "S4", "S5", "S5b", "S6")
        if name not in {scene[0] for scene in scenes}
    ]
    if missing:
        raise SystemExit(f"kich_ban.md thieu canh {', '.join(missing)}")
    return scenes


def parse_scenes(path):
    text = Path(path).read_text(encoding="utf-8")
    heading = text.find("## Lời thuyết minh")
    if heading < 0:
        raise SystemExit("video_script.md thieu muc '## Lời thuyết minh'")
    block = re.search(r"```csv\s*\n(.*?)```", text[heading:], re.S)
    if not block:
        raise SystemExit("thieu khoi csv loi thuyet minh")
    scenes = []
    for row in csv.DictReader(io.StringIO(block.group(1).strip())):
        scenes.append(
            (
                row["scene"].strip(),
                float(row["start_s"]),
                float(row["end_s"]),
                row["text"].strip(),
            )
        )
    return scenes


def ffmpeg_info(ffmpeg, video):
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(video)],
        capture_output=True,
        text=True,
    )
    text = result.stderr
    duration = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", text)
    if not duration:
        raise SystemExit("khong doc duoc duration")
    hours, minutes, seconds = duration.groups()
    total = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    video_stream = re.search(
        r"Video: (\w+).*? (\d{2,5})x(\d{2,5}).*? (\d+(?:\.\d+)?) fps", text
    )
    if not video_stream:
        raise SystemExit("khong doc duoc video stream")
    codec, width, height, fps = video_stream.groups()
    audio = re.search(r"Audio: (\w+)", text)
    return {
        "duration": total,
        "codec": codec,
        "width": int(width),
        "height": int(height),
        "fps": float(fps),
        "audio": audio.group(1) if audio else None,
    }


def volume(ffmpeg, video, start=None, length=None):
    """mean_volume và max_volume (dBFS) của một cửa sổ."""
    cmd = [str(ffmpeg), "-hide_banner", "-nostats"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}", "-t", f"{length:.3f}"]
    cmd += [
        "-i", str(video), "-map", "0:a:0",
        "-af", "volumedetect", "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit("ffmpeg volumedetect loi")
    mean = re.search(r"mean_volume: (-?\d+(?:\.\d+)?) dB", result.stderr)
    peak = re.search(r"max_volume: (-?\d+(?:\.\d+)?) dB", result.stderr)
    return (
        float(mean.group(1)) if mean else float("-inf"),
        float(peak.group(1)) if peak else float("-inf"),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", default=str(DEFAULT_VIDEO))
    parser.add_argument("--script-doc", default=str(DEFAULT_SCRIPT))
    parser.add_argument("--kich-ban", default=str(DEFAULT_KICH_BAN))
    args = parser.parse_args(argv)

    ffmpeg = find_ffmpeg()
    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"khong thay video: {video}")
    scenes = (
        parse_kich_ban(Path(args.kich_ban))
        if Path(args.kich_ban).exists()
        else parse_scenes(Path(args.script_doc))
    )
    info = ffmpeg_info(ffmpeg, video)
    peak_mean, peak_max = volume(ffmpeg, video)

    checks = []
    checks.append(
        (
            "duration 77 +-1 s",
            f"{info['duration']:.2f}s",
            abs(info["duration"] - EXPECTED_DURATION) <= DURATION_TOL,
            f"{EXPECTED_DURATION - DURATION_TOL:.0f}-{EXPECTED_DURATION + DURATION_TOL:.0f}s",
        )
    )
    checks.append(
        (
            "audio AAC",
            str(info["audio"]),
            info["audio"] == "aac",
            "aac",
        )
    )
    checks.append(
        (
            "peak < -1 dBFS",
            f"{peak_max:.1f} dBFS",
            peak_max < PEAK_MAX,
            f"< {PEAK_MAX:.0f}",
        )
    )
    checks.append(
        (
            "video 1280x720 30fps",
            f"{info['width']}x{info['height']} {info['fps']:.1f}fps",
            info["width"] == 1280
            and info["height"] == 720
            and abs(info["fps"] - 30.0) < 0.1,
            "1280x720 30fps",
        )
    )

    scene_rows = []
    for name, start, end, text in scenes:
        mean, scene_peak = volume(ffmpeg, video, start, end - start)
        ok = mean > RMS_MIN
        scene_rows.append((name, start, end, mean, scene_peak, ok))

    gap_rows = []
    for name, start, end, text in scenes[1:]:
        if start < GAP:
            continue
        mean, _ = volume(ffmpeg, video, start - GAP, GAP)
        ok = mean < RMS_MIN
        gap_rows.append((name, start - GAP, start, mean, ok))

    ok_all = all(item[2] for item in checks)
    ok_all = ok_all and all(item[5] for item in scene_rows)
    ok_all = ok_all and all(item[4] for item in gap_rows)

    print("=== KIEM VIDEO (co loi thuyet minh) ===")
    print(f"file: {video}")
    print()
    print(f"{'Muc':28} {'Gia tri':26} {'Ket qua':8} {'Nguong'}")
    for name, value, ok, limit in checks:
        print(f"{name:28} {value:26} {'PASS' if ok else 'FAIL':8} {limit}")
    print()
    print(f"{'Canh':5} {'Bat dau':>8} {'Ket thuc':>9} {'RMS dBFS':>9} "
          f"{'Peak':>7} {'Ket qua'}")
    for name, start, end, mean, scene_peak, ok in scene_rows:
        print(
            f"{name:5} {start:8.1f} {end:9.1f} {mean:9.1f} "
            f"{scene_peak:7.1f} {'PASS' if ok else 'FAIL'}"
        )
    print()
    print(f"{'Khoang lang':12} {'Tu':>7} {'Den':>7} {'RMS dBFS':>9} {'Ket qua'}")
    for name, start, end, mean, ok in gap_rows:
        print(
            f"{name + ' -0.3s':12} {start:7.1f} {end:7.1f} "
            f"{mean:9.1f} {'PASS' if ok else 'FAIL'}"
        )
    print()
    print("TONG KET:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
