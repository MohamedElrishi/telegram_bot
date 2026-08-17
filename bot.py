import http.server
import os
import socketserver
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# سيرفر وهمي لتشغيل الخدمة مجاناً على Render
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
    bot.reply_to(
        message, "أهلاً بك! أرسل لي أي رابط فيديو (يوتيوب، تيك توك، إلخ) وسأقوم بعرض خيارات الجودة المتاحة لتحميله."
    )

@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        bot.reply_to(message, "يرجى إرسال رابط صحيح.")
        return

    user_urls[message.chat.id] = url

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎬 360p", callback_data="q_360"),
        InlineKeyboardButton("🎬 480p", callback_data="q_480"),
        InlineKeyboardButton("🎬 720p", callback_data="q_720")
    )

    bot.reply_to(message, "اختر الجودة المطلوبة للتحميل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("q_"))
def process_download(call):
    chat_id = call.message.chat.id
    quality = call.data.split("_")[1]
    url = user_urls.get(chat_id)

    if not url:
        bot.edit_message_text(
            "❌ انتهت صلاحية الطلب، يرجى إرسال الرابط من جديد.",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        return

    bot.edit_message_text(
        "⏳ جاري التحميل، يرجى الانتظار...",
        chat_id=chat_id,
        message_id=call.message.message_id
    )

    try:
        # تنظيف الملفات السابقة
        for f in os.listdir("."):
            if f.startswith("video."):
                try:
                    os.remove(f)
                except:
                    pass

        format_str = f"best[height<={quality}][ext=mp4]/best[height<={quality}]/best"

        # إعدادات لتجاوز الحظر والتعرف كـ هاتف
        ydl_opts = {
            "format": format_str,
            "outtmpl": "video.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["ios", "android", "mweb"]
                }
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_file = None
        for f in os.listdir("."):
            if f.startswith("video."):
                downloaded_file = f
                break

        if downloaded_file and os.path.exists(downloaded_file):
            bot.edit_message_text(
                "📤 جاري رفع الفيديو إلى تيليجرام...",
                chat_id=chat_id,
                message_id=call.message.message_id
            )
            with open(downloaded_file, "rb") as video:
                bot.send_video(chat_id, video)
            os.remove(downloaded_file)
        else:
            bot.edit_message_text(
                "❌ تعذر تحميل الفيديو.",
                chat_id=chat_id,
                message_id=call.message.message_id
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ حدث خطأ أثناء التحميل: {str(e)}",
            chat_id=chat_id,
            message_id=call.message.message_id
        )

bot.polling()
