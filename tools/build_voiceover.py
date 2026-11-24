"""Sinh lời thuyết minh tiếng Việt (gTTS) và ghép vào video demo.

Chạy bằng **python base** (gTTS 2.5.4 nằm ở base, không có trong env gmr):

    python tools/build_voiceover.py
    python tools/build_voiceover.py --no-mux     # chỉ sinh narration.wav

Đọc 8 cửa sổ cảnh từ khối ```csv``` trong mục "## Lời thuyết minh" của
report/video_script.md, sinh TTS từng cảnh, đo thời lượng, tăng tốc nhẹ
(atempo, tối đa 1,3x) nếu đoạn dài hơn cửa sổ, rồi đặt đúng timecode.
Cuối cùng mux vào video (video stream copy, audio AAC 128k) và ghi đè
demo_v6_720p.mp4 để link release cũ vẫn dùng được.
"""

import argparse
import csv
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
DEFAULT_WAV = ROOT / "results/media/demo/narration.wav"
SAMPLE_RATE = 48000
MAX_TEMPO = 1.4  # kich_ban dài hơn ước lượng 2,6 từ/giây; 1,4x vẫn rõ, tránh cắt chữ
GAP_BEFORE_NEXT = 0.4  # giữ im lặng trước cảnh kế để kiem_video kiểm được
GAIN_DB = -4.0


def log(message):
    print(f"[voice] {message}", flush=True)


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
    raise SystemExit("khong tim thay ffmpeg (dat bien FFMPEG hoac --ffmpeg)")


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(" ".join(str(part) for part in cmd) + "\n")
        sys.stderr.write(result.stderr[-3000:] + "\n")
        raise SystemExit(f"ffmpeg loi (exit {result.returncode})")
    return result


def media_duration(ffmpeg, path):
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
    )
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", result.stderr)
    if not match:
        raise SystemExit(f"khong doc duoc duration: {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_kich_ban(path):
    """Đọc lời thuyết minh theo cảnh từ bảng của report/kich_ban.md."""
    text = Path(path).read_text(encoding="utf-8")
    if "Lời thuyết minh" not in text:
        raise SystemExit("kich_ban.md thieu cot 'Loi thuyet minh'")
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
        match_start = re.fullmatch(r"(\d+):(\d+)", cells[2].replace(" ", ""))
        match_end = re.fullmatch(r"(\d+):(\d+)", cells[3].replace(" ", ""))
        if not match_start or not match_end:
            raise SystemExit(f"kich_ban.md: timecode sai o {name}")
        scenes.append(
            {
                "scene": name,
                "start": int(match_start.group(1)) * 60 + int(match_start.group(2)),
                "end": int(match_end.group(1)) * 60 + int(match_end.group(2)),
                "text": cells[7].strip(),
            }
        )
    missing = [
        name
        for name in ("S0", "S1", "S2", "S3", "S4", "S5", "S5b", "S6")
        if name not in {scene["scene"] for scene in scenes}
    ]
    if missing:
        raise SystemExit(f"kich_ban.md thieu canh {', '.join(missing)}")
    return scenes


def parse_narration(path):
    text = Path(path).read_text(encoding="utf-8")
    heading = text.find("## Lời thuyết minh")
    if heading < 0:
        raise SystemExit("video_script.md thieu muc '## Lời thuyết minh'")
    block = re.search(r"```csv\s*\n(.*?)```", text[heading:], re.S)
    if not block:
        raise SystemExit("muc 'Lời thuyết minh' thieu khoi ```csv```")
    scenes = []
    for row in csv.DictReader(io.StringIO(block.group(1).strip())):
        scenes.append(
            {
                "scene": row["scene"].strip(),
                "start": float(row["start_s"]),
                "end": float(row["end_s"]),
                "text": row["text"].strip(),
            }
        )
    if not scenes:
        raise SystemExit("khong co canh nao trong khoi csv")
    return scenes


def validate(scenes, total):
    if abs(scenes[0]["start"]) > 1e-6:
        raise SystemExit("canh dau tien phai bat dau tu 0")
    for index, scene in enumerate(scenes):
        if scene["end"] <= scene["start"]:
            raise SystemExit(f"{scene['scene']}: end <= start")
        if index and abs(scene["start"] - scenes[index - 1]["end"]) > 1e-6:
            raise SystemExit(
                f"{scene['scene']}: start {scene['start']} khong noi tiep canh truoc"
            )
    if abs(scenes[-1]["end"] - total) > 1.0:
        raise SystemExit(
            f"tong timecode {scenes[-1]['end']}s lech duration video {total:.2f}s"
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", default=str(DEFAULT_VIDEO))
    parser.add_argument("--script-doc", default=str(DEFAULT_SCRIPT))
    parser.add_argument("--kich-ban", default=str(DEFAULT_KICH_BAN))
    parser.add_argument("--wav", default=str(DEFAULT_WAV))
    parser.add_argument("--work-dir", default=None)
    parser.add_argument("--no-mux", action="store_true")
    args = parser.parse_args(argv)

    ffmpeg = find_ffmpeg()
    video = Path(args.video).resolve()
    wav_out = Path(args.wav).resolve()
    if not video.exists():
        raise SystemExit(f"khong thay video: {video}")
    total = media_duration(ffmpeg, video)
    kich_ban = Path(args.kich_ban).resolve()
    if kich_ban.exists():
        scenes = parse_kich_ban(kich_ban)
        log(f"loi thuyet minh: {kich_ban} (cot 'Loi thuyet minh')")
    else:
        log("CANH BAO: dang dung narration tam, se thay bang kich_ban.md")
        scenes = parse_narration(Path(args.script_doc).resolve())
    validate(scenes, total)
    log(f"video {total:.2f}s, {len(scenes)} canh")

    workdir = Path(tempfile.mkdtemp(prefix="gmr_voice_"))
    rows = []
    wavs = []
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise SystemExit(
            f"khong import duoc gtts ({exc}); chay bang python BASE, khong phai env gmr"
        )

    for scene in scenes:
        window = scene["end"] - scene["start"]
        target = max(window - GAP_BEFORE_NEXT, 0.5)
        mp3 = workdir / f"{scene['scene']}.mp3"
        try:
            gTTS(text=scene["text"], lang="vi").save(str(mp3))
        except Exception as exc:  # gTTS loi mang/HTTP
            raise SystemExit(f"gTTS loi o {scene['scene']}: {exc}")
        raw = media_duration(ffmpeg, mp3)
        speed = raw / target
        tempo = min(max(speed, 1.0), MAX_TEMPO)
        wav = workdir / f"{scene['scene']}.wav"
        filters = []
        if tempo > 1.001:
            filters.append(f"atempo={tempo:.4f}")
        if raw / tempo > target:
            fade_at = max(target - 0.15, 0)
            filters.append(f"afade=t=out:st={fade_at:.3f}:d=0.15")
        filters += [f"aresample={SAMPLE_RATE}", "aformat=channel_layouts=mono"]
        run(
            [
                str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(mp3),
                "-af", ",".join(filters),
                "-t", f"{target:.3f}",
                "-c:a", "pcm_s16le", "-ar", str(SAMPLE_RATE), "-ac", "1",
                str(wav),
            ]
        )
        actual = media_duration(ffmpeg, wav)
        cut = raw / tempo > target + 1e-3
        rows.append(
            (scene["scene"], scene["start"], window, raw, tempo, actual, cut)
        )
        wavs.append((scene, wav))
        log(
            f"{scene['scene']}: raw {raw:.2f}s / cua so {window:.1f}s "
            f"-> tempo {tempo:.2f}x, phat {actual:.2f}s"
            + (" (cat bot duoi)" if cut else "")
        )

    # Track 77 s: silence + adelay từng đoạn + amix, hạ 4 dB để chừa headroom.
    inputs = [
        "-f", "lavfi", "-t", f"{total:.3f}",
        "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
    ]
    chains = []
    labels = ["[0:a]"]
    for index, (scene, wav) in enumerate(wavs, start=1):
        inputs += ["-i", str(wav)]
        delay = int(round(scene["start"] * 1000))
        chains.append(f"[{index}:a]adelay={delay}:all=1[a{index}]")
        labels.append(f"[a{index}]")
    graph = ";".join(chains)
    graph += (
        ";" + "".join(labels)
        + f"amix=inputs={len(labels)}:duration=first:normalize=0,"
        + f"volume={GAIN_DB}dB[out]"
    )
    wav_out.parent.mkdir(parents=True, exist_ok=True)
    run(
        [str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error"]
        + inputs
        + [
            "-filter_complex", graph,
            "-map", "[out]",
            "-t", f"{total:.3f}",
            "-c:a", "pcm_s16le", "-ar", str(SAMPLE_RATE), "-ac", "1",
            str(wav_out),
        ]
    )
    log(f"narration: {wav_out} ({wav_out.stat().st_size / 1024:.0f} KB)")

    if not args.no_mux:
        temp = video.with_name(video.stem + "_voiced.tmp.mp4")
        run(
            [
                str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(video), "-i", str(wav_out),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-movflags", "+faststart",
                str(temp),
            ]
        )
        os.replace(temp, video)
        log(f"mux xong: {video}")

    print()
    print("canh | cua so | raw | tempo | phat | cat")
    for scene, start, window, raw, tempo, actual, cut in rows:
        print(
            f"{scene:4} | {start:6.2f}s | {window:5.1f}s | {raw:5.2f}s | "
            f"{tempo:4.2f}x | {actual:5.2f}s | {'co' if cut else 'khong'}"
        )
    shutil.rmtree(workdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
