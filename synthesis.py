# -*- coding: utf-8 -*-
import os
import datetime
import math
from pathlib import Path
import io
import html
import json

class ChimeraOmniscience:
    def __init__(self, target_path):
        self.target = Path(target_path)
        self.peek_exts = {'.txt', '.md', '.py', '.json', '.html', '.css', '.js', '.sh', '.csv'}
        self.peek_limit = 512
        self.g_stats = {'total_size': 0, 'total_files': 0}

    def human_size(self, size_bytes):
        if size_bytes == 0: return "0B"
        units = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        return f"{round(size_bytes / math.pow(1024, i), 2)} {units[i]}"

    def get_content_context(self, fpath):
        fname = fpath.name.lower()
        if "previous_data" in fname or "raw_logs" in fname:
            return "[SIGNAL_MAPPED_TO_CORE_DATABASE]"
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(self.peek_limit).strip()
                sanitized = " ".join(content.split())
                preview = sanitized[:120] + "..." if len(sanitized) > 120 else sanitized
                return html.escape(f"'{preview}'")
        except: return "[BINARY_DATA]"

    def generate_report(self):
        out = io.StringIO()
        out.write(f"// CHIMERA_CORE_CENSUS_REPORT\\n// TS: {datetime.datetime.now().isoformat()}\\n\\n")
        for f in sorted(self.target.iterdir()):
            if f.is_file() and not f.name.startswith('.'):
                stat = f.stat()
                self.g_stats['total_size'] += stat.st_size
                self.g_stats['total_files'] += 1
                out.write(f"[NODE] {f.name:<40} : {self.human_size(stat.st_size):>10}\\n")
                if f.suffix.lower() in self.peek_exts:
                    out.write(f"       └─ [SIGNAL]: {self.get_content_context(f)}\\n")
        out.write(f"\\nTOTAL NODES: {self.g_stats['total_files']} | VOLUME: {self.human_size(self.g_stats['total_size'])}")
        return out.getvalue()

def perform_synthesis():
    base_path = Path(__file__).parent
    file_prompt = base_path / 'prompt.txt'
    file_prev_data = base_path / 'previous_data.txt'
    file_raw_logs = base_path / 'RAW_LOGS.txt'
    file_index = base_path / 'index.html'
    file_output = base_path / 'chimera-core-memory-synthesis.html'

    if not all(f.exists() for f in [file_raw_logs, file_index]): return

    eye = ChimeraOmniscience(base_path)
    census_data = eye.generate_report()

    prompt_content = ""
    if file_prompt.exists():
        with open(file_prompt, 'r', encoding='utf-8') as f: 
            prompt_content = f.read()

    with open(file_prev_data, 'r', encoding='utf-8') as f:
        prev_raw = f.read().strip().replace('\n', '\\n').replace('|', 'I').replace('"', '\\"')
    
    with open(file_raw_logs, 'r', encoding='utf-8') as f:
        raw_logs_content = f.read().strip()
        if raw_logs_content.endswith('];'):
            raw_logs_content = raw_logs_content[:-2].strip()
        if raw_logs_content.startswith('const RAW_LOGS = ['):
            raw_logs_content = raw_logs_content[len('const RAW_LOGS = ['):].strip()

    with open(file_index, 'r', encoding='utf-8') as f:
        index_content = f.read()

    today_str = datetime.datetime.now().strftime("%Y%m%d")
    extra_entries = f'\n"D:{today_str}",'
    extra_entries += f'\n"0000_998|U||L|SYSTEM_CENSUS.log|{census_data}",'
    extra_entries += f'\n"0000_999|U||L|previous_data.txt|{prev_raw}"'

    final_logs = f"const RAW_LOGS = [\n{raw_logs_content},\n{extra_entries}\n];"
    final_html = prompt_content + "\n" + index_content
    
    start_marker = "const RAW_LOGS = ["
    end_marker = "];"
    s_idx = final_html.find(start_marker)
    if s_idx != -1:
        e_idx = final_html.find(end_marker, s_idx) + len(end_marker)
        final_html = final_html[:s_idx] + final_logs + final_html[e_idx:]

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == "__main__":
    perform_synthesis()