import requests
import re
import json
import html
import time
import hashlib
import os
from googleapiclient.discovery import build
import isodate
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_API_KEY = ""
CHANNEL_ID = "UC6emrtiZcu4TMtDuZqFs-eA"

VIDEO_MAP = {
    "6A8hFdb34JE": {"tag": "ULTIMATE_SYNTHESIS_V2"},
    "rmLcxxDK5MU": {"tag": "ATOMIC_CESSATION_V3"}
}

COMMUNITY_POST_IDS = [
    "Ugkx8iLPNtrLrGD_DjG9icZ5Yw68CH3cxXYL"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def clean_js_string(text):
    if not text: return "NULL"
    text = html.unescape(str(text))
    text = text.replace('\\', '\\\\').replace('"', '\\"')
    text = text.replace('\r', '').replace('\n', '\\n')
    text = text.replace('|', '&#124;')
    return text.strip()

def mask_user(author_id):
    if not author_id: return "UNKNOWN_NODE"
    if author_id == CHANNEL_ID: return "USR_00"
    node_id = hashlib.md5(author_id.encode()).hexdigest()[:4].upper()
    return f"ENT_NODE_{node_id}"

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['th', 'en'])
        return "\\n".join([f"[{time.strftime('%M:%S', time.gmtime(e['start']))}] {e['text']}" for e in transcript_list])
    except: return "NULL"

def get_comments(youtube, video_id):
    try:
        request = youtube.commentThreads().list(part="snippet,replies", videoId=video_id, maxResults=20, textFormat="plainText")
        response = request.execute()
        feed = []
        for item in response.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comment_str = f"{mask_user(top.get('authorChannelId', {}).get('value', ''))}>>{clean_js_string(top['textDisplay'])} ({top['publishedAt'][:10]})"
            feed.append(comment_str)
        return "\\n---\\n".join(feed) if feed else "NO_COMMUNITY_SIGNALS"
    except: return "NULL"

def extract_community_post(p_id):
    url = f"https://www.youtube.com/post/{p_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        match = re.search(r'var ytInitialData = (\{.*?\});', r.text)
        if not match: return None
        data = json.loads(match.group(1))
        contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['backstagePostThreadRenderer']['post']['backstagePostRenderer']
        post_text = "".join([r['text'] for r in contents['contentText']['runs']]) if 'contentText' in contents else "NO_TEXT"
        likes = contents.get('voteCount', {}).get('simpleText', '0')
        return {"id": p_id, "content": post_text, "likes": likes, "date": "2026-03-28"}
    except: return None

def sync_archives():
    print(f"[SYSTEM] Connecting to YouTube Signal Spectrum...")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    try:
        ch_res = youtube.channels().list(part='snippet,statistics,contentDetails', id=CHANNEL_ID).execute()
        if not ch_res['items']: return
        ch_data = ch_res['items'][0]
        ch_name = ch_data['snippet']['title']
        total_views = ch_data['statistics']['viewCount']
        uploads_id = ch_data['contentDetails']['relatedPlaylists']['uploads']

        video_ids = set(VIDEO_MAP.keys())
        next_page = None
        while True:
            pl_res = youtube.playlistItems().list(part='contentDetails', playlistId=uploads_id, maxResults=50, pageToken=next_page).execute()
            for item in pl_res['items']: video_ids.add(item['contentDetails']['videoId'])
            next_page = pl_res.get('nextPageToken')
            if not next_page: break

        final_entries = []
        id_list = list(video_ids)
        for i in range(0, len(id_list), 50):
            v_res = youtube.videos().list(part='snippet,contentDetails,statistics,status', id=','.join(id_list[i:i+50])).execute()
            for v in v_res['items']:
                title = v['snippet']['title']
                dur_obj = isodate.parse_duration(v['contentDetails']['duration'])
                v_type = "VIDEO" if dur_obj.total_seconds() > 60 else "SHORT"
                tag = VIDEO_MAP.get(v['id'], {"tag": "SIGNAL_LOCKED"})['tag']
                final_entries.append({
                    'timestamp': v['snippet']['publishedAt'],
                    'log': (f'"{v["id"]}|{clean_js_string(title)}|{v["snippet"]["publishedAt"][:10]}|'
                            f'{str(dur_obj).split(".")[0].zfill(8)}|{v_type}|{v["status"]["privacyStatus"].upper()}|'
                            f'{v["statistics"].get("viewCount", "0")}|{v["statistics"].get("likeCount", "0")}|100|'
                            f'{v["statistics"].get("commentCount", "0")}|{tag}|{clean_js_string(v["snippet"]["description"])}|'
                            f'{clean_js_string(get_transcript(v["id"]))}|{clean_js_string(get_comments(youtube, v["id"]))}"')
                })

        for p_id in COMMUNITY_POST_IDS:
            p = extract_community_post(p_id)
            if p:
                final_entries.append({
                    'timestamp': p['date'] + "T00:00:00Z",
                    'log': (f'"{p["id"]}|{clean_js_string(p["content"])}|{p["date"]}|00:00:00|TEXT_POST|PUBLIC|'
                            f'0|{p["likes"]}|100|0|YOUTUBE_COMMUNITY|NULL|NULL|NULL"')
                })

        raw_logs = [
            f'"1500_1|U||Y|CHANNEL|{clean_js_string(ch_name)}|ESTB_2018|{len(final_entries)}_NODES|{total_views}_PULSES|62.9h_UPTIME",',
            f'"1500_2|U||Y|NOTICE|Relational Data Stream: Video + Consolidated Community Post. Anonymized via OpSec V7.",'
        ]

        time_index = 1505
        for entry in sorted(final_entries, key=lambda x: x['timestamp'], reverse=True):
            raw_logs.append(f'"{time_index:04d}_1|U||Y|ENTRY|{entry["log"][1:]},')
            time_index += 5

        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_file = os.path.join(script_dir, 'extracted_archives_logs.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(raw_logs))
        print(f"[SUCCESS] {len(final_entries)} Archives Mapped to {output_file}")

    except Exception as e: print(f"[ERROR] Sync Failed: {e}")

if __name__ == "__main__":
    sync_archives()