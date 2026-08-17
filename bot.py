import http.server
import os
import socketserver
import threading
import telebot
import yt_dlp


# سيرفر وهمي لتشغيل الخدمة على الخطط المجانية
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()


threading.Thread(target=run_dummy_server, daemon=True).start()

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message, "أهلاً بك! أرسل لي أي رابط فيديو وسأقوم بتحميله لك."
    )


@bot.message_handler(func=lambda message: True)
def download_and_send(message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        bot.reply_to(message, "يرجى إرسال رابط صحيح.")
        return

    status_msg = bot.reply_to(message, "⏳ جاري التحميل على السيرفر الخارجي...")

    try:
        # مسح أي ملف قديم
        for f in os.listdir("."):
            if f.startswith("video."):
                os.remove(f)

        # خيارات yt-dlp للتحميل المباشر داخل بايثون
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "video.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # البحث عن الملف المحمل
        downloaded_file = None
        for f in os.listdir("."):
            if f.startswith("video."):
                downloaded_file = f
                break

        if downloaded_file and os.path.exists(downloaded_file):
            bot.edit_message_text(
                "📤 جاري رفع الفيديو لتيليجرام...",
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
            )
            with open(downloaded_file, "rb") as video:
                bot.send_video(message.chat.id, video)
            os.remove(downloaded_file)
        else:
            bot.edit_message_text(
                "❌ تعذر تحميل الفيديو، حاول مع رابط آخر.",
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ حدث خطأ أثناء التحميل: {str(e)}",
            chat_id=status_msg.chat.id,
            message_id=status_msg.message_id,
        )


bot.polling()
