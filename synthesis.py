import os
import datetime
import math
from pathlib import Path
import io
import html
import re

class ChimeraOmniscience:
    def __init__(self, target_path):
        self.target = Path(target_path)
        self.peek_exts = {'.py', '.json', '.sh', '.csv', '.md', '.html', '.txt'}
        self.g_stats = {'total_size': 0, 'total_files': 0}

    def human_size(self, size_bytes):
        if size_bytes == 0: return "0B"
        units = ("B", "KB", "MB", "GB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        return f"{round(size_bytes / math.pow(1024, i), 2)} {units[i]}"

    def get_content_context(self, fpath):
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024).strip()
                sanitized = content.replace('\n', ' ').replace('|', 'I')
                preview = sanitized[:150] + "..." if len(sanitized) > 150 else sanitized
                return html.escape(preview)
        except:
            return "[BINARY_DATA]"

    def generate_report(self):
        out = io.StringIO()
        out.write(f"// CHIMERA_CORE_CENSUS_REPORT\n")
        out.write(f"// TIMESTAMP: {datetime.datetime.now().isoformat()}\n\n")
        
        files = sorted([f for f in self.target.iterdir() if f.is_file() and not f.name.startswith('.')])
        for f in files:
            stat = f.stat()
            self.g_stats['total_size'] += stat.st_size
            self.g_stats['total_files'] += 1
            out.write(f"[NODE] {f.name:<40} : {self.human_size(stat.st_size):>10}\n")
            if f.suffix.lower() in self.peek_exts:
                out.write(f"       └─ [SIGNAL]: {self.get_content_context(f)}\n")
        
        out.write(f"\nTOTAL_NODES: {self.g_stats['total_files']} | AGGREGATE_VOLUME: {self.human_size(self.g_stats['total_size'])}\n")
        out.write(f"// STATUS: ALL_SYSTEMS_MAPPED")
        return out.getvalue()

def perform_synthesis():
    base_path = Path(__file__).parent
    file_prompt = base_path / 'prompt.txt'
    file_raw_logs = base_path / 'RAW_LOGS.txt'
    file_index = base_path / 'index.html'
    file_output = base_path / 'chimera-core-memory-synthesis.html'

    if not all(f.exists() for f in [file_raw_logs, file_index]):
        print("CRITICAL_ERROR: MISSING_CORE_FILES")
        return

    prompt_content = ""
    if file_prompt.exists():
        with open(file_prompt, 'r', encoding='utf-8') as f:
            prompt_content = f.read().strip()

    eye = ChimeraOmniscience(base_path)
    report_raw = eye.generate_report()
    
    report_encoded = report_raw.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"').replace('$', '\\$')
    
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    
    with open(file_raw_logs, 'r', encoding='utf-8') as f:
        log_content = f.read().strip()
        log_content = re.sub(r'^const\s+RAW_LOGS\s*=\s*\[', '', log_content)
        log_content = re.sub(r'\];?$', '', log_content).strip()
        if log_content.endswith(','):
            log_content = log_content[:-1]

    daily_node = f'"{today_str}_998|U||L|SYSTEM_CENSUS.log|{report_encoded}"'
    
    if not log_content:
        final_logs_js = f"const RAW_LOGS = [\n\"D:{today_str}\",\n{daily_node}\n];"
    else:
        final_logs_js = f"const RAW_LOGS = [\n{log_content},\n\"D:{today_str}\",\n{daily_node}\n];"

    with open(file_index, 'r', encoding='utf-8') as f:
        html_markup = f.read()

    s_idx = html_markup.find("const RAW_LOGS = [")
    if s_idx != -1:
        e_idx = html_markup.find("];", s_idx)
        if e_idx != -1:
            e_idx += 2
            html_markup = html_markup[:s_idx] + final_logs_js + html_markup[e_idx:]
    else:
        html_markup = html_markup.replace("let RAW_DATA = [];", f"let RAW_DATA = [];\n{final_logs_js}")

    final_artifact = prompt_content + "\n" + html_markup if prompt_content else html_markup

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_artifact)
    
    print(f"SYNTHESIS_SUCCESSFUL: {file_output.name} GENERATED")

if __name__ == "__main__":
    perform_synthesis()
