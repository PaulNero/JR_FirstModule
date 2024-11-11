from telegram import Update
from telegram.ext import ContextTypes

from util import load_message, send_text

class Feature_Start():
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Запускает работу бота после выполнения команды /start
        """
        text = load_message('start')
        await send_text(update, context, text)
