import http.server
import os
import socketserver
import subprocess
import threading
import telebot


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
                                                                                if os.path.exists("video.mp4"):
                                                                                            os.remove("video.mp4")

                                                                                                    cmd = f'yt-dlp -o "video.%(ext)s" -f "best[ext=mp4]/best" "{url}"'
                                                                                                            subprocess.run(cmd, shell=True, check=True)

                                                                                                                    if os.path.exists("video.mp4"):
                                                                                                                                bot.edit_message_text(
                                                                                                                                                    "📤 جاري رفع الفيديو لتيليجرام...",
                                                                                                                                                                    chat_id=status_msg.chat.id,
                                                                                                                                                                                    message_id=status_msg.message_id,
                                                                                                                                                                                                )
                                                                                                                                                                                                            with open("video.mp4", "rb") as video:
                                                                                                                                                                                                                            bot.send_video(message.chat.id, video)
                                                                                                                                                                                                                                        os.remove("video.mp4")
                                                                                                                                                                                                                                                else:
                                                                                                                                                                                                                                                            bot.edit_message_text(
                                                                                                                                                                                                                                                                                "❌ تعذر تحميل الفيديو.",
                                                                                                                                                                                                                                                                                                chat_id=status_msg.chat.id,
                                                                                                                                                                                                                                                                                                                message_id=status_msg.message_id,
                                                                                                                                                                                                                                                                                                                            )

                                                                                                                                                                                                                                                                                                                                except Exception as e:
                                                                                                                                                                                                                                                                                                                                        bot.edit_message_text(
                                                                                                                                                                                                                                                                                                                                                        f"❌ حدث خطأ: {str(e)}",
                                                                                                                                                                                                                                                                                                                                                                    chat_id=status_msg.chat.id,
                                                                                                                                                                                                                                                                                                                                                                                message_id=status_msg.message_id,
                                                                                                                                                                                                                                                                                                                                                                                        )


                                                                                                                                                                                                                                                                                                                                                                                        bot.polling()"
                                                                                                                                                                                                                                                                                                                                        )
                                                                                                                                                                                                                                                            )
                                                                                                                                )'
                        )
