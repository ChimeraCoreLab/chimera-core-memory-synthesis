import os, math, datetime, re
from pathlib import Path
from PIL import Image

b = Path(__file__).parent
p = b / "Artifacts"
t = b / "artifact_logs.txt"
m = {}

def decimal_to_base36(num, width=2):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num == 0:
        return "0".zfill(width)
    res = ""
    while num > 0:
        res = chars[num % 36] + res
        num //= 36
    return res.zfill(width)

if t.exists():
    with open(t, 'r', encoding='utf-8') as f:
        current_date_in_file = None
        for l in f:
            clean_l = l.strip().strip('",').strip("'")
            if not clean_l:
                continue
            if clean_l.startswith("D:"):
                current_date_in_file = clean_l[2:].strip()
                continue
            if "|" in clean_l:
                s = clean_l.split('|')
                if len(s) >= 9 and s[3] == 'I':
                    meta = s[0].split('_')
                    time_str = meta[0].strip()
                    filename = s[4].strip()
                    desc = s[8].strip()
                    m[filename] = (desc, current_date_in_file, time_str)
                elif len(s) >= 5 and len(s[0]) > 8 and s[0][6] == 'U' and s[0][7] == 'I':
                    time_str = s[0][0:4].strip()
                    ref_flag = s[0][8]
                    header_len = 15 if ref_flag == '1' else (20 if ref_flag == '2' else 9)
                    filename = s[0][header_len:].strip()
                    desc = s[4].strip()
                    m[filename] = (desc, current_date_in_file, time_str)

if not p.exists():
    exit()

fs = [x for x in p.iterdir() if x.suffix.lower() in ['.png', '.jpg', '.jpeg']]
raw_data = []

for f in fs:
    try:
        with Image.open(f) as img:
            w, h = img.size
            g = math.gcd(w, h)
            c = img.convert("RGB").resize((1, 1)).getpixel((0, 0))
            hx = f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"
            
            if f.name in m:
                ds, hist_date, hist_time = m[f.name]
                base_desc = re.sub(r'\s*\(\d{8}\)$|\s*PEND_\d{8}$', '', ds).strip()
                ds = "PEND" if base_desc == "PEND" else base_desc
                mdate = hist_date if hist_date else datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y%m%d")
                hhmm = hist_time if hist_time else datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%H%M")
            else:
                ds = "PEND"
                mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
                hhmm = mtime.strftime("%H%M")
                mdate = mtime.strftime("%Y%m%d")

            raw_data.append({
                'file_path': f,
                'mdate': mdate,
                'hhmm': hhmm,
                'w': w,
                'h': h,
                'g': g,
                'hx': hx,
                'ds': ds
            })
    except:
        pass

raw_data.sort(key=lambda x: (-int(x['mdate']), x['hhmm']))

for idx, item in enumerate(raw_data):
    item['global_idx'] = idx

raw_data.sort(key=lambda x: (int(x['mdate']), x['hhmm']))

r = []
current_date = None

for item in raw_data:
    if item['mdate'] != current_date:
        current_date = item['mdate']
        r.append(f'"D:{current_date}",')

    idx_b36 = decimal_to_base36(item['global_idx'], 2)
    line = f'"{item["hhmm"]}{idx_b36}UI0{item["file_path"].name}|{item["w"]}x{item["h"]}|{item["w"]//item["g"]}:{item["h"]//item["g"]}|{item["hx"]}|{item["ds"]}",'
    r.append(line)

with open(t, "w", encoding="utf-8") as f:
    f.write("\n".join(r))