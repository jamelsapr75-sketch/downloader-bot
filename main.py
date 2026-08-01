import os
import telebot
import yt_dlp

TOKEN = "8754840620:AAEoURGSEuxH2yG6GNZSAVWx4drkzaDrGAc"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "أهلاً بك! 🤖\nأرسل لي رابط أي فيديو من يوتيوب، إنستغرام، أو تيك توك وسأقوم بتحميله لك."
    )

@bot.message_handler(func=lambda message: True)
def download_media(message):
    url = message.text.strip()
    
    if not url.startswith("http://") and not url.startswith("https://"):
        bot.reply_to(message, "الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    processing_msg = bot.reply_to(message, "⏳ جاري المعالجة والتحميل، يرجى الانتظار...")
    os.makedirs("downloads", exist_ok=True)
    
    ydl_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'format': 'best',
        'max_filesize': 50 * 1024 * 1024,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="تم التحميل بواسطة البوت ✅")
            os.remove(file_path)
        else:
            bot.reply_to(message, "❌ عذراً، لم أتمكن من العثور على الملف وتحميله.")
            
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ أثناء التحميل. تأكد من أن الرابط صالح وعام.")
        
    finally:
        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass

bot.infinity_polling()
