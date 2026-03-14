# -*- coding: utf-8 -*-
import os
import datetime
import math
from pathlib import Path
from collections import defaultdict, Counter
import io
import html

class ChimeraOmniscience:
    def __init__(self, target_path):
        self.target = Path(target_path)
        self.peek_exts = {'.txt', '.md', '.py', '.json', '.html', '.css', '.js', '.sh', '.csv'}
        self.exclude_dirs = {'__pycache__', '.git', '.vscode'}
        self.preview_limit_subdir = 5
        self.peek_limit = 512
        self.g_stats = {'total_size': 0, 'total_files': 0, 'ext_counts': Counter()}

    def human_size(self, size_bytes):
        if size_bytes == 0: return "0B"
        units = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        return f"{round(size_bytes / math.pow(1024, i), 2)} {units[i]}"

    def get_content_context(self, fpath):
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(self.peek_limit).strip()
                sanitized = " ".join(content.split())
                preview = sanitized[:120] + "..." if len(sanitized) > 120 else sanitized
                return html.escape(f"'{preview}'")
        except: return "[BINARY_DATA]"

    def generate_report(self):
        out = io.StringIO()
        out.write(f"// CHIMERA_CORE_CENSUS_REPORT\n// TS: {datetime.datetime.now().isoformat()}\n\n")
        for f in sorted(self.target.iterdir()):
            if f.is_file() and not f.name.startswith('.'):
                stat = f.stat()
                self.g_stats['total_size'] += stat.st_size
                self.g_stats['total_files'] += 1
                self.g_stats['ext_counts'][f.suffix.lower()] += 1
                out.write(f"[NODE] {f.name:<40} | {self.human_size(stat.st_size):>10}\n")
                if f.suffix.lower() in self.peek_exts:
                    out.write(f"       └─ [SIGNAL]: {self.get_content_context(f)}\n")
        out.write(f"\nTOTAL NODES: {self.g_stats['total_files']} | VOLUME: {self.human_size(self.g_stats['total_size'])}\n")
        return out.getvalue()

def perform_synthesis():
    base_path = Path(__file__).parent
    file_prompt = base_path / 'prompt.txt'
    file_prev_data = base_path / 'previous_data.txt'
    file_raw_logs = base_path / 'RAW_LOGS.txt'
    file_index = base_path / 'index.html'
    file_output = base_path / 'chimera-core-memory-synthesis.html'

    print("[*] INITIATING DATA ALCHEMY...")
    eye = ChimeraOmniscience(base_path)
    census_report = eye.generate_report()

    for f in [file_prompt, file_prev_data, file_raw_logs, file_index]:
        if not f.exists():
            print(f"[ERROR] Missing: {f.name}")
            return

    with open(file_prompt, 'r', encoding='utf-8') as f: prompt_content = f.read()
    with open(file_prev_data, 'r', encoding='utf-8') as f: prev_data_content = f.read()
    with open(file_raw_logs, 'r', encoding='utf-8') as f: raw_logs_content = f.read()
    with open(file_index, 'r', encoding='utf-8') as f: index_content = f.read()

    safe_census = census_report.replace("`", "\\`").replace("${", "\\${")
    census_block = f"""<details class="file-viewer" open><summary style="color:var(--c-cyan); font-weight:bold;">SYSTEM_CENSUS: CHIMERA_AUDIT_V9.log</summary><div class="file-content" style="white-space: pre-wrap; font-size: 0.7rem; line-height: 1.2; color: #aaa; background: #000; max-height: 500px; overflow-y: auto; border: 1px solid var(--c-cyan);">{safe_census}</div></details>"""

    final_html = prompt_content + "\n" + index_content
    
    start_logs_marker = "const RAW_LOGS = ["
    end_logs_marker = "];"
    s_idx = final_html.find(start_logs_marker)
    if s_idx != -1:
        e_idx = final_html.find(end_logs_marker, s_idx) + len(end_logs_marker)
        final_html = final_html[:s_idx] + raw_logs_content + final_html[e_idx:]

    if "// CENSUS_DATA_STREAM" in final_html:
        final_html = final_html.replace("// CENSUS_DATA_STREAM", census_block)
    
    if "// Kill the noise..." in final_html:
        final_html = final_html.replace("// Kill the noise...", html.escape(prev_data_content))

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"[SUCCESS] Artifact synthesized: {file_output.name}")
    print(f"Final size: {os.path.getsize(file_output) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    perform_synthesis()
