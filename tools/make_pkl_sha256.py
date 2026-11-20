# Liet ke toan bo pkl trong results/pkl kem SHA256, size, robot, motion, run.
# Muc dich: nguoi cham kiem chung tuyen bo tat dinh ma khong can 40 file pkl nang.
# Dung: python tools\make_pkl_sha256.py
import hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKL = os.path.join(ROOT, "results", "pkl")

ROBOTS = ["engineai_pm01", "booster_t1_29dof", "unitree_g1", "unitree_h1"]


def parse(name):
    stem = name[:-4] if name.endswith(".pkl") else name
    # v6_* : dieu kien nhieu
    if stem.startswith("v6_"):
        return "unitree_g1", "walk1_subject1", stem[3:]
    # fix_* : kiem chung KI-01 (ten file khong theo quy tac chung)
    if stem.startswith("fix_"):
        special = {
            "fix_dance1_g1": ("unitree_g1", "dance1_subject2"),
            "fix_walk3_subject1_unitree_g1": ("unitree_g1", "walk3_subject1"),
            "fix_walk4_subject1_booster_t1_29dof": ("booster_t1_29dof", "walk4_subject1"),
        }
        if stem in special:
            rb, mv = special[stem]
            return rb, mv, "ki01"
        return "unitree_g1", stem[4:], "ki01"
    robot = next((r for r in ROBOTS if stem.startswith("v5_" + r) or stem.startswith("v5_" + r)), None)
    if robot:
        rest = stem[len("v5_" + robot) + 1:]
        m = re.match(r"(.+?)(?:_run(\d+))?$", rest)
        return robot, m.group(1), (f"run{m.group(2)}" if m.group(2) else "single")
    if stem.startswith("g1_"):
        rest = stem[3:]
        m = re.match(r"(.+?)_(run\d+|warmup|evidence|no_rate_limit_\d+|rate_limit_\d+)$", rest)
        if m:
            return "unitree_g1", m.group(1), m.group(2)
        return "unitree_g1", rest, ""
    return "", "", ""


lines = []
for name in sorted(os.listdir(PKL)):
    if not name.endswith(".pkl"):
        continue
    p = os.path.join(PKL, name)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    size = os.path.getsize(p)
    rel = f"results/pkl/{name}"
    group = "v6-noise" if name.startswith("v6_") else "determinism(RV-23)"
    robot, motion, run = parse(name)
    lines.append(f"{h}  {size:>8}  {robot:<16} {motion:<18} {run:<20} {group:<18} {rel}")

header = [
    "# SHA256 toan bo pkl trong results/pkl — sinh bang tools/make_pkl_sha256.py",
    "# Cot: sha256  size_byte  robot  motion  run  group  path",
    "# group 'determinism(RV-23)': 40 file dung cho tuyen bo retarget tat dinh (cung cap robot+motion -> cung hash)",
    "# group 'v6-noise': pkl cua 16 dieu kien V6 (clean + 15 muc nhieu), moi dieu kien 1 lan",
]
out = os.path.join(ROOT, "results", "pkl_sha256.txt")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(header + lines) + "\n")
print(f"wrote {out}: {len(lines)} file")
