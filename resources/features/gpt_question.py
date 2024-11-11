from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

from resources.features import menu

chat_gpt = ChatGptService(ChatGPT_TOKEN)
GPT, HANDLE_GPT_QUESTION = range(2)

class Feature_Gpt_Question():
    @staticmethod
    async def handle_gpt_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Запускает GPT-сессию после команды /gpt и приглашает пользователя задать вопрос.
        """
        prompt = load_prompt('gpt')
        message = load_message('gpt')
        chat_gpt.set_prompt(prompt)
        await send_image(update, context, name='gpt')
        await send_text(update, context, message)
        return HANDLE_GPT_QUESTION  # Переход в состояние обработки вопросов

    @staticmethod
    async def handle_gpt_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает каждый новый ввод пользователя в режиме GPT.
        """
        user_question = update.message.text
        message = await send_text(update, context, text='Думаю над вопросом...')
        answer = await chat_gpt.add_message(message_text=user_question)
        await message.edit_text(answer)
        return HANDLE_GPT_QUESTION  # Остаемся в режиме обработки вопросов

    @staticmethod
    async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Завершает работу бота в режиме GPT.
        """
        await send_text(update, context, text="Сеанс связи завершен")
        await menu.Feature_Menu.menu(update, context)
        return ConversationHandler.END
