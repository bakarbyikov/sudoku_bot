from io import BytesIO
import logging
import os

from dotenv import load_dotenv
from telegram import Update
import telegram
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters

from cather import process_image
from my_logger import InterceptHandler
from exceptions import CantRecogniseImage
from solver import Solver

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

async def get_photo(update: Update, context: CallbackContext):
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]

    obj = await file.get_file()
    image = BytesIO(await obj.download_as_bytearray())

    context_bot: telegram.Bot = context.bot

    progress_message = await context_bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"Распознаю фото...")

    try:
        table = process_image(image.getvalue())
        await context_bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=progress_message.message_id,
            text=f"Я распознал табличку\n{table}",
            )
    except CantRecogniseImage:
        await context_bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=progress_message.message_id,
            text="Не удалось распознать",
            )
        raise
    
    solved = Solver(table).solve()

    await context_bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Я решил судоку\n{solved}",
        )

    
        


async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=("Привет! Я могу решить судоку. "
              "Чтобы начать просто отправь картинку с судоку"))

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    assert TOKEN
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    photo_handler = MessageHandler(filters.Document.IMAGE | filters.PHOTO, get_photo)
    application.add_handler(photo_handler)
    
    application.run_polling()
