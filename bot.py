import os
import sys
import subprocess
import http.server
import socketserver
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# تحديث المكتبة
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], check=False)
except: pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
user_urls = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "أرسل رابط الفيديو (يوتيوب، تيك توك، إلخ).")

@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text.strip()
    if not url.startswith("http"): return
    user_urls[message.chat.id] = url
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("جودة متوسطة (480p)", callback_data="q_480"))
    bot.reply_to(message, "اختر الجودة للتحميل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("q_"))
def process_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)
    bot.edit_message_text("⏳ جاري المعالجة (محاولة تجاوز الحظر)...", chat_id, call.message.message_id)

    try:
        ydl_opts = {
            'format': 'best[height<=480][ext=mp4]/best',
            'outtmpl': 'video.mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'nocheckcertificate': True,
            # محاكاة متصفح Chrome حديث
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {'player_client': ['web']},
                'tiktok': {'referer': 'https://www.tiktok.com/'}
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists("video.mp4"):
            bot.edit_message_text("📤 جاري الرفع...", chat_id, call.message.message_id)
            with open("video.mp4", "rb") as video:
                bot.send_video(chat_id, video)
            os.remove("video.mp4")
        else:
            raise Exception("فشل التحميل.")

    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}\nملاحظة: السيرفر محظور من المنصة.", chat_id, call.message.message_id)

bot.polling()
