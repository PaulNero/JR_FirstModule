from telegram import Update
from telegram.ext import ContextTypes

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

chat_gpt = ChatGptService(ChatGPT_TOKEN)

class Feature_Random_Word():
    @staticmethod
    async def random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Выводит случайное слово или предложение на английском с переводом
        """
        prompt = load_prompt('random_word')
        message = load_message('random_word')

        await send_image(update, context, name='random')
        message = await send_text(update, context, message)
        answer = await chat_gpt.send_question(prompt, message_text="")
        await message.edit_text(answer)