from telegram import Update
from telegram.ext import ContextTypes

from util import send_text

class Feature_Echo():
    @staticmethod
    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Выводит сообщение пользователя, обратно пользователю.
        """
        await send_text(update, context, update.message.text)