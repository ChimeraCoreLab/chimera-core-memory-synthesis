import os, math, datetime
from pathlib import Path
from PIL import Image

b = Path(__file__).parent
p = b / "Artifacts"
t = b / "artifact_logs.txt"
n = datetime.datetime.now().strftime("%Y%m%d")
m = {}

if t.exists():
    with open(t, 'r', encoding='utf-8') as f:
        for l in f:
            if "|I|" in l:
                s = l.strip().strip('",').split('|')
                if len(s) >= 9: m[s[4]] = s[8]

if not p.exists(): exit()

r = [f'"D:{n}",']
fs = sorted([x for x in p.iterdir() if x.suffix.lower() in ['.png', '.jpg', '.jpeg']])

for i, f in enumerate(fs):
    try:
        with Image.open(f) as img:
            w, h = img.size
            g = math.gcd(w, h)
            c = img.convert("RGB").resize((1, 1)).getpixel((0, 0))
            hx = f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
            ds = m.get(f.name, "PENDING_DESCRIPTION")
            r.append(f'"0000_{i:03d}|U||I|{f.name}|{w}x{h}|{w//g}:{h//g}|{hx}|{ds}",')
    except: pass

with open(t, "w", encoding="utf-8") as f:
    f.write("\n".join(r))