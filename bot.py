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


with open("config.json", encoding='UTF-8') as file:
    config = json.load(file)
token = config["token"]
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
    print(message.video)
    try:
        file_obj = await bot.get_file(file_id)
        file_path = file_obj.file_path
        await bot.download_file(file_path, f"{unique_id}.mp4")
    except FileIsTooBig:
        await message.reply("File is too big, try to compress it.")
        return
    except Exception as e:
        traceback.print_exc()
        await message.reply(f"There is an error during downloading:\n`{e}`", parse_mode="MarkdownV2")
        return
    await message.reply("Your video is converting, wait")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, convert_gif, unique_id)
    except Exception as e:
        traceback.print_exc()
        await message.reply(f"There is an error during converting:\n`{e}`", parse_mode="MarkdownV2")
        return
    await message.reply_animation(animation=types.InputFile(f"{unique_id}.gif"))
    os.remove(f"{unique_id}.mp4")
    os.remove(f"{unique_id}.gif")


@dp.message_handler(content_types=ContentType.ANIMATION)
async def anim(message):
    await message.reply("This is already an animation!")

if __name__ == "__main__":
    executor.start_polling(dp)
