import os
import telebot
import yt_dlp

TOKEN = "7953258525:AAH-Sj8V-1fX-3D8-72Q8J3g8J2L1"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(
      message,
      "Salom! Menga YouTube yoki Instagram (Reels/Post) havolasini yuboring,"
      " men uni sizga yuklab beraman. 📥",
  )


@bot.message_handler(func=lambda message: True)
def download_media(message):
  url = message.text.strip()

  if not (
      "youtube.com" in url
      or "youtu.be" in url
      or "instagram.com" in url
      or "instagr.am" in url
  ):
    bot.reply_to(
        message,
        "Iltimos, faqat YouTube yoki Instagram havolasini yuboring!",
    )
    return

  sent_msg = bot.reply_to(
      message, "⏳ Fayl yuklab olinmoqda, iltimos kuting..."
  )

  # yt-dlp sozlamalari
  ydl_opts = {
      'format': 'best',
      'outtmpl': 'downloaded_media.%(ext)s',
      'max_filesize': 50 * 1024 * 1024,  # Telegram limiti uchun 50MB
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    # Faylni Telegramga yuborish
    with open(filename, 'rb') as f:
      bot.send_video(message.chat.id, f)

    bot.delete_message(message.chat.id, sent_msg.message_id)

    # Yuklab olingandan keyin serverdan o'chirish
    if os.path.exists(filename):
      os.remove(filename)

  except Exception as e:
    bot.edit_message_text(
        f"❌ Xatolik yuz berdi:\n{str(e)}",
        message.chat.id,
        sent_msg.message_id,
    )


if __name__ == '__main__':
  bot.infinity_polling()
