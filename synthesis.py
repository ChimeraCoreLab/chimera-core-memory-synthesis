import os
import datetime
from pathlib import Path
import re

def compress_html_markup(html_str):
    html_str = re.sub(r'\x3c!--.*?--\x3e', '', html_str, flags=re.DOTALL)

    lines = []
    for line in html_str.splitlines():
        line_str = line.strip()
        if line_str and not line_str.startswith('//'):
            lines.append(line_str)

    return '\n'.join(lines)

def perform_synthesis():
    base_path = Path(__file__).parent
    file_prompt = base_path / 'prompt.txt'
    file_raw_logs = base_path / 'RAW_LOGS.txt'
    file_index = base_path / 'index.html'
    file_output = base_path / 'chimera-core-memory-synthesis.html'
    file_prompt_logs = base_path / 'RAW_LOGS.js'

    if not all(f.exists() for f in [file_raw_logs, file_index]):
        print('CRITICAL_ERROR: MISSING_CORE_FILES')
        return

    today_str = datetime.datetime.now().strftime('%Y%m%d')
    prompt_content = ''
    if file_prompt.exists():
        with open(file_prompt, 'r', encoding='utf-8') as f:
            prompt_content = f.read().strip()

        date_pattern = r'\(เช่น [\x22\']D:20211225[\x22\'],.*?\)|\(เช่น [\x22\']D:20211225[\x22\'],.*?\)'
        new_date_range = f'(เช่น \'D:20211225\', \'D:20211228\', \'D:20211229\', ..., \'D:{today_str}\')'
        prompt_content = re.sub(date_pattern, new_date_range, prompt_content)

    with open(file_raw_logs, 'r', encoding='utf-8') as f:
        log_content = f.read().strip()
        if log_content.startswith('const RAW_LOGS = ['):
            log_content = log_content[18:]
        if log_content.endswith('];'):
            log_content = log_content[:-2]
        elif log_content.endswith(']'):
            log_content = log_content[:-1]

        log_content = log_content.strip()
        if log_content.endswith(','):
            log_content = log_content[:-1]

    clean_lines = []
    for line in log_content.splitlines():
        line_str = line.strip().strip(',')
        if line_str:
            clean_lines.append(line_str)

    final_logs_js = f'const RAW_LOGS = [{",".join(clean_lines)},\'D:{today_str}\'];'

    with open(file_index, 'r', encoding='utf-8') as f:
        html_markup = f.read()

    s_idx = html_markup.find('const RAW_LOGS = [')
    if s_idx != -1:
        e_idx = html_markup.find('];', s_idx)
        if e_idx != -1:
            e_idx += 2
            html_markup = html_markup[:s_idx] + final_logs_js + html_markup[e_idx:]
    else:
        html_markup = html_markup.replace('let RAW_DATA = [];', f'let RAW_DATA = [];\n{final_logs_js}')

    html_markup = compress_html_markup(html_markup)
    final_artifact = prompt_content + '\n' + html_markup if prompt_content else html_markup

    with open(file_output, 'w', encoding='utf-8') as f:
        f.write(final_artifact)

    prompt_one_line = prompt_content.replace('\r', '').replace('\n', '\\n').replace('\x22', '\'')
    logs_one_line = final_logs_js.replace('\x22', '\'')

    with open(file_prompt_logs, 'w', encoding='utf-8') as f:
        f.write(prompt_one_line + ' ' + logs_one_line)

    print(f'SYNTHESIS_SUCCESSFUL: {file_output.name} GENERATED')
    print(f'PROMPT_LOGS_SUCCESSFUL: {file_prompt_logs.name} GENERATED')

if __name__ == '__main__':
    perform_synthesis()