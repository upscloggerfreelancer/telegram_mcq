# NOTE:
# Paste the first part of your existing script (imports, image generation functions,
# Gemini client setup, etc.) above this section unchanged.
import random
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import re
import asyncio
from google import genai
from telegram import Bot, Poll
import time

from datetime import date

# ====== Google GenAI client ======

api_key - os.environ["GEMINI_API"] #srijayadhikari@gmail.com API key

client = genai.Client(api_key=api_key)  #srijayadhikari@gmail.com API KEY

BOT_TOKEN = os.environ["BOT_TOKEN"]






BG         = (18, 18, 20)
CARD       = (26, 26, 30)
ACCENT     = (212, 175, 95)
ACCENT2    = (180, 145, 70)
TEXT_BODY  = (210, 205, 192)
TEXT_MUTED = (130, 125, 115)
W, H       = 1080, 1080

POPPINS_BOLD = "fonts/Poppins-Bold.ttf"
POPPINS_MED  = "fonts/Poppins-Medium.ttf"
LORA         = "fonts/Lora-VariableFont_wght.ttf"

HIGHLIGHT_COLORS = [
    (212, 175, 95),
    (120, 200, 170),
    (220, 120, 100),
    (150, 180, 230),
    (200, 160, 220),
]

def _wrap(text, fnt, draw, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def generate_upsc_graphic(text: str, save_dir: str = ".") -> str:
    os.makedirs(save_dir, exist_ok=True)
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    pad  = 72

    draw.rounded_rectangle([pad, pad, W-pad, H-pad], radius=20, fill=CARD)
    lx, ly = pad + 64, pad + 72

    # — Header
    label_font = ImageFont.truetype(POPPINS_BOLD, 42)
    draw.text((lx, ly), "UPSC LoG", font=label_font, fill=ACCENT)
    rule_y = ly + 62
    draw.rectangle([lx, rule_y, W-pad-64, rule_y+2], fill=ACCENT2)
    tag_font = ImageFont.truetype(POPPINS_MED, 20)
    draw.text((lx, rule_y+20), "Daily Fact", font=tag_font, fill=TEXT_MUTED)

    # — Body
    body_font = ImageFont.truetype(LORA, 34)
    try:
        body_font.set_variation_by_name("Bold")
    except Exception:
        pass

    max_w    = W - (pad + 64) * 2
    lines    = _wrap(text, body_font, draw, max_w)
    line_h   = 56
    total_h  = len(lines) * line_h
    text_top = H // 2 - total_h // 2 + 30

    for i, line in enumerate(lines):
        words    = line.split()
        hi_idx   = random.randint(0, len(words)-1)
        hi_color = random.choice(HIGHLIGHT_COLORS)
        tx, ty   = lx, text_top + i * line_h
        for j, word in enumerate(words):
            color = hi_color if j == hi_idx else TEXT_BODY
            draw.text((tx, ty), word, font=body_font, fill=color)
            tx += draw.textbbox((0, 0), word + " ", font=body_font)[2]

    # — Footer
    foot_rule_y = H - pad - 112
    draw.rectangle([lx, foot_rule_y, W-pad-64, foot_rule_y+2], fill=ACCENT2)
    foot_font = ImageFont.truetype(POPPINS_MED, 22)
    draw.text((lx, foot_rule_y+22), "Prepare  ·  Practice  ·  Prevail",
              font=foot_font, fill=TEXT_MUTED)
    sq = 8
    draw.rectangle([W-pad-64-sq, foot_rule_y+28, W-pad-64, foot_rule_y+28+sq], fill=ACCENT)

    # — Save
    filename = f"upsc_{abs(hash(text)) % 10**8}.png"
    out_path = os.path.abspath(os.path.join(save_dir, filename))
    img.save(out_path, "PNG")
    return out_path




# ====== Read topics from file ======
file_path = "topics.txt"
with open(file_path, "r", encoding="utf-8") as f:
    topics = [t.strip() for t in f.readlines() if t.strip()]

topic = random.choice(topics)

MAX_RETRIES = 5
RETRY_DELAY = 30

prompt = f"""
Generate under 40 words, an interesting and informative catchy UPSC/SSC-themed fact on the topic "{topic}".
Don't include any unnecessary characters in the response, just the fact.
"""

text = None

for attempt in range(1, MAX_RETRIES + 1):
    try:
        print(f"Generating fact... ({attempt}/{MAX_RETRIES})")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text:
            break
    except Exception as e:
        print(e)

    if attempt < MAX_RETRIES:
        print(f"Retrying in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)

if text is None:
    raise Exception("Gemini failed after all retries.")

print(text)

image_genr = generate_upsc_graphic(text=text)

CHAT_IDS = ["@upsclog" , "@upscgroupch" , "@upsc_mains_answer_writing_groupp"]

TARGET_DATE = date(2027, 5, 24)
days_left = (TARGET_DATE - date.today()).days

morning_message = (
    f"🌻 Good Morning Officers!\n\n"
    f"👉 Only {days_left} days left for UPSC Prelims 2027.\n\n"
    "Let's make today count. 💪"
)

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        r = requests.post(url, data={
            "chat_id": chat_id,
            "text": message
        })
        r.raise_for_status()

def send_photo(image_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    for chat_id in CHAT_IDS:
        with open(image_path, "rb") as img:
            r = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "caption": f"DAILY LoG 📝\n\n👉 {text}"
                },
                files={"photo": img}
            )
            r.raise_for_status()

send_message(morning_message)
time.sleep(2)
send_photo(image_genr)

print("Done.")
