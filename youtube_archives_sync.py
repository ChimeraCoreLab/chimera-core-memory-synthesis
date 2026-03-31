# -*- coding: utf-8 -*-
import html
import time
import re
import base64
import hashlib
from googleapiclient.discovery import build
import isodate
from youtube_transcript_api import YouTubeTranscriptApi

YOUTUBE_API_KEY = ""
CHANNEL_ID = "UC6emrtiZcu4TMtDuZqFs-eA"

VIDEO_MAP = {
    "mXLSUwlZYdQ": {"tag": "READY_TO_SYNTHESIZE"},
    "aXRiXD1PtEs": {"tag": "INITIALIZE_PORTFOLIO_STREAM"},
    "TBx6ZQZo940": {"tag": "DECODE_CINEMATIC_DATA"},
    "k3WDd9ohpCg": {"tag": "VIRTUAL_TRIBUTE_UPLINK"},
    "suNZLquZLgM": {"tag": "ACCESS_GRAVEYARD_LOGS"},
    "dcT_wgk8QQU": {"tag": "STREAM_FINALE_SIGNAL"},
    "kXLAHmE7FCQ": {"tag": "START_MALL_SURVEILLANCE"},
    "9pXJkHeX4tg": {"tag": "ANALYZE_AGI_DEFINITION"},
    "uQ22siZ2riQ": {"tag": "CLEANING_SHIFT_SIGNAL"},
    "4sTuf_fG0B4": {"tag": "VOXEL_WORLD_RECOVERY"},
    "Ym1gyQvkfgs": {"tag": "RETAIL_LOGIC_INIT"},
    "BosI8Qg_sYg": {"tag": "ELEVA_SOURCE_PREVIEW"},
    "p-we_yoI6xE": {"tag": "PHYSICS_MODULE_02"},
    "QYYbO_hVfyM": {"tag": "PHYSICS_MODULE_01"},
    "zpDM2shFrsM": {"tag": "UI_ENGINE_TEST_V3.1"},
    "QctKXGoduGQ": {"tag": "UI_ENGINE_TEST_V3"},
    "ljAXi6Npk5E": {"tag": "LEGACY_UI_PROTO"},
    "uLq-d2tXOeo": {"tag": "CLI_KNOWLEDGE_DUMP"},
    "zGp0Pc83HNs": {"tag": "ENVIRONMENT_SETUP_V7"},
    "uSTruTEou5A": {"tag": "MINDMAP_LOGIC_PREVIEW"},
    "CZ84FCHMb4w": {"tag": "ORIGIN_UI_ARTIFACT"},
    "yB5EKDGgWTI": {"tag": "MOBILE_DEV_MANIFESTO"},
    "9pnF7TmSHnk": {"tag": "AI_GUIDE_V2"},
    "95UXjQl7ihc": {"tag": "SHORT_SIGNAL"},
    "KyuUzGyu7kM": {"tag": "ATMOSPHERE_SHORT"},
    "3oUpBjyCEn4": {"tag": "SOMATIC_ANOMALY_LOG"},
    "XQ27AC3Yhec": {"tag": "AVIAN_DATA_RECOVERY_02"},
    "uCR0tjpTtug": {"tag": "CORE_IDENTITY_FRAGMENT"},
    "E0ihQUmI_4Y": {"tag": "FRONTIER_SYNTHESIS"},
    "ZIZU60MAzjA": {"tag": "AVIAN_DATA_RECOVERY_01"},
    "3fSJVDMpjGk": {"tag": "RECORDED_LIVE_UPLINK"},
    "W8htct4Pz5o": {"tag": "DEV_SESSION_RECOVERY"},
    "2DhkOG7wubY": {"tag": "LIVE_SYNTHESIS_ACTIVE"},
    "-HcZgjYLxSQ": {"tag": "LIVE_STREAM_RECOVERY"}
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
        formatted = []
        for entry in transcript_list:
            timestamp = time.strftime('%M:%S', time.gmtime(entry['start']))
            formatted.append(f"[{timestamp}] {entry['text']}")
        return "\\n".join(formatted)
    except:
        return "NULL"

def get_comments(youtube, video_id):
    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )
        response = request.execute()
        feed = []
        for item in response.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            author_id = top.get("authorChannelId", {}).get("value", "")
            author_display = mask_user(author_id)
            comment_str = f"{author_display}>>{clean_js_string(top['textDisplay'])} ({top['publishedAt'][:10]})"
            if "replies" in item:
                for r_item in item["replies"]["comments"]:
                    s = r_item["snippet"]
                    r_author_id = s.get("authorChannelId", {}).get("value", "")
                    r_author_display = mask_user(r_author_id)
                    comment_str += f"\\n    └─ {r_author_display}: {clean_js_string(s['textDisplay'])} ({s['publishedAt'][:10]})"
            feed.append(comment_str)
        return "\\n---\\n".join(feed) if feed else "NO_COMMUNITY_SIGNALS"
    except:
        return "NULL"

def sync_archives():
    print(f"[SYSTEM] Connecting to YouTube Signal Spectrum...")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    try:
        ch_res = youtube.channels().list(part='snippet,statistics,contentDetails', id=CHANNEL_ID).execute()
        if not ch_res['items']:
            return
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
        id_list = list(video_ids)
        archives_data = []
        for i in range(0, len(id_list), 50):
            v_res = youtube.videos().list(part='snippet,contentDetails,statistics,status', id=','.join(id_list[i:i+50])).execute()
            for v in v_res['items']:
                title = v['snippet']['title']
                dur_obj = isodate.parse_duration(v['contentDetails']['duration'])
                unique_archives = {item['id']: item for item in archives_data}
                if v['id'] not in unique_archives:
                    v_type = "VIDEO"
                    if dur_obj.total_seconds() < 60: v_type = "SHORT"
                    if v['snippet'].get('liveBroadcastContent') != 'none': v_type = "LIVE"
                    archives_data.append({
                        'id': v['id'], 'title': title, 'date': v['snippet']['publishedAt'][:10],
                        'duration': str(dur_obj).split('.')[0].zfill(8), 'type': v_type,
                        'status': v['status']['privacyStatus'].upper(), 'views': v['statistics'].get('viewCount', '0'),
                        'likes': v['statistics'].get('likeCount', '0'), 'comm_count': v['statistics'].get('commentCount', '0'),
                        'desc': v['snippet']['description']
                    })
        raw_logs = []
        raw_logs.append(f'"1500_1|U||Y|CHANNEL|{clean_js_string(ch_name)}|ESTB_2018|{len(archives_data)}_NODES|{total_views}_PULSES|62.9h_UPTIME",')
        raw_logs.append(f'"1500_2|U||Y|NOTICE|Data stream fully anonymized (OpSec V7).\\nSignal detected from matrix node: {clean_js_string(ch_name)}.\\nBypassing the public algorithm.",')
        time_index = 1505
        for data in sorted(archives_data, key=lambda x: x['date'], reverse=True):
            print(f"[DISTILLING_ARCHIVE] {data['id']} (ANONYMIZING...)")
            tag = VIDEO_MAP.get(data['id'], {"tag": "SIGNAL_LOCKED"})['tag']
            transcript = get_transcript(data['id'])
            community_feed = get_comments(youtube, data['id'])
            log_entry = (
                f'"{time_index:04d}_1|U||Y|ENTRY|'
                f'{data["id"]}|{clean_js_string(data["title"])}|{data["date"]}|'
                f'{data["duration"]}|{data["type"]}|{data["status"]}|'
                f'{data["views"]}|{data["likes"]}|100|'
                f'{data["comm_count"]}|{tag}|{clean_js_string(data["desc"])}|'
                f'{clean_js_string(transcript)}|{clean_js_string(community_feed)}",'
            )
            raw_logs.append(log_entry)
            time_index += 5
            time.sleep(0.2)
        with open('extracted_archives_logs.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(raw_logs))
        print(f"\n[SUCCESS] Sync complete. {len(archives_data)} Archives Mapped.")
    except Exception as e:
        print(f"[ERROR] Sync Failed: {e}")

if __name__ == "__main__":
    sync_archives()
