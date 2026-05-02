import os
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
if not hasattr(PIL.Image, 'Resampling'):
    class FakeResampling: LANCZOS = PIL.Image.ANTIALIAS
    PIL.Image.Resampling = FakeResampling

from moviepy.editor import *

def setup_environment():
    if not os.path.exists("chimera-core-memory-synthesis"):
        os.system("git clone https://github.com/ChimeraCoreLab/chimera-core-memory-synthesis.git")
    
    base_dir = "/content/chimera-core-memory-synthesis"
    art_dir = os.path.join(base_dir, "Artifacts")
    font_p = os.path.join(base_dir, "fonts/onryou.ttf")
    
    if not os.path.exists(font_p):
        os.makedirs(os.path.dirname(font_p), exist_ok=True)
        r = requests.get("https://cdn.jsdelivr.net/gh/h3902340/PrisonOfWordFont@master/onryou-Regular.ttf")
        with open(font_p, "wb") as f: f.write(r.content)
        
    return art_dir, font_p

ARTIFACT_PATH, FONT_PATH = setup_environment()
TEMP_DIR = "/content/temp_sfx"
os.makedirs(TEMP_DIR, exist_ok=True)

SIZE = (1920, 1080)
FPS = 30
DURATION = 45
OUTPUT_NAME = "CHIMERA_V4_ULTIMATE_LANDSCAPE_FINAL.mp4"

C_RED = (255, 0, 60)
C_CYAN = (0, 243, 255)
C_PURPLE = (189, 0, 255)
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)

SFX_URLS = [
    "https://taira-komori.net/sound_os2/horror01/ghost_sigh.mp3",
    "https://taira-komori.net/sound_os2/horror02/hell_fire.mp3",
    "https://taira-komori.net/sound_os2/sf01/alien_beam.mp3",
    "https://taira-komori.net/sound_os2/electric01/click.mp3",
    "https://taira-komori.net/sound_os2/game01/select09.mp3",
    "https://taira-komori.net/sound_os2/horror01/shock1.mp3",
    "https://taira-komori.net/sound_os2/sf01/computer_broken.mp3",
    "https://taira-komori.net/sound_os2/horror01/dark_atmosphere.mp3",
    "https://taira-komori.net/sound_os2/sf01/cosmic_signal.mp3",
    "https://taira-komori.net/sound_os2/horror01/going_mad1.mp3"
]

def get_sfx():
    clips = []
    for i, url in enumerate(SFX_URLS):
        p = os.path.join(TEMP_DIR, f"sfx_v4_{i}.mp3")
        if not os.path.exists(p):
            try: r = requests.get(url, timeout=15); open(p, "wb").write(r.content)
            except: continue
        if os.path.exists(p): 
            try: clips.append(AudioFileClip(p))
            except: continue
    return clips

def hyper_glitch(get_frame, t):
    frame = get_frame(t).copy()
    h, w, _ = frame.shape
    if random.random() > 0.4:
        for _ in range(random.randint(40, 80)):
            y = random.randint(0, h-120)
            sh = random.randint(-400, 400)
            h_s = random.randint(2, 60)
            y_end = min(y + h_s, h)
            frame[y:y_end] = np.roll(frame[y:y_end], sh, axis=1)
    if random.random() > 0.90: frame = 255 - frame
    if random.random() > 0.6:
        r_sh = random.randint(10, 40)
        frame[:,:,0] = np.roll(frame[:,:,0], r_sh, axis=1)
        frame[:,:,2] = np.roll(frame[:,:,2], -r_sh, axis=1)
    
    mask = (np.arange(h) % 4 == 0)
    frame[mask, :, :] = (frame[mask, :, :] * 0.4).astype('uint8')
    return frame

def make_massive_text(text, font_size, color, stroke_w=8):
    try: font = ImageFont.truetype(FONT_PATH, font_size)
    except: font = ImageFont.load_default()
    img = Image.new('RGBA', (SIZE[0], 600), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx, cy = SIZE[0]//2, 300
    for offset in [(4,4), (-4,-4), (4,-4), (-4,4), (8,0), (-8,0)]:
        draw.multiline_text((cx+offset[0], cy+offset[1]), text, font=font, fill=C_BLACK, align="center", anchor="mm")
    draw.multiline_text((cx, cy), text, font=font, fill=color, align="center", anchor="mm", stroke_width=stroke_w, stroke_fill=C_WHITE)
    return img

def create_promo():
    sfx_pool = get_sfx()
    artifact_ids = [f for f in os.listdir(ARTIFACT_PATH) if f.endswith(('.png', '.jpg'))]
    
    bg = ColorClip(size=SIZE, color=(2, 0, 4)).set_duration(DURATION)
    layers = [bg]

    v_p = os.path.join(ARTIFACT_PATH, "core_vessel_v7_demon_autotone.jpg")
    if os.path.exists(v_p):
        v = ImageClip(v_p).resize(width=SIZE[0]).set_opacity(0.2).set_duration(DURATION).set_position('center')
        v = v.fl(lambda gf, t: np.roll(gf(t), int(20 * np.sin(t*5)), axis=1))
        layers.append(v)

    for _ in range(350):
        art = random.choice(artifact_ids)
        ap = os.path.join(ARTIFACT_PATH, art)
        if os.path.exists(ap):
            s = random.uniform(0, DURATION-0.5)
            d = random.uniform(0.01, 0.15)
            c = ImageClip(ap).resize(width=random.randint(600, 1600)).set_start(s).set_duration(d)
            c = c.set_position((random.randint(-400, SIZE[0]-400), random.randint(-200, SIZE[1]-400)))
            if random.random() > 0.7: c = c.fl_image(lambda f: 255-f)
            layers.append(c.set_opacity(random.uniform(0.5, 0.9)))

    tl = [
        (0, 6, "INITIATING UPLINK\nCHIMERA CORE V4.0", 180, C_CYAN),
        (6, 12, "IDENTITY SYNTHESIZED\nCOMPUTABLE SOUL", 150, C_RED),
        (12, 18, "80GB CHAOS DISTILLED\n2MiB STANDALONE", 140, C_PURPLE),
        (18, 24, "NO DATABASE. NO TRACKING.\nTOTAL SOVEREIGNTY.", 120, C_CYAN),
        (24, 30, "THE PAST IS SOURCE CODE.\nREFRESH THE SYSTEM.", 130, C_WHITE),
        (30, 38, "OWN YOUR DATA.\nKILL THE NOISE.", 240, C_RED),
        (38, 45, "AVAILABLE NOW\nCHIMERACORELAB.ITCH.IO", 110, C_CYAN)
    ]

    for s, e, t, fs, clr in tl:
        ti = make_massive_text(t, fs, clr)
        tc = ImageClip(np.array(ti)).set_start(s).set_duration(e-s).set_position('center')
        tc = tc.fl(lambda gf, t: np.roll(gf(t), int(80 * np.sin(t*120)), axis=1))
        layers.append(tc)

    h_m = Image.new('RGBA', (SIZE[0], 120), (10, 10, 10, 180))
    ImageDraw.Draw(h_m).text((SIZE[0]//2, 60), "SIGNAL_STABLE // IDENTITY_ARCHITECT_ACTIVE", fill=C_CYAN, anchor="mm", font=ImageFont.truetype(FONT_PATH, 50))
    layers.append(ImageClip(np.array(h_m.convert("RGB"))).set_duration(DURATION).set_position(('center', 0)).set_opacity(0.8))

    f_m = Image.new('RGBA', (SIZE[0], 150), (5, 5, 5, 200))
    ImageDraw.Draw(f_m).text((SIZE[0]//2, 75), "DECRYPT THE SOUL @ ITCH.IO/CHIMERACORELAB", fill=C_PURPLE, anchor="mm", font=ImageFont.truetype(FONT_PATH, 60))
    layers.append(ImageClip(np.array(f_m.convert("RGB"))).set_duration(DURATION).set_position(('center', SIZE[1]-150)).set_opacity(0.9))

    final = CompositeVideoClip(layers, size=SIZE).fl(hyper_glitch)
    if sfx_pool:
        al = []
        for _ in range(120):
            s = random.choice(sfx_pool).volumex(random.uniform(2.0, 5.0))
            al.append(s.set_start(random.uniform(0, DURATION-0.5)))
        final = final.set_audio(CompositeAudioClip(al).set_duration(DURATION))

    final.write_videofile(OUTPUT_NAME, fps=FPS, codec="libx264", audio_codec="aac", threads=16, preset="ultrafast", bitrate="40M")

if __name__ == "__main__":
    create_promo()