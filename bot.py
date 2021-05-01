import traceback
import os
import json
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils import executor
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import resize
from aiogram.utils.exceptions import FileIsTooBig


with open("config.json", encoding='UTF-8') as file:
    config = json.load(file)
token = config["token"]
bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(content_types=ContentType.VIDEO)
async def convert(message):
    file_id = message.video.file_id
    try:
        file_obj = await bot.get_file(file_id)
        file_path = file_obj.file_path
        await bot.download_file(file_path, "video.mp4")
    except FileIsTooBig:
        await message.reply("File is too big, try to compress it.")
        return
    except Exception as e:
        traceback.print_exc()
        await message.reply(f"There is an error during downloading:\n`{e}`", parse_mode="MarkdownV2")
        return
    await message.reply("Your video is converting, wait")
    try:
        orig_clip = VideoFileClip("video.mp4")
        clip = resize(orig_clip, 0.35)
        clip.write_gif("send.gif")
        clip.close()
        orig_clip.close()
    except Exception as e:
        traceback.print_exc()
        await message.reply(f"There is an error during converting:\n`{e}`", parse_mode="MarkdownV2")
        return
    await message.reply_animation(animation=types.InputFile("send.gif"))
    os.remove("video.mp4")
    os.remove("send.gif")


@dp.message_handler(content_types=ContentType.ANIMATION)
async def anim(message):
    await message.reply("This is already an animation!")

if __name__ == "__main__":
    executor.start_polling(dp)
