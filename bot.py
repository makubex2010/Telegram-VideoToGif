import traceback
import os
import json
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils import executor
from moviepy.editor import VideoFileClip
from moviepy.video.fx.resize import resize
from aiogram.utils.exceptions import FileIsTooBig


token = os.getenv('BOT_TOKEN')
bot = Bot(token=token)
dp = Dispatcher(bot)


def convert_gif(unique_id):
    orig_clip = VideoFileClip(f"{unique_id}.mp4")
    w, h = orig_clip.size
    if h > w:
        clip = resize(orig_clip, height=640)
    else:
        clip = resize(orig_clip, width=640)
    clip.write_gif(f"{unique_id}.gif")
    clip.close()
    orig_clip.close()


@dp.message_handler(content_types=ContentType.VIDEO)
async def convert(message):
    file_id = message.video.file_id
    unique_id = message.video.file_unique_id
    try:
        file_obj = await bot.get_file(file_id)
        file_path = file_obj.file_path
        await bot.download_file(file_path, f"{unique_id}.mp4")
    except FileIsTooBig:
        await message.reply("文件太大，請嘗試壓縮它。")
        return
    except Exception as e:
        traceback.print_exc()
        await message.reply(f"下載過程中出現錯誤:\n`{e}`", parse_mode="MarkdownV2")
        return
    await message.reply("您的視頻正在轉換中，請稍候")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, convert_gif, unique_id)
    except Exception as e:
        traceback.print_exc()
        await message.reply(f"轉換過程中出現錯誤:\n`{e}`", parse_mode="MarkdownV2")
        return
    await message.reply_animation(animation=types.InputFile(f"{unique_id}.gif"))
    os.remove(f"{unique_id}.mp4")
    os.remove(f"{unique_id}.gif")


@dp.message_handler(content_types=ContentType.ANIMATION)
async def anim(message):
    await message.reply("這已經是動畫了！")


@dp.message_handler(commands=['start'])
async def start(message):
    await message.reply("你好！ 我可以將視頻轉換為 GIF：只需向我發送視頻即可！")

if __name__ == "__main__":
    executor.start_polling(dp)
