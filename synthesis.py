# -*- coding: utf-8 -*-
import os
import datetime
import math
from pathlib import Path
import io
import html

class ChimeraOmniscience:
    def __init__(self, target_path):
        self.target = Path(target_path)
        self.peek_exts = {'.py', '.json', '.sh', '.csv', '.md'}
        self.peek_limit = 256
        self.g_stats = {'total_size': 0, 'total_files': 0}

    def human_size(self, size_bytes):
        if size_bytes == 0: return "0B"
        units = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        return f"{round(size_bytes / math.pow(1024, i), 2)} {units[i]}"

    def get_content_context(self, fpath):
        if fpath.suffix.lower() in {'.html', '.txt'}:
            return "[STRUCTURE_SIGNAL_ONLY]"
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(self.peek_limit).strip()
                sanitized = " ".join(content.split())
                preview = sanitized[:100] + "..." if len(sanitized) > 100 else sanitized
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
                if f.suffix.lower() in self.peek_exts or f.name == 'README.md':
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

    if not all(f.exists() for f in [file_raw_logs, file_index]):
        return

    prompt_content = ""
    if file_prompt.exists():
        with open(file_prompt, 'r', encoding='utf-8') as f:
            prompt_content = f.read().strip()

    eye = ChimeraOmniscience(base_path)
    census_data = eye.generate_report().replace('\n', '\\n').replace('"', '\\"')

    prev_raw = ""
    if file_prev_data.exists():
        with open(file_prev_data, 'r', encoding='utf-8') as f:
            prev_raw = f.read().strip().replace('\n', '\\n').replace('|', 'I').replace('"', '\\"')

    with open(file_raw_logs, 'r', encoding='utf-8') as f:
        raw_logs_content = f.read().strip()
        if raw_logs_content.startswith('const RAW_LOGS = ['):
            raw_logs_content = raw_logs_content[len('const RAW_LOGS = ['):].strip()
        if raw_logs_content.endswith('];'):
            raw_logs_content = raw_logs_content[:-2].strip()
        
        log_lines = [line.strip() for line in raw_logs_content.split('\n') if line.strip()]
        if log_lines and log_lines[-1].endswith(','):
            log_lines[-1] = log_lines[-1][:-1]
        clean_logs = "\n".join(log_lines)

    with open(file_index, 'r', encoding='utf-8') as f:
        index_content = f.read()

    today_str = datetime.datetime.now().strftime("%Y%m%d")
    
    extra_entries = f'"{today_str}_998|U||L|SYSTEM_CENSUS.log|{census_data}",\n'
    extra_entries += f'"{today_str}_999|U||L|previous_data.txt|{prev_raw}"'

    final_logs_block = f"const RAW_LOGS = [\n{clean_logs},\n\"D:{today_str}\",\n{extra_entries}\n];"

    start_marker = "const RAW_LOGS = ["
    end_marker = "\n];"
    
    s_idx = index_content.find(start_marker)
    if s_idx != -1:
        e_idx = index_content.find(end_marker, s_idx)
        if e_idx != -1:
            e_idx += len(end_marker)
            index_content = index_content[:s_idx] + final_logs_block + index_content[e_idx:]
        else:
            e_idx = index_content.rfind("];")
            if e_idx != -1 and e_idx > s_idx:
                e_idx += 2
                index_content = index_content[:s_idx] + final_logs_block + index_content[e_idx:]

    final_result = prompt_content + "\n" + index_content

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_result)

if __name__ == "__main__":
    perform_synthesis()