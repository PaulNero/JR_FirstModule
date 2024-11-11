from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, PicklePersistence

from credentials import ChatGPT_TOKEN, Bot_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text, send_image

from resources.features import start, \
    menu, \
    echo, \
    random_fact, \
    random_word, \
    gpt_question, \
    talk_with_famous_person as TALK, \
    translator, \
    idea_generator as idea, \
    quiz

"Билдер бота"
persistence = PicklePersistence(filepath='bot_data')
app = ApplicationBuilder().token(f"{Bot_TOKEN}").persistence(persistence).build()
# app = ApplicationBuilder().token(f"{Bot_TOKEN}").quiz.persistence.build()
# TODO: Починить работу QUIZ в вынесенном файле и подружить его с персистентностью
chat_gpt = ChatGptService(ChatGPT_TOKEN)

# TODO: Не смог провести декомпозицию с фичи QUIZ с наскоку
QUIZ, HANDLE_QUIZ_THEME, HANDLE_QUIZ_ANSWER, HANDLE_QUIZ_MORE = range(4)

async def handle_quiz_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запускает GPT-сессию после команды /quiz и приглашает пользователя выбрать тему для квиза.
    """
    global BEST_SCORE
    # Сохраняем BEST_SCORE из bot_data для возобновления с предыдущего результата
    bot_data = await app.persistence.get_bot_data()
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
        await handle_quiz_entry(update, context)
        return HANDLE_QUIZ_THEME

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
        update_best_score(context, context.user_data['current_right_score'])
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
    return HANDLE_QUIZ_ANSWER # Остаемся в режиме обработки вопросов


async def handle_quiz_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает кнопку "Задать ещё вопрос"
    """
    await update.callback_query.answer()  # Подтверждение клика по кнопке
    theme = context.user_data.get('theme')  # Извлекаем тему из user_data
    next_question = await chat_gpt.add_message(message_text=theme)
    await update.callback_query.edit_message_text(text=next_question)  # Отправляем новый вопрос

    return HANDLE_QUIZ_ANSWER  # Остаемся в режиме обработки вопросов

def update_best_score(context, current_score):
    """
    Записывает лучший счет в память бота
    """
    best_score = context.bot_data.get("best_score", 0)
    if current_score > best_score:
        context.bot_data["best_score"] = current_score
        context.application.persistence.update_bot_data(context.bot_data)

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершает работу бота в режиме GPT.
    """
    await send_text(update, context, text="Сеанс связи завершен")
    await menu.Feature_Menu.menu(update, context)
    return ConversationHandler.END

"Обработчик команд"
app.add_handler(CommandHandler(
    command='start',
    callback=start.Feature_Start.start))
app.add_handler(CommandHandler(
    command='menu',
    callback=menu.Feature_Menu.menu))
app.add_handler(CommandHandler(
    command="random",
    callback=random_fact.Feature_Random_Fact.random_fact))
app.add_handler(CommandHandler(
    command="word",
    callback=random_word.Feature_Random_Word.random_word))

"Обработчик диалогов"
conv_gpt = ConversationHandler(
    entry_points=[CommandHandler("gpt", gpt_question.Feature_Gpt_Question.handle_gpt_entry)],
    states={
        gpt_question.HANDLE_GPT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_question.Feature_Gpt_Question.handle_gpt_question)]
    },
    fallbacks=[
        CommandHandler("end", gpt_question.Feature_Gpt_Question.end_conversation)]
)
app.add_handler(conv_gpt)

conv_famous = ConversationHandler(
    entry_points=[CommandHandler("talk", TALK.Feature_Talk_With_Famous.handle_talk_entry)],
    states={
        TALK.HANDLE_TALK_PERSON: [CallbackQueryHandler(TALK.Feature_Talk_With_Famous.handle_talk_person, pattern='^talk_.*')],
        TALK.HANDLE_TALK_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, TALK.Feature_Talk_With_Famous.handle_talk_conversation)]
    },
    fallbacks=[
        CommandHandler("end", TALK.Feature_Talk_With_Famous.end_conversation)]
)
app.add_handler(conv_famous)

conv_quiz = ConversationHandler(
    entry_points=[CommandHandler("quiz", handle_quiz_entry)],
    states={
        HANDLE_QUIZ_THEME: [CallbackQueryHandler(handle_quiz_theme, pattern='^quiz_.*')],
        HANDLE_QUIZ_ANSWER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quiz_answer),
            CallbackQueryHandler(handle_quiz_more, pattern='^quiz_more$')  # для кнопки «Ещё вопрос»
        ]
    },
    fallbacks=[
        CommandHandler("end", end_conversation)]
)
app.add_handler(conv_quiz)

# conv_quiz = ConversationHandler(
#     entry_points=[CommandHandler("quiz", quiz.Feature_Quiz.handle_quiz_entry)],
#     states={
#         quiz.HANDLE_QUIZ_THEME: [CallbackQueryHandler(quiz.Feature_Quiz.handle_quiz_theme, pattern='^quiz_.*')],
#         quiz.HANDLE_QUIZ_ANSWER: [
#             MessageHandler(filters.TEXT & ~filters.COMMAND, quiz.Feature_Quiz.handle_quiz_answer),
#             CallbackQueryHandler(quiz.Feature_Quiz.handle_quiz_more, pattern='^quiz_more$')  # для кнопки «Ещё вопрос»
#         ]
#     },
#     fallbacks=[
#         CommandHandler("end", quiz.Feature_Quiz.end_conversation)]
# )
# app.add_handler(conv_quiz)

conv_translator = ConversationHandler(
    entry_points=[CommandHandler("translator", translator.Feature_Translator.handle_translator_entry)],
    states={
        translator.HANDLE_TRANSLATOR_LANGUAGE: [CallbackQueryHandler(translator.Feature_Translator.handle_translator_language, pattern='^translator_.*')],
        translator.HANDLE_TRANSLATOR_PROCESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, translator.Feature_Translator.handle_translator_process)]
    },
    fallbacks=[
        CommandHandler("end", translator.Feature_Translator.end_conversation)]
)
app.add_handler(conv_translator)

conv_idea = ConversationHandler(
    entry_points=[CommandHandler("idea", idea.Feature_Idea.handle_idea_entry)],
    states={
        idea.HANDLE_IDEA_GENERATOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, idea.Feature_Idea.handle_idea_generator)]
    },
    fallbacks=[
        CommandHandler("end", idea.Feature_Idea.end_conversation)]
)
app.add_handler(conv_idea)



# app.add_handler(CommandHandler(
#     command="gpt",
#     callback=gpt))

# app.add_handler(CommandHandler('start', start))
# Зарегистрировать обработчик команды можно так:
# app.add_handler(CommandHandler('command', handler_func))

# Зарегистрировать обработчик кнопки можно так:
# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
# app.add_handler(CallbackQueryHandler(default_callback_handler))


"Обработчик текста"
app.add_handler(MessageHandler(
    filters.TEXT &
    ~filters.COMMAND,
    echo.Feature_Echo.echo))

app.run_polling()
