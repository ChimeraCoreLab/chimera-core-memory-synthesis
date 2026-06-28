import os
import sys
import zipfile
import math
import wave
import subprocess
import tempfile
import io
from collections import defaultdict
from datetime import datetime
try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import numpy as np
except ImportError:
    np = None

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if len(sys.argv) < 2:
    print("[-] USAGE: python zip_tree_generator.py [path_to_zip]")
    sys.exit(1)

ZIP_FILE_PATH = sys.argv[1]
base_dir = os.path.dirname(ZIP_FILE_PATH) or "."
base_name = os.path.splitext(os.path.basename(ZIP_FILE_PATH))[0]
OUTPUT_TXT_PATH = os.path.join(base_dir, f"{base_name}_tree.txt")

EXTRACT_IMAGE_METADATA = True
EXTRACT_AUDIO_METADATA = True
TARGET_DEPTH = 4
USE_FORCE_TRUNCATE = False
FORCE_TRUNCATE_FOLDERS = {"Artifacts"}
USE_FORCE_SHOW_ALL = False
FORCE_SHOW_ALL_FOLDERS = {"scenes", "scripts", "ACT"}
MAX_LIMIT = 4
SHOW_FIRST = 3

def human_size(size_bytes):
    if size_bytes == 0: return "0B"
    units = ("B", "KB", "MB", "GB")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    if i == 0: return f"{int(size_bytes)}B"
    return f"{size_bytes:.2f}{units[i]}"

def get_image_details(zf, member):
    if not EXTRACT_IMAGE_METADATA or Image is None: return ""
    try:
        with zf.open(member) as f:
            with Image.open(f) as img:
                w, h = img.size
                g = math.gcd(w, h)
                ratio = f"{w//g}:{h//g}"
                rgb_img = img.convert("RGB")
                pixel = rgb_img.getpixel((w // 2, h // 2))
                return f"|{w}x{h}|{ratio}|#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
    except: return ""

def get_audio_details(zf, member):
    if not EXTRACT_AUDIO_METADATA: return ""
    ext = os.path.splitext(member.filename)[1].lower()
    if ext not in ['.wav', '.mp3', '.ogg', '.flac']: return ""
    try:
        if ext == '.wav':
            with zf.open(member) as f:
                with wave.open(f, 'rb') as w_file:
                    frames = w_file.getnframes()
                    rate = w_file.getframerate()
                    duration = frames / float(rate)
                    if np is None: return f"|d:{duration:.2f}s"
                    raw_data = w_file.readframes(frames)
                    sampwidth = w_file.getsampwidth()
                    if sampwidth == 2: data = np.frombuffer(raw_data, dtype=np.int16)
                    elif sampwidth == 1: data = np.frombuffer(raw_data, dtype=np.uint8).astype(np.int16) - 128
                    else: data = []
                    if len(data) > 0:
                        mx_val = int(np.max(data))
                        mn_val = int(np.min(data))
                    else: mx_val = mn_val = 0
                    return f"|d:{duration:.2f}s|mx:{mx_val}|mn:{mn_val}"
        else:
            with zf.open(member) as src:
                temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
                try:
                    with os.fdopen(temp_fd, 'wb') as dst: dst.write(src.read())
                    duration = 0.0
                    ffprobe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", temp_path]
                    try:
                        output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.DEVNULL).decode('utf-8').strip()
                        duration = float(output)
                    except: pass
                    mx_val, mn_val = 0, 0
                    if np is not None:
                        ffmpeg_cmd = ["ffmpeg", "-y", "-i", temp_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
                        try:
                            raw_pcm = subprocess.check_output(ffmpeg_cmd, stderr=subprocess.DEVNULL)
                            data = np.frombuffer(raw_pcm, dtype=np.int16)
                            if len(data) > 0:
                                mx_val = int(np.max(data))
                                mn_val = int(np.min(data))
                        except: pass
                    if duration > 0:
                        if np is not None: return f"|d:{duration:.2f}s|mx:{mx_val}|mn:{mn_val}"
                        return f"|d:{duration:.2f}s"
                finally:
                    try: os.remove(temp_path)
                    except: pass
        return ""
    except: return ""

def get_node_size(node):
    tot = 0
    for k, v in node.items():
        if isinstance(v, dict): tot += get_node_size(v)
        else: tot += v[0]
    return tot

def parse_zip_to_trie(zip_path):
    trie = {}
    total_dirs, total_files, total_bytes = 0, 0, 0
    type_counts = defaultdict(int)
    timestamps = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.infolist():
                filename = member.filename
                try: filename = filename.encode('cp437').decode('utf-8')
                except: pass
                normalized_path = filename.replace('\\', '/')
                parts = [p for p in normalized_path.split('/') if p]
                if not parts: continue
                is_dir = normalized_path.endswith('/')
                if is_dir: total_dirs += 1
                else:
                    total_files += 1
                    total_bytes += member.file_size
                    ext = os.path.splitext(parts[-1])[1].lower() or '_no_ext'
                    type_counts[ext] += 1
                    try:
                        dt = datetime(*member.date_time)
                        timestamps.append(dt)
                    except: pass
                current = trie
                for i, part in enumerate(parts):
                    if i == len(parts) - 1 and not is_dir: current[part] = (member.file_size, member)
                    else:
                        if part not in current or not isinstance(current[part], dict): current[part] = {}
                        current = current[part]
        return trie, total_dirs, total_files, total_bytes, type_counts, timestamps
    except: return None

def build_tree_string(zf, node, depth=1, prefix="", current_dir_name=""):
    subdirs = {k: v for k, v in node.items() if isinstance(v, dict)}
    files = {k: v for k, v in node.items() if not isinstance(v, dict)}
    sorted_dirs = sorted(subdirs.items())
    sorted_files = sorted(files.items())
    num_dirs = len(sorted_dirs)
    num_files = len(sorted_files)
    lines = []
    for idx, (dir_name, dir_node) in enumerate(sorted_dirs):
        is_last = (idx == num_dirs - 1) and (num_files == 0)
        connector = "└── " if is_last else "├── "
        if depth > 1:
            size_str = human_size(get_node_size(dir_node))
            lines.append(f"{prefix}{connector}{dir_name}({size_str})/")
        else: lines.append(f"{prefix}{connector}{dir_name}/")
        new_prefix = prefix + ("    " if is_last else "│   ")
        lines.extend(build_tree_string(zf, dir_node, depth + 1, new_prefix, current_dir_name=dir_name))
    if num_files > 0:
        is_force_show_all = USE_FORCE_SHOW_ALL and (current_dir_name in FORCE_SHOW_ALL_FOLDERS)
        is_truncate_target = (depth >= TARGET_DEPTH) or (USE_FORCE_TRUNCATE and (current_dir_name in FORCE_TRUNCATE_FOLDERS))
        should_truncate = is_truncate_target and not is_force_show_all
        if should_truncate and num_files > MAX_LIMIT:
            for idx in range(SHOW_FIRST):
                name, (size, member) = sorted_files[idx]
                meta_img = get_image_details(zf, member) if name.lower().endswith(('.png', '.jpg', '.jpeg')) else ""
                meta_aud = get_audio_details(zf, member) if name.lower().endswith(('.png', '.jpg', '.jpeg', '.wav', '.mp3', '.ogg', '.flac')) else ""
                lines.append(f"{prefix}├── {name}({human_size(size)}{meta_img}{meta_aud})")
            mid_files = sorted_files[SHOW_FIRST:-1]
            groups = defaultdict(list)
            for name, (size, _) in mid_files:
                ext = os.path.splitext(name)[1].lower() or '_no_ext'
                groups[ext].append(size)
            parts = []
            for ext, sizes in sorted(groups.items()):
                parts.append(f"{ext}:{len(sizes)}({human_size(sum(sizes))})")
            lines.append(f"{prefix}├── ...[{','.join(parts)}]")
            last_name, (last_size, last_member) = sorted_files[-1]
            meta_img = get_image_details(zf, last_member) if last_name.lower().endswith(('.png', '.jpg', '.jpeg')) else ""
            meta_aud = get_audio_details(zf, last_member) if last_name.lower().endswith(('.png', '.jpg', '.jpeg', '.wav', '.mp3', '.ogg', '.flac')) else ""
            lines.append(f"{prefix}└── {last_name}({human_size(last_size)}{meta_img}{meta_aud})")
        else:
            for idx, (name, (size, member)) in enumerate(sorted_files):
                is_last = (idx == num_files - 1)
                connector = "└── " if is_last else "├── "
                meta_img = get_image_details(zf, member) if name.lower().endswith(('.png', '.jpg', '.jpeg')) else ""
                meta_aud = get_audio_details(zf, member) if name.lower().endswith(('.png', '.jpg', '.jpeg', '.wav', '.mp3', '.ogg', '.flac')) else ""
                lines.append(f"{prefix}{connector}{name}({human_size(size)}{meta_img}{meta_aud})")
    return lines

def execute_generation():
    print(f"[*] Ingesting: {ZIP_FILE_PATH}")
    result = parse_zip_to_trie(ZIP_FILE_PATH)
    if not result: return
    trie, total_dirs, total_files, total_bytes, type_counts, timestamps = result
    with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zf:
        tree_lines = build_tree_string(zf, trie)
    if timestamps:
        oldest = min(timestamps).strftime('%Y/%m/%d')
        latest = max(timestamps).strftime('%Y/%m/%d')
    else: oldest = latest = "UNKNOWN"
    types_list = [f"{ext}:{count}" for ext, count in sorted(type_counts.items())]
    types_str = ",".join(types_list)
    summary = f"[{total_dirs} directories, {total_files} files | Types: {types_str} | Range: {oldest} - {latest} | Total: {human_size(total_bytes)}]"
    tree_lines.append(summary)
    final_output = "\n".join(tree_lines)
    print("\n" + final_output + "\n")
    try:
        with open(OUTPUT_TXT_PATH, 'w', encoding='utf-8') as f: f.write(final_output)
        print(f"[+] SUCCESS: {OUTPUT_TXT_PATH}")
    except Exception as e: print(f"[-] FAILED: {e}")

if __name__ == "__main__":
    execute_generation()