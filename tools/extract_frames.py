# Trich 3 khung 25% / 50% / 75% tu mot clip mp4 -> PNG (<=1MB)
# python extract_frames.py <mp4> <tien_to_anh> <tong_so_frame>
import sys, os, subprocess
import imageio_ffmpeg, imageio.v2 as imageio

mp4, prefix, total = sys.argv[1], sys.argv[2], int(sys.argv[3])
ff = imageio_ffmpeg.get_ffmpeg_exe()
outdir = os.path.dirname(prefix) or "."
os.makedirs(outdir, exist_ok=True)

for frac in (0.25, 0.5, 0.75):
    f = int(total * frac)
    out = f"{prefix}_f{f}.png"
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", mp4,
                    "-vf", f"select=eq(n\\,{f})", "-frames:v", "1", "-update", "1", out], check=True)
    size = os.path.getsize(out)
    if size > 1_000_000:
        img = imageio.imread(out)
        imageio.imwrite(out, img[::2, ::2])
        size = os.path.getsize(out)
    print(f"{out} frame={f} bytes={size}")
