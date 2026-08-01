import os
import telebot
from telebot import types
import yt_dlp

TOKEN = "8754840620:AAEoURGSEuxH2yG6GNZSAVWx4drkzaDrGAc"
bot = telebot.TeleBot(TOKEN)

# معرف قناتك للاشتراك الإجباري
CHANNEL_USERNAME = "@nooraliman1"

# دالة للتحقق مما إذا كان المستخدم مشتركاً في القناة أم لا
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking subscription: {e}")
    return False

# رسالة طلب الاشتراك الإجباري مع الأزرار
def send_subscription_required(message):
    markup = types.InlineKeyboardMarkup()
    channel_btn = types.InlineKeyboardButton("📢 اشترك في القناة هنا", url="https://t.me/nooraliman1")
    check_btn = types.InlineKeyboardButton("🔄 تحقق من الاشتراك", callback_data="check_sub")
    markup.add(channel_btn)
    markup.add(check_btn)
    
    bot.send_message(
        message.chat.id,
        "⚠️ **عذراً، عليك الاشترا⁠ك في قناة البوت أولاً لتتمكن من استخدامه!**\n\n"
        "القناة: https://t.me/nooraliman1\n\n"
        "بعد الاشتراك، اضغط على زر (تحقق من الاشتراك) بالأسفل 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        send_subscription_required(message)
        return

    bot.reply_to(
        message,
        "👋 مرحبًا بك في Media Downloader Bot\n\n"
        "يدعم التحميل من:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Facebook\n"
        "• X (Twitter)\n"
        "• Snapchat\n"
        "• SoundCloud\n\n"
        "📥 فقط أرسل رابط الفيديو أو المنشور، وسيتم تنزيله تلقائيًا بأفضل جودة متاحة."
    )

# التعامل مع ضغطة زر التحقق من الاشتراك
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def verify_subscription(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ شكراً لاشتراكك! يمكنك الآن استخدام البوت.")
        bot.edit_message_text(
            "🎉 تم التحقق من اشتراكك بنجاح!\n\n"
            "📥 أرسل لي الآن رابط أي فيديو وسأقوم بتحميله لك.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ لم تقم بالاشتراك في القناة بعد!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def download_media(message):
    if not check_subscription(message.from_user.id):
        send_subscription_required(message)
        return

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
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                # النص الإعلاني المحدث الذي يظهر تحت كل فيديو مرفق
                caption_text = (
                    "📥 **تم التحميل بنجاح!**\n\n"
                    "✨ يمكنك تحميل الفيديوهات من على منصات التواصل الإجتماعي عبر بوت:\n"
                    "👉 @sm_downloader01_bot"
                )
                bot.send_video(message.chat.id, video, caption=caption_text, parse_mode="Markdown")
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
