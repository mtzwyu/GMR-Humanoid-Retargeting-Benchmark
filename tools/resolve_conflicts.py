# Giai quyet xung dot merge: giu phan HEAD (ban cua Run) trong moi khoi conflict.
# Dung: python resolve_conflicts.py <file> [<file> ...]
import sys

for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    out, state = [], "normal"
    for ln in lines:
        if ln.startswith("<<<<<<<"):
            state = "head"
            continue
        if ln.startswith("=======") and state == "head":
            state = "theirs"
            continue
        if ln.startswith(">>>>>>>") and state == "theirs":
            state = "normal"
            continue
        if state in ("normal", "head"):
            out.append(ln)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(out)
    print(f"resolved {path}: {len(lines)} -> {len(out)} lines")
