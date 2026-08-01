import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# التوكن الخاص بك
TOKEN = "8754840620:AAEoURGSEuxH2yG6GNZSAVWx4drkzaDrGAc"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "أهلاً بك! 🤖\n"
        "أرسل لي رابط أي فيديو من يوتيوب، إنستغرام، تيك توك، أو تويتر وسأقوم بتحميله لك."
    )

@dp.message()
async def download_media(message: types.Message):
    url = message.text.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        await message.answer("الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    processing_msg = await message.answer("⏳ جاري المعالجة والتحميل، يرجى الانتظار...")
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
            await message.answer_video(types.FSInputFile(file_path), caption="تم التحميل بواسطة البوت ✅")
            os.remove(file_path)
        else:
            await message.answer("❌ عذراً، لم أتمكن من العثور على الملف وتحميله.")
    except Exception as e:
        await message.answer("❌ حدث خطأ أثناء التحميل. تأكد من أن الرابط صالح وعام.")
    finally:
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
