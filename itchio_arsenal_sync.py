# -*- coding: utf-8 -*-
import requests
import json
import re
import html
import time

ITCHIO_API_KEY = ""
ITCHIO_USER = "ChimeraCoreLab"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_js(t):
    if not t: return "NULL"
    return html.unescape(str(t)).replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n').replace('|', '&#124;').strip()

def scrape_web_data(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200: return {}
        
        desc_match = re.search(r'<div class="formatted_description user_formatted">(.*?)</div>', r.text, re.DOTALL)
        description = re.sub('<[^>]*>', '', desc_match.group(1)) if desc_match else "NULL"
        
        tags = re.findall(r'/directory/tag/[^"]+">([^<]+)</a>', r.text)
        
        noun_match = re.search(r'<td>Genre</td>\s*<td>\s*<a[^>]+>([^<]+)</a>', r.text)
        if not noun_match:
            noun_match = re.search(r'<td>Noun</td>\s*<td>([^<]+)</td>', r.text)

        return {
            "desc": description.strip(),
            "tags": ", ".join(tags) if tags else "NULL",
            "noun": noun_match.group(1).strip() if noun_match else "artifact"
        }
    except: return {}

def sync_market():
    api_headers = {"Authorization": ITCHIO_API_KEY}
    try:
        r = requests.get("https://itch.io/api/1/key/my-games", headers=api_headers, timeout=15)
        if r.status_code != 200: return
        
        games = r.json().get('games', [])
        total_v = sum(g.get('views_count', 0) for g in games)
        total_d = sum(g.get('downloads_count', 0) for g in games)
        
        logs = [f'"1300_1|U||K|PROFILE|{ITCHIO_USER}|{len(games)}|{total_v}|{total_d}",']
        
        idx = 1305
        for g in games:
            g_id = g['id']
            g_url = g['url']
            
            web_data = scrape_web_data(g_url)
            
            f_r = requests.get(f"https://itch.io/api/1/key/game/{g_id}/uploads", headers=api_headers)
            f_data = f_r.json().get('uploads', []) if f_r.status_code == 200 else []
            f_list = [f"{u['filename']} ({u['size']//1048576}mb) - {u.get('downloads_count', 0)} DLs" for u in f_data]

            # Logic check for Trailer mapping
            v_link = "https://www.youtube.com/watch?v=rmLcxxDK5MU" if "ENGINE" in g['title'].upper() else "https://www.youtube.com/watch?v=suNZLquZLgM"

            entry = [
                clean_js(g['title']),
                clean_js(g.get('short_text', 'NULL')),
                clean_js(g.get('classification', 'Other')),
                "Downloadable" if g.get('type') != 'html' else "HTML",
                "RELEASED" if g.get('published') else "DRAFT",
                "$0 or donate" if g.get('min_price', 0) == 0 else f"${g['min_price']}",
                "2.00",
                "; ".join(f_list) if f_list else "NULL",
                clean_js(web_data.get('desc', 'NULL')),
                clean_js(web_data.get('tags', 'NULL')),
                "Yes (AI Assisted)" if "ai" in web_data.get('tags', '').lower() else "No",
                clean_js(web_data.get('noun', 'artifact')),
                "Instruction merged with description node.",
                "Comments Enabled",
                "Public",
                g.get('cover_url', 'NULL'),
                v_link,
                g.get('earnings', [{}])[0].get('amount', '0') if g.get('earnings') else '0',
                g.get('purchases_count', 0),
                g.get('views_count', 0),
                g.get('downloads_count', 0),
                "★ 5.0",
                g.get('collections_count', 0),
                "0", "0"
            ]
            
            logs.append(f'"{idx:04d}_1|U||K|ENTRY|{"|".join(map(str, entry))}",')
            idx += 5

        with open('extracted_market_logs.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(logs))

    except Exception as e: pass

if __name__ == "__main__":
    sync_market()