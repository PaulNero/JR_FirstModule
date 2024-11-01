from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, \
    CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, PicklePersistence

from credentials import ChatGPT_TOKEN, Bot_TOKEN
from gpt import ChatGptService
from util import load_message, load_prompt, send_text_buttons, send_text, \
    send_image, show_main_menu, Dialog, default_callback_handler

"Билдер бота"
persistence = PicklePersistence(filepath='bot_data')
app = ApplicationBuilder().token(f"{Bot_TOKEN}").persistence(persistence).build()
chat_gpt = ChatGptService(ChatGPT_TOKEN)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('start')
    await send_text(update, context, text)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # dialog.mode = 'main'
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


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выводит сообщение пользователя, обратно пользователю.
    """
    await send_text(update, context, update.message.text)


async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выводит рандомный факт
    """
    prompt = load_prompt('random')
    message = load_message('random')

    await send_image(update, context, name='random')
    message = await send_text(update, context, message)
    answer = await chat_gpt.send_question(prompt, message_text="")
    await message.edit_text(answer)

async def random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выводит рандомный факт
    """
    prompt = load_prompt('random_word')
    message = load_message('random_word')

    await send_image(update, context, name='random')
    message = await send_text(update, context, message)
    answer = await chat_gpt.send_question(prompt, message_text="")
    await message.edit_text(answer)


GPT, HANDLE_GPT_QUESTION = range(2)
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

async def handle_gpt_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает каждый новый ввод пользователя в режиме GPT.
    """
    user_question = update.message.text
    message = await send_text(update, context, text='Думаю над вопросом...')
    answer = await chat_gpt.add_message(message_text=user_question)
    await message.edit_text(answer)
    return HANDLE_GPT_QUESTION  # Остаемся в режиме обработки вопросов

TALK, HANDLE_TALK_PERSON, HANDLE_TALK_CONVERSATION = range(3)
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

async def handle_talk_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает каждый новый ввод пользователя в режиме GPT.
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
        greeting = await chat_gpt.add_message(message_text="Представься и поздаровайся с пользователем как это сделала ла бы выбранная личность")
        await send_text(update, context, greeting)

        return HANDLE_TALK_CONVERSATION  # Переход в состояние общения с выбранной личностью
    else:
        await handle_talk_entry(update, context)  # Повторный показ выбора, если callback_data не распознана
        return HANDLE_TALK_PERSON  # Возвращаемся к выбору личности

async def handle_talk_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    message = await send_text(update, context, text='Думаю над вопросом...')
    answer = await chat_gpt.add_message(message_text=user_question)
    await message.edit_text(answer)
    return HANDLE_TALK_CONVERSATION  # Остаемся в режиме обработки вопросов

QUIZ, HANDLE_QUIZ_THEME, HANDLE_QUIZ_ANSWER, HANDLE_QUIZ_MORE = range(4)

# BEST_SCORE = app.persistence.get_bot_data().get("best_score", 0)
# # Функция обновления и сохранения лучшего результата
# def update_best_score(context, current_score):
#     global BEST_SCORE
#     if current_score > BEST_SCORE:
#         BEST_SCORE = current_score
#         # Обновляем и сохраняем лучший результат в bot_data
#         context.bot_data["best_score"] = BEST_SCORE

async def handle_quiz_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запускает GPT-сессию после команды /gpt и приглашает пользователя задать вопрос.
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
        await handle_talk_entry(update, context)
        return HANDLE_QUIZ_THEME

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.callback_query.answer()  # Подтверждение клика по кнопке
    theme = context.user_data.get('theme')  # Извлекаем тему из user_data
    next_question = await chat_gpt.add_message(message_text=theme)
    await update.callback_query.edit_message_text(text=next_question)  # Отправляем новый вопрос

    return HANDLE_QUIZ_ANSWER  # Остаемся в режиме обработки вопросов

def update_best_score(context, current_score):
    best_score = context.bot_data.get("best_score", 0)
    if current_score > best_score:
        context.bot_data["best_score"] = current_score
        context.application.persistence.update_bot_data(context.bot_data)

TRANSLATOR, HANDLE_TRANSLATOR_LANGUAGE, HANDLE_TRANSLATOR_PROCESS = range(3)
async def handle_translator_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def handle_translator_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает каждый новый ввод пользователя в режиме GPT.
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
        # await send_image(update, context, name=language_key)  # Отправляем изображение выбранной личности
        greeting = await chat_gpt.add_message(
            message_text=f"Выбранный язык: {language_key}, Поздаровайся с пользователем как это сделалал бы носитель выбранного языка")
        await send_text(update, context, greeting)

        return HANDLE_TRANSLATOR_PROCESS  # Переход в состояние общения с выбранной личностью
    else:
        await handle_translator_entry(update, context)  # Повторный показ выбора, если callback_data не распознана
        return HANDLE_TRANSLATOR_LANGUAGE  # Возвращаемся к выбору личности

async def handle_translator_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    message = await send_text(update, context, text='Думаю над вопросом...')
    answer = await chat_gpt.add_message(message_text=user_question)
    await message.edit_text(answer)
    return HANDLE_TALK_CONVERSATION  # Остаемся в режиме обработки вопросов

IDEA, HANDLE_IDEA_GENERATOR = range(2)
async def handle_idea_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запускает GPT-сессию после команды /gpt и приглашает пользователя задать вопрос.
    """
    prompt = load_prompt('idea')
    message = load_message('idea')
    chat_gpt.set_prompt(prompt)
    await send_image(update, context, name='idea')
    await send_text(update, context, message)
    return HANDLE_GPT_QUESTION  # Переход в состояние обработки вопросов

async def handle_idea_generator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает каждый новый ввод пользователя в режиме GPT.
    """
    user_question = update.message.text
    message = await send_text(update, context, text='Думаю над вопросом...')
    answer = await chat_gpt.add_message(message_text=user_question)
    await message.edit_text(answer)
    return HANDLE_GPT_QUESTION  # Остаемся в режиме обработки вопросов










async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text(update, context, text="Сеанс связи завершен")
    await menu(update, context)
    return ConversationHandler.END


# dialog = Dialog()
# dialog.mode = None
# # Переменные можно определить, как атрибуты dialog

"Обработчик команд"
app.add_handler(CommandHandler(
    command='start',
    callback=start))
app.add_handler(CommandHandler(
    command='menu',
    callback=menu))
app.add_handler(CommandHandler(
    command="random",
    callback=random_fact))
app.add_handler(CommandHandler(
    command="word",
    callback=random_word))

"Обработчик диалогов"
conv_gpt = ConversationHandler(
    entry_points=[CommandHandler("gpt", handle_gpt_entry)],
    states={
        HANDLE_GPT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gpt_question)]
    },
    fallbacks=[
        CommandHandler("end", end_conversation)]
)
app.add_handler(conv_gpt)

conv_famous = ConversationHandler(
    entry_points=[CommandHandler("talk", handle_talk_entry)],
    states={
        HANDLE_TALK_PERSON: [CallbackQueryHandler(handle_talk_person, pattern='^talk_.*')],
        HANDLE_TALK_CONVERSATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_talk_conversation)]
    },
    fallbacks=[
        CommandHandler("end", end_conversation)]
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

conv_translator = ConversationHandler(
    entry_points=[CommandHandler("translator", handle_translator_entry)],
    states={
        HANDLE_TRANSLATOR_LANGUAGE: [CallbackQueryHandler(handle_translator_language, pattern='^translator_.*')],
        HANDLE_TRANSLATOR_PROCESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_translator_process)]
    },
    fallbacks=[
        CommandHandler("end", end_conversation)]
)
app.add_handler(conv_translator)

conv_idea = ConversationHandler(
    entry_points=[CommandHandler("idea", handle_idea_entry)],
    states={
        HANDLE_GPT_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea_generator)]
    },
    fallbacks=[
        CommandHandler("end", end_conversation)]
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
    echo))

app.run_polling()
