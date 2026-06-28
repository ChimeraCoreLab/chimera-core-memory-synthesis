import os
import re
from datetime import datetime

d = os.path.dirname(os.path.abspath(__file__))
f_in = os.path.join(d, "input.txt")
f_tgt = os.path.join(d, "RAW_LOGS.txt")
f_bak = os.path.join(d, "raw_logs_backup.txt")

def decimal_to_base36(num, width=2):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num == 0:
        return "0".zfill(width)
    res = ""
    while num > 0:
        res = chars[num % 36] + res
        num //= 36
    return res.zfill(width)

if not os.path.exists(f_in) or os.path.getsize(f_in) == 0:
    exit()

with open(f_in, 'r', encoding='utf-8') as f:
    data = f.read()

segs = [s.strip() for s in data.split("[NEXT_SIGNAL_9369]") if s.strip()]
if not segs:
    exit()

now = datetime.now()
d_str = f"D:{now.strftime('%Y%m%d')}"
h_str = now.strftime('%H%M')

with open(f_tgt, 'rb+') as f:
    f.seek(0, os.SEEK_END)
    sz = f.tell()
    offset = min(sz, 8192)
    f.seek(sz - offset)
    chunk = f.read(offset).decode('utf-8', errors='ignore')

    ld = ""
    ds = re.findall(r'"(D:\d{8})"', chunk)
    if ds: ld = ds[-1]

    lh = ""
    li = 0
    ls = re.findall(r'"(\d{4})([0-9a-z]{2})[A-Z]{2}[0-2]', chunk)
    if ls:
        lh, ix_b36 = ls[-1]
        li = int(ix_b36, 36)

    pos = chunk.rfind('];')
    if pos != -1:
        actual_pos = sz - offset + pos
        q_idx = chunk[:pos].rstrip().rfind('"')
        if q_idx != -1:
            f.seek(sz - offset + q_idx + 1)
            f.truncate()
            f.write(b'",\n')
        else:
            lb = chunk.find('[')
            if lb != -1:
                f.seek(sz - offset + lb + 1)
                f.truncate()
                f.write(b'\n')
    else:
        f.seek(0, os.SEEK_END)

    res = []
    if ld != d_str:
        res.append(f'"{d_str}"')

    for s in segs:
        s = s.replace('\\', '\\\\').replace('"', "'")
        s = re.sub(r'[ \t]{2,}', ' ', s)
        s = s.replace('\r', '').replace('\n', '\\n')

        if h_str == lh:
            li += 1
        else:
            lh = h_str
            li = 1
        
        idx_b36 = decimal_to_base36(li, 2)
        res.append(f'"{h_str}{idx_b36}UM0{s}"')

    f.write(',\n'.join(res).encode('utf-8'))
    f.write(b'\n];')

with open(f_bak, 'a', encoding='utf-8') as f:
    f.write(f"\n--- {now.isoformat()} ---\n{data}")

open(f_in, 'w').close()