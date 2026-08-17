import http.server
import os
import socketserver
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# سيرفر وهمي لتشغيل الخدمة على Render
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# قاموس مؤقت لحفظ رابط كل مستخدم
user_urls = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message, "أهلاً بك! أرسل لي أي رابط فيديو وسأقوم بعرض خيارات الجودة المتاحة لتحميله."
    )

@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        bot.reply_to(message, "يرجى إرسال رابط صحيح.")
        return

    # حفظ الرابط الخاص بالمرسل
    user_urls[message.chat.id] = url

    # إنشاء أزرار الجودات
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
    quality = call.data.split("_")[1] # 360, 480, or 720
    url = user_urls.get(chat_id)

    if not url:
        bot.edit_message_text(
            "❌ انتهت صلاحية الطلب، يرجى إرسال الرابط من جديد.",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        return

    bot.edit_message_text(
        f"⏳ جاري تحميل الفيديو بجودة {quality}p...",
        chat_id=chat_id,
        message_id=call.message.message_id
    )

    try:
        # تنظيف أي ملفات سابقة
        for f in os.listdir("."):
            if f.startswith("video."):
                os.remove(f)

        # صيغة طلب الجودة المحددة
        format_str = f"best[height<={quality}][ext=mp4]/best[height<={quality}]"

        ydl_opts = {
            "format": format_str,
            "outtmpl": "video.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
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
                f"📤 جاري رفع الفيديو (جودة {quality}p) إلى تيليجرام...",
                chat_id=chat_id,
                message_id=call.message.message_id
            )
            with open(downloaded_file, "rb") as video:
                bot.send_video(chat_id, video)
            os.remove(downloaded_file)
        else:
            bot.edit_message_text(
                "❌ تعذر تحميل الفيديو بهذه الجودة.",
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
