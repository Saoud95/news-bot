import anthropic
import requests
import os
import json
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ملف لحفظ الأخبار السابقة لتجنب التكرار
SENT_NEWS_FILE = "sent_myeloma_news.json"

def load_sent_news():
    """تحميل الأخبار المرسلة سابقاً"""
    if os.path.exists(SENT_NEWS_FILE):
        with open(SENT_NEWS_FILE, "r") as f:
            return json.load(f)
    return []

def save_sent_news(news_list):
    """حفظ الأخبار المرسلة"""
    # نحتفظ بآخر 50 خبر فقط
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(news_list[-50:], f, ensure_ascii=False)

def send_message(text):
    """إرسال رسالة إلى تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })
    if resp.status_code != 200:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_myeloma_news(sent_titles):
    """جلب أخبار المايلوما مع تجنب التكرار"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%Y-%m-%d")

    # تحويل الأخبار السابقة لنص
    sent_str = "\n".join(f"- {t}" for t in sent_titles[-20:]) if sent_titles else "لا يوجد"

    prompt = f"""You are a medical research editor specialized in Multiple Myeloma (سرطان المايلوما المتعددة).

Today is {today}.

IMPORTANT: These news items were already sent before. DO NOT repeat them:
{sent_str}

Search for NEW and DIFFERENT myeloma research from: pubmed.ncbi.nlm.nih.gov, asco.org, ash.org, fda.gov, myeloma.org, nejm.org, thelancet.com

Search terms: "multiple myeloma 2025", "CAR-T myeloma", "myeloma treatment breakthrough", "daratumumab", "multiple myeloma clinical trial"

Find 3-5 completely NEW items not in the list above.

FORMAT each news item EXACTLY like this:

NEWSITEM_START
🔬 *أخبار المايلوما | Myeloma Update*

📌 *[عنوان بالعربية | Title in English]*

🇸🇦 [تفاصيل بالعربية - 2-3 جمل]

🇬🇧 [Details in English - 2-3 sentences]

📎 المصدر | Source: [NIH/FDA/ASCO/ASH/NEJM/Lancet]
NEWSITEM_END

Rules:
- ONLY write inside NEWSITEM_START and NEWSITEM_END tags
- Include drug names (Daratumumab, Teclistamab, Carvykti, etc.)
- Each item must be genuinely different from the sent list above
- Write 3-5 items minimum
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    return "".join(b.text for b in message.content if b.type == "text")

def parse_and_send_myeloma(raw_text):
    """تقطيع وإرسال أخبار المايلوما"""
    today = datetime.now().strftime("%Y-%m-%d")
    header = f"🔬 *نشرة المايلوما اليومية*\n📅 {today}\n🔗 _NIH | FDA | ASCO | ASH | NEJM_\n➖➖➖➖➖➖➖➖➖➖"
    send_message(header)

    sent_news = load_sent_news()
    new_titles = []

    items = raw_text.split("NEWSITEM_START")
    count = 0
    for item in items:
        if "NEWSITEM_END" in item:
            news = item.split("NEWSITEM_END")[0].strip()
            if news:
                send_message(news)
                # استخراج العنوان للحفظ
                lines = news.split("\n")
                for line in lines:
                    if line.strip() and "📌" in line:
                        new_titles.append(line.strip())
                        break
                count += 1

    if count == 0:
        send_message(raw_text)

    # حفظ الأخبار الجديدة
    sent_news.extend(new_titles)
    save_sent_news(sent_news)

def main():
    print(f"🔬 Myeloma Bot - {datetime.now()}")
    try:
        sent_news = load_sent_news()
        raw = get_myeloma_news(sent_news)
        parse_and_send_myeloma(raw)
        print("✅ Done!")
    except Exception as e:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": f"⚠️ Myeloma Bot Error: {str(e)[:200]}"}
        )

if __name__ == "__main__":
    main()
