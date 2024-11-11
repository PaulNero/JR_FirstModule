from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

from resources.features import menu

chat_gpt = ChatGptService(ChatGPT_TOKEN)
TALK, HANDLE_TALK_PERSON, HANDLE_TALK_CONVERSATION = range(3)

class Feature_Talk_With_Famous():
    @staticmethod
    async def handle_talk_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Запускает Talk-сессию после команды /talk и приглашает пользователя задать вопрос.
        """
        buttons = [
            [InlineKeyboardButton("Курт Кобейн", callback_data='talk_cobain')],
            [InlineKeyboardButton("Стивен Хоккинг", callback_data='talk_hawking')],
            [InlineKeyboardButton("Фридрих Ницше", callback_data='talk_nietzsche')],
            [InlineKeyboardButton("Королева Елизавета II", callback_data='talk_queen')],
            [InlineKeyboardButton("Дж. Р. Р. Толкин", callback_data='talk_tolkien')]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        message = load_message('talk')
        await send_image(update, context, name='talk')
        await update.message.reply_text(message, reply_markup=keyboard)
        return HANDLE_TALK_PERSON

    @staticmethod
    async def handle_talk_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает выбор персонажа для общения
        """
        btn = update.callback_query.data
        await update.callback_query.answer()  # Оповещение о нажатии кнопки

        # Определение личности для общения
        personalities = {
            'talk_cobain': 'talk_cobain',
            'talk_hawking': 'talk_hawking',
            'talk_nietzsche': 'talk_nietzsche',
            'talk_queen': 'talk_queen',
            'talk_tolkien': 'talk_tolkien',
        }

        if btn in personalities:
            person_key = personalities[btn]
            prompt = load_prompt(person_key)  # Загружаем соответствующий prompt
            chat_gpt.set_prompt(prompt)
            await send_image(update, context, name=person_key)  # Отправляем изображение выбранной личности
            greeting = await chat_gpt.add_message(
                message_text="Представься и поздаровайся с пользователем как это сделала ла бы выбранная личность")
            await send_text(update, context, greeting)

            return HANDLE_TALK_CONVERSATION  # Переход в состояние общения с выбранной личностью
        else:
            await Feature_Talk_With_Famous.handle_talk_entry(update, context)  # Повторный показ выбора, если callback_data не распознана
            return HANDLE_TALK_PERSON  # Возвращаемся к выбору личности

    @staticmethod
    async def handle_talk_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает каждый новый ввод пользователя в режиме GPT.
        """
        user_question = update.message.text
        message = await send_text(update, context, text='Думаю над вопросом...')
        answer = await chat_gpt.add_message(message_text=user_question)
        await message.edit_text(answer)
        return HANDLE_TALK_CONVERSATION  # Остаемся в режиме обработки вопросов

    @staticmethod
    async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Завершает работу бота в режиме GPT.
        """
        await send_text(update, context, text="Сеанс связи завершен")
        await menu.Feature_Menu.menu(update, context)
        return ConversationHandler.END
