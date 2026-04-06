# -*- coding: utf-8 -*-
import requests
import re
import html
import base64
import time
from collections import defaultdict

GITHUB_USER = "ChimeraCoreLab"
GITHUB_TOKEN = ""

REPO_MAP = {
    "chimera-core-memory-synthesis": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.philosophicalAI", "thumb": 0},
    "noice-notice-nice-artifact": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.pyramid", "thumb": 0},
    "haunted-hole": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.hauntedHole", "thumb": 21},
    "chimera-manifesto-engine": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.philosophicalAI", "thumb": 0},
    "hoop-city-9000-nexus": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.hoopct", "thumb": 0},
    "Joise-Character-Model": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.JOSI1", "thumb": 0},
    "Philosophical-Chat-WebApp": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.PACW", "thumb": 0},
    "Architect-of-Intelligence-Godot": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.archOfIntel", "thumb": 0},
    "MFU-Portfolio-Video-Godot-Project": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.MFU", "thumb": 0},
    "national-artist-tribute-godot": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.NATIONART", "thumb": 0},
    "Godot-3.6-beta2-Eleva-Horror-Game": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.ELV", "thumb": 0},
    "Advanced-Chatbot-Blueprint": {"tree_style": 1, "gallery": "PROJECT_GALLERIES.CBP", "thumb": 0},
    "AI-for-Education-Chatbot": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.AEC", "thumb": 0},
    "Godot-4.3-Enemy-Moves-To-Player-Dark-Env": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.archOfIntel", "thumb": 1},
    "Philosophical-AI-Companion-Android": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.AIC", "thumb": 0},
    "Android-AI-Companion": {"tree_style": 2, "gallery": "PROJECT_GALLERIES.AIC", "thumb": 0}
}

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
BASE_URL = "https://api.github.com"

def clean_js_string(text):
    if not text: return ""
    text = html.unescape(str(text))
    text = text.replace('\\', '\\\\').replace('"', '\\"')
    text = text.replace('\r', '').replace('\n', '\\n')
    text = text.replace('|', '&#124;')
    return text.strip()

def get_tree_data(owner, repo, branch="main"):
    url = f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json().get('tree', [])
    except: pass
    return []

def format_tree_full(tree_items):
    lines = []
    num_dirs, num_files = 0, 0
    sorted_items = sorted(tree_items, key=lambda x: x['path'])
    for item in sorted_items:
        path_parts = item['path'].split('/')
        depth = len(path_parts) - 1
        name = path_parts[-1]
        prefix = "│   " * depth + "├── "
        if item['type'] == 'tree':
            num_dirs += 1
            lines.append(f"{prefix}{name}/")
        else:
            num_files += 1
            lines.append(f"{prefix}{name}")
    summary = f"\\n<span style='color:#8b949e; font-size:0.9em;'>{num_dirs} directories, {num_files} files</span>"
    return "\\n".join(lines) + summary

def format_tree_condensed(tree_items):
    structure = defaultdict(lambda: defaultdict(int))
    root_files = []
    num_dirs, num_files = 0, 0
    for item in tree_items:
        if item['type'] == 'tree':
            num_dirs += 1
            continue
        num_files += 1
        path_parts = item['path'].split('/')
        if len(path_parts) == 1: root_files.append(item['path'])
        else:
            folder = path_parts[0]
            ext = "*" + ('.' + item['path'].split('.')[-1] if '.' in item['path'] else '_no_ext')
            structure[folder][ext] += 1
    lines = []
    for folder, exts in sorted(structure.items()):
        lines.append(f"├── {folder}/")
        for ext, count in sorted(exts.items()):
            lines.append(f"│   ├── {ext} [{count} files]")
    for f in sorted(root_files): lines.append(f"├── {f}")
    summary = f"\\n<span style='color:#8b949e; font-size:0.9em;'>{num_dirs} directories, {num_files} files</span>"
    return "\\n".join(lines) + summary

def get_file_content(owner, repo, path):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8', errors='ignore')
    except: pass
    return None

def sync_arsenal():
    print(f"[SYSTEM] Connecting to GitHub Uplink...")
    try:
        u_req = requests.get(f"{BASE_URL}/users/{GITHUB_USER}", headers=HEADERS)
        user_data = u_req.json()
        r_req = requests.get(f"{BASE_URL}/users/{GITHUB_USER}/repos?per_page=100&sort=updated", headers=HEADERS)
        repos = r_req.json()
    except: return

    raw_logs = [f'"1400_1|U||G|PROFILE|{user_data.get("public_repos", 0)}|{sum(r.get("stargazers_count", 0) for r in repos)}|github.com/{GITHUB_USER}|STABLE_ACTIVE|PUBLIC_ENCRYPTED_READ",']

    time_index = 1405
    extra_targets = ["synthesis.py", "DATA_LICENSE.md", "render_manifesto.py", "requirements.txt", "github_arsenal_sync.py", "youtube_archives_sync.py", "wav_audit.py", "render_manifesto_v1_genesis.py", "render_manifesto_v2_ultimate.py", "render_manifesto_v3_atomic.py", "transcript.txt"]

    for r in repos:
        name = r['name']
        print(f"[DISTILLING] {name}...")
        config = REPO_MAP.get(name, {"tree_style": 2, "gallery": "NULL", "thumb": 0})
        tree_items = get_tree_data(GITHUB_USER, name, r.get('default_branch', 'main'))
        
        tree_str = format_tree_full(tree_items) if config['tree_style'] == 1 else format_tree_condensed(tree_items)
        readme = get_file_content(GITHUB_USER, name, "README.md") or "No README documentation found."

        other_files = []
        for item in tree_items:
            if item['type'] == 'blob':
                fname = item['path'].split('/')[-1]
                if fname in extra_targets:
                    content = get_file_content(GITHUB_USER, name, item['path'])
                    if content:
                        safe_content = clean_js_string(content).replace(";;", ";&#59;")
                        other_files.append(f"{item['path']}:{safe_content}")

        v_ref = "NULL"
        desc = r.get('description', '')
        if config['gallery'] != "NULL": v_ref = f"{config['gallery']}:{config['thumb']}"
        elif desc and "PROJECT_GALLERIES" in desc:
            match = re.search(r'PROJECT_GALLERIES\.([a-zA-Z0-9_]+)(?::\d+)?', desc)
            if match: v_ref = match.group(0)

        log_entry = (f'"{time_index:04d}_1|U||G|REPO|{clean_js_string(name)}|'
                     f'{"COMPLETED" if r.get("archived") else "ACTIVE_RESEARCH"}|{r.get("stargazers_count", 0)}|'
                     f'{clean_js_string(tree_str)}|{v_ref}|'
                     f'{r.get("license", {}).get("spdx_id", "MIT") if r.get("license") else "MIT"}|'
                     f'{clean_js_string(readme)}|{";;".join(other_files)}",')
        raw_logs.append(log_entry)
        time_index += 5
        time.sleep(0.5)

    with open('extracted_github_logs.txt', 'w', encoding='utf-8') as f: f.write("\n".join(raw_logs))
    print(f"[SUCCESS] Repositories saved to 'extracted_github_logs.txt'.")

if __name__ == "__main__":
    sync_arsenal()