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
                content = f.read(256).strip()
                preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content
                return html.escape(preview)
        except:
            return "[BINARY_DATA]"

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
    today_str = datetime.datetime.now().strftime("%Y%m%d")

    with open(file_raw_logs, 'r', encoding='utf-8') as f:
        raw_content = f.read().strip()
        raw_content = re.sub(r'^const RAW_LOGS\s*=\s*\[', '', raw_content)
        raw_content = re.sub(r'\];?$', '', raw_content).strip()
        if raw_content.endswith(','):
            raw_content = raw_content[:-1]

    if not raw_content:
        final_logs_js = f"const RAW_LOGS = [\n\"D:{today_str}\",\n\"{today_str}_998|U||L|SYSTEM_CENSUS.log|{census_data}\"\n];"
    else:
        daily_injection = f',\n"D:{today_str}",\n"{today_str}_998|U||L|SYSTEM_CENSUS.log|{census_data}"'
        final_logs_js = f"const RAW_LOGS = [\n{raw_content}{daily_injection}\n];"

    with open(file_index, 'r', encoding='utf-8') as f:
        html_content = f.read()

    s_idx = html_content.find("const RAW_LOGS = [")
    if s_idx != -1:
        e_idx = html_content.find("];", s_idx)
        if e_idx != -1:
            e_idx += 2
            html_content = html_content[:s_idx] + final_logs_js + html_content[e_idx:]
    else:
        html_content = html_content.replace("let RAW_DATA = [];", f"let RAW_DATA = [];\n{final_logs_js}")

    final_result = prompt_content + "\n" + html_content if prompt_content else html_content

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_result)

if __name__ == "__main__":
    perform_synthesis()
