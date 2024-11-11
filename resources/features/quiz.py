from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, PicklePersistence

from credentials import ChatGPT_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

from resources.features import menu

persistence = PicklePersistence(filepath='bot_data')

chat_gpt = ChatGptService(ChatGPT_TOKEN)
QUIZ, HANDLE_QUIZ_THEME, HANDLE_QUIZ_ANSWER, HANDLE_QUIZ_MORE = range(4)

# TODO: Починить работу QUIZ в вынесенном файле и подружить его с персистентностью

class Feature_Quiz():
    @staticmethod
    async def handle_quiz_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Запускает GPT-сессию после команды /quiz и приглашает пользователя выбрать тему для квиза.
        """
        global BEST_SCORE
        # Сохраняем BEST_SCORE из bot_data для возобновления с предыдущего результата
        bot_data = await persistence.get_bot_data()
        context.bot_data["best_score"] = bot_data.get("best_score", 0)
        BEST_SCORE = context.bot_data.get("best_score", 0)
        context.user_data['current_right_score'] = 0

        buttons = [
            [InlineKeyboardButton("Программирование", callback_data='quiz_prog')],
            [InlineKeyboardButton("Математика", callback_data='quiz_math')],
            [InlineKeyboardButton("Биология", callback_data='quiz_biology')],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        message = load_message('quiz')
        await send_image(update, context, name='quiz')
        await update.message.reply_text(message, reply_markup=keyboard)
        return HANDLE_QUIZ_THEME  # Переход в состояние обработки вопросов

    @staticmethod
    async def handle_quiz_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает выбор темы для квиза.
        """
        btn = update.callback_query.data
        await update.callback_query.answer()  # Оповещение о нажатии кнопки

        themes = {
            'quiz_prog': 'quiz_prog',
            'quiz_math': 'quiz_math',
            'quiz_biology': 'quiz_biology',
        }

        if btn in themes:
            theme = themes[btn]
            context.user_data['theme'] = theme
            context.user_data['current_right_score'] = 0
            context.user_data['current_unright_score'] = 0

            prompt = load_prompt('quiz')
            chat_gpt.set_prompt(prompt)
            start_quiz = await chat_gpt.add_message(message_text=theme)
            await send_image(update, context, name='quiz')
            await send_text(update, context, start_quiz)
            return HANDLE_QUIZ_ANSWER  # Остаемся в режиме обработки ответов
        else:
            await Feature_Quiz.handle_quiz_entry(update, context)
            return HANDLE_QUIZ_THEME

    @staticmethod
    async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает ответ пользователя и записывает счет
        """
        global BEST_SCORE
        user_question = update.message.text
        message = await send_text(update, context, text='Думаю над вопросом...')
        answer = await chat_gpt.add_message(message_text=user_question)

        if "Правильно" in answer:
            context.user_data['current_right_score'] += 1
            Feature_Quiz.update_best_score(context, context.user_data['current_right_score'])
        else:
            context.user_data['current_unright_score'] += 1

        buttons = [
            [InlineKeyboardButton("Ещё вопрос", callback_data='quiz_more')]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            f"{answer} \nПравильных ответов: {context.user_data['current_right_score']}\nНеправильных ответов: {context.user_data['current_unright_score']}\nЛучший счет: {context.bot_data.get('best_score', 0)}",
            reply_markup=keyboard
        )
        return HANDLE_QUIZ_ANSWER  # Остаемся в режиме обработки вопросов

    @staticmethod
    async def handle_quiz_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обрабатывает кнопку "Задать ещё вопрос"
        """
        await update.callback_query.answer()  # Подтверждение клика по кнопке
        theme = context.user_data.get('theme')  # Извлекаем тему из user_data
        next_question = await chat_gpt.add_message(message_text=theme)
        await update.callback_query.edit_message_text(text=next_question)  # Отправляем новый вопрос

        return HANDLE_QUIZ_ANSWER  # Остаемся в режиме обработки вопросов

    @staticmethod
    def update_best_score(context, current_score):
        """
        Записывает лучший счет в память бота
        """
        best_score = context.bot_data.get("best_score", 0)
        if current_score > best_score:
            context.bot_data["best_score"] = current_score
            context.application.persistence.update_bot_data(context.bot_data)

    @staticmethod
    async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Завершает работу бота в режиме GPT.
        """
        await send_text(update, context, text="Сеанс связи завершен")
        await menu.Feature_Menu.menu(update, context)
        return ConversationHandler.END
