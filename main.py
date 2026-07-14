import json
import random
from pathlib import Path
import time
import requests
import os
# =====================================================
# CONFIG
# =====================================================



BOT_TOKEN = os.environ["BOT_TOKEN"]

CHANNELS = [
    "@upsc_daily_pyq"
]

QUESTIONS_FILE = "questions.txt"

POLLS_PER_RUN = 300

# =====================================================


INTRO = """📚🔥 <b>Daily NCERT & GS MCQ Quiz</b> 🔥📚
🎯 Welcome to today's practice session!
🏆 Perfect for aspirants preparing for <b>UPSC CSE, SSC, CDS, CAPF, State PSCs, Railways, Banking</b> and other competitive examinations.

🚀 Best of Luck!!
👇 Let's Begin 👇
"""


OUTRO = """#upsc #ssc #prelims #mains #upscmains UPSC SSC CDS CGL daily mcq quizzes and puzzles.</b>
admin - @upsctestse </b>#uspc #ssc #cds upsc_Daily_mcq_practise_bot get all free quizzes and test series
"""


def send_message(channel, text):
    """Send a text message."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": channel,
        "text": text,
        "parse_mode": "HTML"
    }

    r = requests.post(url, data=payload)

    if r.ok:
        print(f"[{channel}] Message sent.")
        return True
    else:
        print(f"[{channel}] Message failed.")
        print(r.text)
        return False


def send_poll(channel, question):
    """Send one quiz poll."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"

    payload = {
        "chat_id": channel,
        "question": question["question"],
        "options": json.dumps(question["options"]),
        "type": "quiz",
        "correct_option_id": question["answer"],
        "is_anonymous": True
    }

    r = requests.post(url, data=payload)

    if r.ok:
        print(f"[{channel}] Posted: {question['question']}")
        return True
    else:
        print(f"[{channel}] Failed:")
        print(r.text)
        return False


def load_questions():
    file = Path(QUESTIONS_FILE)

    if not file.exists():
        raise FileNotFoundError(f"{QUESTIONS_FILE} not found.")

    with file.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():

    lines = load_questions()

    if not lines:
        print("No questions found.")
        return

    # Randomly select questions
    count = min(POLLS_PER_RUN, len(lines))
    current_questions = random.sample(lines, count)

    # Post to every channel
    for channel in CHANNELS:

        print(f"\nPosting to {channel}")

        send_message(channel, INTRO)
        count = 0
        for line in current_questions:
            try:
                question = json.loads(line)
                send_poll(channel, question)
            except Exception as e:
                print("Invalid JSON:")
                print(e)
            if count%2==0:
                send_message(channel, OUTRO)
            count+=1
            time.sleep(120)
    print("\n====================================")
    print(f"Posted {count} random questions.")
    print("Done!")
    print("====================================")


if __name__ == "__main__":
    main()
