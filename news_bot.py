import anthropic
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def send_message(text):
    """إرسال رسالة واحدة إلى تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })
    if resp.status_code != 200:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_news_from_claude(mode):
    """
    mode = 'politics' → أخبار سياسية
    mode = 'football' → أخبار كرة القدم
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%Y-%m-%d")

    if mode == "politics":
        prompt = f"""أنت محرر أخبار محترف. اليوم هو {today}.

ابحث عن أهم أخبار الـ 24 ساعة الماضية من: reuters.com و theguardian.com و skynews.com
