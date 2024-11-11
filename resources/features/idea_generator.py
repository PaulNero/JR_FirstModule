from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

from resources.features import menu

chat_gpt = ChatGptService(ChatGPT_TOKEN)
IDEA, HANDLE_IDEA_GENERATOR = range(2)

class Feature_Idea():
    IDEA, HANDLE_IDEA_GENERATOR = range(2)

    @staticmethod
    async def handle_idea_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Запускает GPT-сессию после команды /idea и приглашает пользователя предложить контекст для генерации идеи.
        """
        prompt = load_prompt('idea')
        message = load_message('idea')
        chat_gpt.set_prompt(prompt)
        await send_image(update, context, name='idea')
        await send_text(update, context, message)
        return HANDLE_IDEA_GENERATOR  # Переход в состояние обработки вопросов

    @staticmethod
    async def handle_idea_generator(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает каждый новый ввод пользователя в режиме GPT.
        """
        user_question = update.message.text
        message = await send_text(update, context, text='Думаю над вопросом...')
        answer = await chat_gpt.add_message(message_text=user_question)
        await message.edit_text(answer)
        return HANDLE_IDEA_GENERATOR  # Остаемся в режиме обработки вопросов

    @staticmethod
    async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Завершает работу бота в режиме GPT.
        """
        await send_text(update, context, text="Сеанс связи завершен")
        await menu.Feature_Menu.menu(update, context)
        return ConversationHandler.END
