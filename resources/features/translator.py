from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

from resources.features import menu

chat_gpt = ChatGptService(ChatGPT_TOKEN)
TRANSLATOR, HANDLE_TRANSLATOR_LANGUAGE, HANDLE_TRANSLATOR_PROCESS = range(3)

class Feature_Translator():
    @staticmethod
    async def handle_translator_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Запускает GPT-сессию после команды /translator и приглашает пользователя выбрать язык.
        """
        buttons = [
            [InlineKeyboardButton("Английский", callback_data='translator_english')],
            [InlineKeyboardButton("Мандаринский", callback_data='translator_china')],
            [InlineKeyboardButton("Хинди", callback_data='translator_hindi')],
            [InlineKeyboardButton("Испанский", callback_data='translator_spain')],
            [InlineKeyboardButton("Французский", callback_data='translator_french')],
            [InlineKeyboardButton("Арабский", callback_data='translator_arabic')],
            [InlineKeyboardButton("Бенгальский", callback_data='translator_bengal')],
            [InlineKeyboardButton("Португальский", callback_data='translator_portugal')],
            [InlineKeyboardButton("Русский", callback_data='translator_russian')],
            [InlineKeyboardButton("Урду", callback_data='translator_urdu')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        message = load_message('translator')
        await send_image(update, context, name='translator')
        await update.message.reply_text(message, reply_markup=keyboard)
        return HANDLE_TRANSLATOR_LANGUAGE  # Переход в состояние обработки вопросов

    @staticmethod
    async def handle_translator_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает выбранный пользователем язык.
        """
        btn = update.callback_query.data
        await update.callback_query.answer()  # Оповещение о нажатии кнопки

        # Определение личности для общения
        languages = {
            'translator_english': 'translator_english',
            'translator_china': 'translator_china',
            'translator_hindi': 'translator_hindi',
            'translator_spain': 'translator_spain',
            'translator_french': 'translator_french',
            'translator_arabic': 'translator_arabic',
            'translator_bengal': 'translator_bengal',
            'translator_portugal': 'translator_portugal',
            'translator_russian': 'translator_russian',
            'translator_urdu': 'translator_urdu',
        }

        if btn in languages:
            language_key = languages[btn]
            prompt = load_prompt('translator')
            chat_gpt.set_prompt(prompt)
            # await send_image(update, context, name=language_key)  # TODO Добавить изображения флагов
            greeting = await chat_gpt.add_message(
                message_text=f"Выбранный язык: {language_key}, Поздаровайся с пользователем как это сделалал бы носитель выбранного языка")
            await send_text(update, context, greeting)

            return HANDLE_TRANSLATOR_PROCESS  # Переход в состояние общения с выбранной личностью
        else:
            await Feature_Translator.handle_translator_entry(update, context)  # Повторный показ выбора, если callback_data не распознана
            return HANDLE_TRANSLATOR_LANGUAGE  # Возвращаемся к выбору личности

    @staticmethod
    async def handle_translator_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает каждый новый ввод пользователя в режиме GPT.
        """
        user_question = update.message.text
        message = await send_text(update, context, text='Думаю над вопросом...')
        answer = await chat_gpt.add_message(message_text=user_question)
        await message.edit_text(answer)
        return HANDLE_TRANSLATOR_PROCESS  # Остаемся в режиме обработки вопросов

    @staticmethod
    async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Завершает работу бота в режиме GPT.
        """
        await send_text(update, context, text="Сеанс связи завершен")
        await menu.Feature_Menu.menu(update, context)
        return ConversationHandler.END
