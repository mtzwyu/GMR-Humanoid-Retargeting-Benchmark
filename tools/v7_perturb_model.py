# V7 — sua tam thoi model XML cua robot (khoi luong / ma sat) de chay lai retarget.
# Sau moi lan chay PHAI khoi phuc: git -C third_party/GMR checkout -- <xml>
# Dung:
#   python tools\v7_perturb_model.py --xml <xml> --mass-factor 1.2
#   python tools\v7_perturb_model.py --xml <xml> --friction 1.5
import argparse
import re

p = argparse.ArgumentParser()
p.add_argument("--xml", required=True)
p.add_argument("--mass-factor", type=float, default=None)
p.add_argument("--friction", type=float, default=None)
a = p.parse_args()

s = open(a.xml, encoding="utf-8").read()
n_mass = n_fric = 0

if a.mass_factor is not None:
    def rep(m):
        global n_mass
        n_mass += 1
        return f'mass="{float(m.group(1)) * a.mass_factor:.6f}"'
    s = re.sub(r'mass="([0-9.eE+-]+)"', rep, s)

if a.friction is not None:
    # bo moi friction cu (co the nam tren dong tiep theo), roi gan lai cho TAT CA geom
    s = re.sub(r'\s+friction="[^"]*"', "", s)

    def add_f(m):
        global n_fric
        n_fric += 1
        return f'<geom friction="{a.friction} 0.005 0.0001"'
    s = re.sub(r"<geom(?=[\s>])", add_f, s)

open(a.xml, "w", encoding="utf-8", newline="\n").write(s)
print(f"perturbed {a.xml}: mass_factor={a.mass_factor} ({n_mass} the) friction={a.friction} ({n_fric} geom)")
