import anthropic
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def get_news_from_claude():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""أنت محرر أخبار محترف متخصص في تلخيص الأخبار العالمية والرياضية.
اليوم هو {today}.

مهمتك: ابحث في المصادر المحددة أدناه عن أهم أخبار الـ 24 ساعة الماضية، ثم لخّصها بالعربية الفصحى الواضحة.

🔴 المحور الأول: حرب غزة وإسرائيل
ابحث في: theguardian.com و reuters.com و skynews.com
اذكر 3 أخبار مهمة مع المصدر.

🔴 المحور الثاني: لبنان وإسرائيل
ابحث في: theguardian.com و reuters.com و skynews.com
اذكر 2-3 أخبار مهمة مع المصدر.

🌐 المحور الثالث: إيران وأمريكا وإسرائيل
ابحث في: theguardian.com و reuters.com و skynews.com
اذكر 2-3 أخبار مهمة مع المصدر.

💰 المحور الرابع: أخبار الخليج الاقتصادية والسياسية
ابحث في: reuters.com و theguardian.com
اذكر 2-3 أخبار مهمة مع المصدر.

🇨🇳 المحور الخامس: أخبار الصين
ابحث في: reuters.com و theguardian.com و skynews.com
اذكر 2-3 أخبار مع المصدر.

🛢️ المحور السادس: النفط والذهب
ابحث في: reuters.com
اذكر السعر الحالي وأهم التحركات.

⚽ المحور السابع: كرة القدم الأوروبية
ابحث في: fifa.com/ar و theguardian.com/football
اذكر أبرز النتائج والأخبار.

🏆 المحور الثامن: كرة القدم الخليجية والآسيوية
ابحث في: the-afc.com/ar و fifa.com/ar
اذكر أبرز أخبار الاتحاد الآسيوي والدوريات الخليجية.

قواعد:
- اكتب كل شيء بالعربية فقط
- اذكر المصدر بعد كل خبر: [رويترز] أو [الغارديان] أو [سكاي نيوز] أو [فيفا] أو [الاتحاد الآسيوي]
- لا تخترع أخباراً

ابدأ الرسالة بـ:
📰 *نشرة أخبار اليوم*
📅 {today}
🔗 _المصادر: الغارديان | رويترز | سكاي نيوز | فيفا | الاتحاد الآسيوي_
➖➖➖➖➖➖➖➖➖➖
وانهِ بـ:
➖➖➖➖➖➖➖➖➖➖
🤖 _تم إعداد هذه النشرة تلقائياً_"""

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
    print(f"🚀 بدء البوت - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    try:
        news = get_news_from_claude()
        if news:
            send_telegram_message(news)
            print("✅ تم!")
        else:
            send_telegram_message("⚠️ لم أتمكن من جلب الأخبار اليوم.")
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": f"⚠️ خطأ: {str(e)[:200]}"})

if __name__ == "__main__":
    main()
