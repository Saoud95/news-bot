import anthropic
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def get_myeloma_news():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""You are a medical research editor specialized in Multiple Myeloma.
Today is {today}. Search for the latest developments in the last 24-48 hours from:
- pubmed.ncbi.nlm.nih.gov, asco.org, ash.org, fda.gov, myeloma.org
- Search: "multiple myeloma treatment breakthrough 2025"
- Search: "CAR-T myeloma 2025"
- Search: "multiple myeloma China Europe Russia clinical trial 2025"

Cover: new drugs, CAR-T therapy, clinical trials, immunotherapy, new approvals.

FORMAT:
🔬 *نشرة المايلوما اليومية | Daily Myeloma Update*
📅 {today}
➖➖➖➖➖➖➖➖➖➖
🇸🇦 *بالعربية:*
[أخبار بالعربية مع المصدر]
➖➖➖➖➖➖➖➖➖➖
🇬🇧 *In English:*
[Same news in English with source]
➖➖➖➖➖➖➖➖➖➖
🤖 _Automated Myeloma Research Bot_

Rules:
- Cite source after each item: [NIH] [FDA] [ASCO] [ASH] [EMA] [IMF]
- Include drug names (Daratumumab, CAR-T, etc.)
- Minimum 5 news items"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    return "".join(b.text for b in message.content if b.type == "text")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunks = []
    max_len = 4000
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = text.rfind('\n', 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip('\n')
    for i, chunk in enumerate(chunks):
        resp = requests.post(url, json={"chat_id": CHAT_ID, "text": chunk, "parse_mode": "Markdown"})
        if resp.status_code != 200:
            requests.post(url, json={"chat_id": CHAT_ID, "text": chunk})

def main():
    print(f"🔬 Myeloma Bot - {datetime.now()}")
    try:
        news = get_myeloma_news()
        if news:
            send_telegram_message(news)
            print("✅ Done!")
        else:
            send_telegram_message("⚠️ No myeloma news today.")
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": f"⚠️ Error: {str(e)[:200]}"})

if __name__ == "__main__":
    main()
