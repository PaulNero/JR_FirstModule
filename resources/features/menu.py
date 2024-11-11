from telegram import Update
from telegram.ext import ContextTypes

from util import load_message, send_text, send_image, show_main_menu

class Feature_Menu():
    @staticmethod
    async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Отображает главное меню бота пользователю по выполнению команды /menu и после завершения сессии общения с ChatGPT командой /end
        """
        text = load_message('main')
        await send_image(update, context, 'main')
        await send_text(update, context, text)
        await show_main_menu(update, context, {
            'menu': 'Главное меню',
            'random': 'Узнать случайный интересный факт 🧠',
            'gpt': 'Задать вопрос чату GPT 🤖',
            'talk': 'Поговорить с известной личностью 👤',
            'quiz': 'Поучаствовать в квизе ❓',
            'translator': 'Воспользуйся переводчиком',
            'idea': 'Генератор идей',
            'word': 'Случайное слово или выражение на английском',
            'end': 'Прервать сеанс связи с gpt'
            # Добавить команду в меню можно так:
            # 'command': 'button text'
        })
