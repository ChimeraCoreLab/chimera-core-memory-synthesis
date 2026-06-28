import os
import time
import re
import html
import base64
import requests
from collections import defaultdict
from datetime import datetime
from googleapiclient.discovery import build
import isodate
from youtube_transcript_api import YouTubeTranscriptApi

ITCHIO_API_KEY = ""
ITCHIO_USER = "ChimeraCoreLab"
GITHUB_USER = "ChimeraCoreLab"
GITHUB_TOKEN = ""
YOUTUBE_API_KEY = ""
CHANNEL_ID = "UC6emrtiZcu4TMtDuZqFs-eA"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
GH_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def decimal_to_base36(num, width=2):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if num == 0:
        return "0".zfill(width)
    res = ""
    while num > 0:
        res = chars[num % 36] + res
        num //= 36
    return res.zfill(width)

class SystemLogger:
    def __init__(self):
        now = datetime.now()
        self.d_str = now.strftime("%Y%m%d")
        self.t_str = now.strftime("%H%M")
        self.idx = 1
        self.logs = [f'"D:{self.d_str}",']

    def add(self, l_type, content):
        idx_b36 = decimal_to_base36(self.idx, 2)
        self.logs.append(f'"{self.t_str}{idx_b36}U{l_type}0{content}",')
        self.idx += 1

    def save(self, filename):
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.logs))

def clean_text(text):
    if not text: return "NULL"
    text = html.unescape(str(text))
    text = text.replace('\\', '\\\\').replace('"', '\\"')
    text = text.replace('\r', '').replace('\n', '\\n')
    text = text.replace('|', '&#124;')
    return text.strip()

def get_itch_web_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200: return {}
        desc_match = re.search(r'<div class="formatted_description user_formatted">(.*?)</div>', r.text, re.DOTALL)
        description = re.sub('<[^>]*>', '', desc_match.group(1)) if desc_match else "NULL"
        tags = re.findall(r'/directory/tag/[^"]+">([^<]+)</a>', r.text)
        noun_match = re.search(r'<td>Genre</td>\s*<td>\s*<a[^>]+>([^<]+)</a>', r.text)
        if not noun_match:
            noun_match = re.search(r'<td>Noun</td>\s*<td>([^<]+)</td>', r.text)
        yt_match = re.search(r'youtube\.com/embed/([^?"]+)', r.text)
        if not yt_match:
            yt_match = re.search(r'youtube\.com/watch\?v=([^&?"]+)', r.text)
        video_id = yt_match.group(1) if yt_match else "NULL"
        return {
            "desc": description.strip(),
            "tags": ", ".join(tags) if tags else "NULL",
            "noun": noun_match.group(1).strip() if noun_match else "artifact",
            "video_id": video_id
        }
    except: return {}

def sync_market(logger):
    api_headers = {"Authorization": ITCHIO_API_KEY}
    try:
        r = requests.get("https://itch.io/api/1/key/my-games", headers=api_headers, timeout=15)
        if r.status_code != 200: return
        games = r.json().get('games', [])
        
        games.sort(key=lambda g: g.get('published_at', ''), reverse=True)
        
        total_v = sum(g.get('views_count', 0) for g in games)
        total_d = sum(g.get('downloads_count', 0) for g in games)
        logger.add('K', f'PROFILE|{ITCHIO_USER}|{len(games)}|{total_v}|{total_d}')
        for g in games:
            g_id = g['id']
            web_data = get_itch_web_data(g['url'])
            f_r = requests.get(f"https://itch.io/api/1/key/game/{g_id}/uploads", headers=api_headers)
            f_data = f_r.json().get('uploads', []) if f_r.status_code == 200 else []
            f_list = [f"{u['filename']} ({u['size']//1048576}mb) - {u.get('downloads_count', 0)} DLs" for u in f_data]
            p_val = g.get('min_price', 0)
            try:
                price_float = float(p_val) / 100.0
                price_display = "${:.2f}".format(price_float) if price_float > 0 else "$0.00 or donate"
            except:
                price_display = "$0.00 or donate"
            v_link = f"https://www.youtube.com/watch?v={web_data['video_id']}" if web_data.get('video_id') != "NULL" else "NULL"
            entry = [
                clean_text(g['title']),
                clean_text(g.get('short_text', 'NULL')),
                clean_text(g.get('classification', 'Other')),
                "Downloadable" if g.get('type') != 'html' else "HTML",
                "RELEASED" if g.get('published') else "DRAFT",
                price_display,
                "2.00",
                "; ".join(f_list) if f_list else "NULL",
                clean_text(web_data.get('desc', 'NULL')),
                clean_text(web_data.get('tags', 'NULL')),
                "Yes (AI Assisted)" if "ai" in web_data.get('tags', "").lower() else "No",
                clean_text(web_data.get('noun', 'artifact')),
                "Instruction merged with description node.",
                "Comments Enabled",
                "Public",
                g.get('cover_url', 'NULL'),
                v_link,
                g.get('earnings', [{}])[0].get('amount', '0') if g.get('earnings') else '0',
                g.get('purchases_count', 0),
                g.get('views_count', 0),
                g.get('downloads_count', 0),
                g.get('published_at', 'NULL'),
                g.get('collections_count', 0),
                "0",
                "0"
            ]
            logger.add('K', f'ENTRY|{"|".join(map(str, entry))}')
            time.sleep(0.1)
    except: pass

def human_size(size_bytes):
    if size_bytes == 0: return "0B"
    units = ("B", "KB", "MB", "GB")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{round(size_bytes, 2)}{units[i]}"

def get_gh_tree(owner, repo, branch="main"):
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", headers=GH_HEADERS, timeout=15)
        if r.status_code == 200: return r.json().get('tree', [])
    except: pass
    return []

def format_tree_full(tree_items, created_at, latest_date):
    lines = []
    num_dirs, num_files, total_bytes = 0, 0, 0
    extensions = set()
    dir_files = defaultdict(list)
    sorted_items = sorted(tree_items, key=lambda x: x['path'])
    for item in sorted_items:
        if item['type'] == 'blob':
            num_files += 1
            total_bytes += item.get('size', 0)
            ext = os.path.splitext(item['path'])[1].lower() or '_no_ext'
            extensions.add(ext)
            parts = item['path'].split('/')
            if len(parts) > 1:
                dir_files["/".join(parts[:-1])].append(item)
        else: num_dirs += 1
    processed_dirs = set()
    for item in sorted_items:
        path = item['path']
        parts = path.split('/')
        depth = len(parts) - 1
        name = parts[-1]
        if item['type'] == 'tree':
            lines.append("│   " * depth + f"├── {name}/")
        else:
            if depth <= 1:
                lines.append("│   " * depth + f"├── {name} <span style='color:#444;font-size:0.85em;'>({human_size(item.get('size', 0))})</span>")
            else:
                parent_path = "/".join(parts[:-1])
                if parent_path in processed_dirs: continue
                files = dir_files[parent_path]
                if len(files) <= 4:
                    for f in files: lines.append("│   " * depth + f"├── {f['path'].split('/')[-1]} <span style='color:#444;font-size:0.85em;'>({human_size(f.get('size', 0))})</span>")
                else:
                    for f in files[:3]: lines.append("│   " * depth + f"├── {f['path'].split('/')[-1]} <span style='color:#444;font-size:0.85em;'>({human_size(f.get('size', 0))})</span>")
                    mid_files = files[3:-1]
                    mid_size = sum(f.get('size', 0) for f in mid_files)
                    mid_exts = set(os.path.splitext(f['path'])[1].lower() or '_no_ext' for f in mid_files)
                    lines.append("│   " * depth + f"├── ...[{len(mid_files)} files, {human_size(mid_size)}, {', '.join(sorted(mid_exts))}]")
                    f = files[-1]
                    lines.append("│   " * depth + f"├── {f['path'].split('/')[-1]} <span style='color:#444;font-size:0.85em;'>({human_size(f.get('size', 0))})</span>")
                processed_dirs.add(parent_path)
    return "\\n".join(lines) + f"\\n<span style='color:#8b949e; font-size:0.9em;'>{num_dirs} directories, {num_files} files &#124; Types: {', '.join(sorted(extensions))} &#124; Range: {created_at} - {latest_date} &#124; Total: {human_size(total_bytes)}</span>"

def get_gh_file(owner, repo, path):
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=GH_HEADERS, timeout=10)
        if r.status_code == 200: return base64.b64decode(r.json()['content']).decode('utf-8', errors='ignore')
    except: pass
    return None

def sync_github(logger):
    try:
        user_data = requests.get(f"https://api.github.com/users/{GITHUB_USER}", headers=GH_HEADERS).json()
        repos = requests.get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=updated", headers=GH_HEADERS).json()
        logger.add('G', f'PROFILE|{user_data.get("public_repos", 0)}|{sum(r.get("stargazers_count", 0) for r in repos)}|github.com/{GITHUB_USER}|STABLE_ACTIVE|PUBLIC_ENCRYPTED_READ')
        extra_targets = ["synthesis.py", "DATA_LICENSE.md", "wav_audit.py", "artifact_audit.py", "chimera_arsenal_sync.py", "injector.py", "zip_tree_generator.py", "prism_engine.sh"]
        for r in repos:
            name = r['name']
            tree_items = get_gh_tree(GITHUB_USER, name, r.get('default_branch', 'main'))
            c_at = datetime.strptime(r['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d')
            p_at = datetime.strptime(r['pushed_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d')
            tree_str = format_tree_full(tree_items, c_at, p_at)
            readme = get_gh_file(GITHUB_USER, name, "README.md") or "No README documentation found."
            other_files = []
            for item in tree_items:
                if item['type'] == 'blob' and item['path'].split('/')[-1] in extra_targets:
                    content = get_gh_file(GITHUB_USER, name, item['path'])
                    if content: other_files.append(f"{item['path']}:{clean_text(content).replace(';;', ';&#59;')}")
            logger.add('G', f'REPO|{clean_text(name)}|{"COMPLETED" if r.get("archived") else "ACTIVE_RESEARCH"}|{r.get("stargazers_count", 0)}|{clean_text(tree_str)}|{r.get("license", {}).get("spdx_id", "MIT") if r.get("license") else "MIT"}|{clean_text(readme)}|{";;".join(other_files)}')
            time.sleep(0.1)
    except: pass

def get_transcript(video_id):
    try:
        return "\\n".join([f"[{time.strftime('%M:%S', time.gmtime(e['start']))}] {e['text']}" for e in YouTubeTranscriptApi.get_transcript(video_id, languages=['th', 'en'])])
    except: return "NULL"

def sync_youtube(logger):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    try:
        ch_res = youtube.channels().list(part='snippet,statistics,contentDetails', id=CHANNEL_ID).execute()
        if not ch_res['items']: return
        ch_data = ch_res['items'][0]
        video_ids = set()
        next_page = None
        while True:
            pl_res = youtube.playlistItems().list(part='contentDetails', playlistId=ch_data['contentDetails']['relatedPlaylists']['uploads'], maxResults=50, pageToken=next_page).execute()
            for item in pl_res['items']: video_ids.add(item['contentDetails']['videoId'])
            next_page = pl_res.get('nextPageToken')
            if not next_page: break
        final_entries = []
        id_list = list(video_ids)
        for i in range(0, len(id_list), 50):
            v_res = youtube.videos().list(part='snippet,contentDetails,statistics,status', id=','.join(id_list[i:i+50])).execute()
            for v in v_res['items']:
                dur_obj = isodate.parse_duration(v['contentDetails']['duration'])
                final_entries.append({
                    'timestamp': v['snippet']['publishedAt'],
                    'log': f'{v["id"]}|{clean_text(v["snippet"]["title"])}|{v["snippet"]["publishedAt"][:10]}|{str(dur_obj).split(".")[0].zfill(8)}|VIDEO|{v["status"]["privacyStatus"].upper()}|{v["statistics"].get("viewCount", "0")}|{v["statistics"].get("likeCount", "0")}|100|0|SIGNAL_LOCKED|{clean_text(v["snippet"]["description"])}|{clean_text(get_transcript(v["id"]))}|NO_COMMUNITY_SIGNALS'
                })
        logger.add('Y', f'CHANNEL|{clean_text(ch_data["snippet"]["title"])}|ESTB_2018|{len(final_entries)}_NODES|{ch_data["statistics"]["viewCount"]}_PULSES')
        for entry in sorted(final_entries, key=lambda x: x['timestamp'], reverse=True):
            logger.add('Y', f'ENTRY|{entry["log"]}')
    except: pass

if __name__ == "__main__":
    sys_log = SystemLogger()
    sync_market(sys_log)
    sync_github(sys_log)
    sync_youtube(sys_log)
    sys_log.save('extracted_arsenal_sync_logs.txt')