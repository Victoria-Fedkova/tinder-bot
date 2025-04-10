from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from dotenv import load_dotenv
import os

load_dotenv()
from gpt import *
from util import *

TOKEN = os.getenv("TOKEN")

# тут будемо писати наш код :)
async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "Головне меню бота",
        "profile": "Генерація Tinder - профілю \uD83D\uDE0E",
        "opener": "Повідомлення для знайомства \uD83E\uDD70",
        "message": "Листування від вашого імені \uD83D\uDE08",
        "date": "Листування із зірками \uD83D\uDD25",
        "gpt": "Поставити запитання чату GPT \uD83E\uDDE0"
    })

async def gpt(update, context):
    dialog.mode = "gpt"
    await send_photo(update, context, "gpt")

    msg = load_message("gpt")
    await send_text(update, context, msg)

async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await  send_text(update, context, answer)

async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, 'Друкує повідомлення...')
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def date (update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text,{
        "date_grande":"Аріана Гранде",
        "date_robbie": "Марго Роббі",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослінг",
        "date_hardy": "Том Харді",

    })

async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)

    names = {
        "date_grande": "Аріану Гранде",
        "date_robbie": "Марго Роббі",
        "date_zendaya": "Зендею",
        "date_gosling": "Райана Гослінга",
        "date_hardy": "Тома Харді",
    }

    person_name = names.get(query, "обрану особу")

    await send_text(update, context, f"Гарний вибір! 😅 Ваша задача запросити {person_name} на побачення за 5 повідомлень! ❤️")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)

async def message_dialog(update, context):
    text= update.message.text
    dialog.list.append(text)

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "/n/n".join(dialog.list)

    my_message = await  send_text(update, context, "Думаю над варіантами...")

    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)

async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "Привіт!")
        await send_text(update, context, "Ти написав " + update.message.text)
        await send_text(update, context, "Обери режим в меню для обробки повідомлень")

async def message(update, context):
    dialog.mode = 'message'
    msg = load_message('message')
    await  send_photo(update, context, 'message')
    await  send_text_buttons(update, context, msg, {
        "message_next": "Написати повідомлення",
        "message_date": "Запросити на побачення",

    })

    dialog.list.clear()

async def profile(update, context):
    dialog.mode = 'profile'
    msg = load_message('profile')
    await  send_photo(update, context, 'profile')
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Ваше імʼя і скільки вам років?")



async def profile_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if  dialog.counter == 1:
        dialog.user['age'] = text
        await send_text(update, context, "Ким ви працюєте?")
    elif  dialog.counter == 2:
        dialog.user['oppupation'] = text
        await send_text(update, context, "У вас є хоббі?")
    elif dialog.counter == 3:
        dialog.user['hobby'] = text
        await send_text(update, context, "Що вам НЕ подобається в людях?")
    elif dialog.counter == 4:
        dialog.user['annoys'] = text
        await send_text(update, context, "Мета знайомства?")
    elif dialog.counter == 5:
        dialog.user['goal'] = text
        prompt = load_prompt('profile')
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "Чат GPT генерує ваш профіль. Зачекайте декілька секунд...")
        answer = await chatgpt.send_question(prompt, user_info)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Згенерувати ще", callback_data='profile_regenerate')]
        ])

        await my_message.edit_text(answer, reply_markup=keyboard)

async def handle_profile_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'profile_regenerate':
        prompt = load_prompt('profile')
        user_info = dialog_user_info_to_str(dialog.user)

        await query.edit_message_reply_markup()
        await query.message.reply_text("🔁 Генеруємо новий профіль...")

        answer = await chatgpt.send_question(prompt, user_info)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Згенерувати ще", callback_data='profile_regenerate')]
        ])
        await query.message.reply_text(answer, reply_markup=keyboard)


async def opener(update, context):
    dialog.mode = 'opener'
    msg = load_message('opener')
    await  send_photo(update, context, 'opener')
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Імʼя дівчини/хлопця?")

async def opener_dialog(update, context):
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user['name'] = text
        await send_text(update, context, "Скільки років їй/йому?")
    elif dialog.counter == 2:
        dialog.user['age'] = text
        await send_text(update, context, "Оцініть її/його зовнішність: 1-10 балів?")
    elif dialog.counter == 3:
        dialog.user['handsome'] = text
        await send_text(update, context, "Ким він/вона працює?")
    elif dialog.counter == 4:
        dialog.user['occupation'] = text
        await send_text(update, context, "Мета знайомства?")
    elif dialog.counter == 5:
        dialog.user['goal'] = text

        prompt = load_prompt('opener')
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "Чат GPT генерує ваше повідомлення. Зачекайте декілька секунд...")
        answer = await chatgpt.send_question(prompt, user_info)
        # await my_message.edit_text(answer)

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👍 Подобається", callback_data='opener_like'),
                InlineKeyboardButton("🔁 Згенерувати ще", callback_data='opener_regenerate')
            ]
        ])

        await my_message.edit_text(answer, reply_markup=keyboard)


async def handle_opener_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'opener_like':
        await query.edit_message_reply_markup()
        await query.message.reply_text("✅ Збережено. Успіхів у знайомствах! 😎")

    elif query.data == 'opener_regenerate':
        prompt = load_prompt('opener')
        user_info = dialog_user_info_to_str(dialog.user)

        await query.edit_message_reply_markup()
        await query.message.reply_text("🔁 Генеруємо новий варіант...")

        new_answer = await chatgpt.send_question(prompt, user_info)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👍 Подобається", callback_data='opener_like'),
                InlineKeyboardButton("🔁 Згенерувати ще", callback_data='opener_regenerate')
            ]
        ])
        await query.message.reply_text(new_answer, reply_markup=keyboard)

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user ={}
dialog.counter = 0

GPT_TOKEN = os.getenv("GPT_TOKEN")
chatgpt = ChatGptService(token=GPT_TOKEN)

app = ApplicationBuilder().token(TOKEN).build()

#  Добавляем команду /start и /gpt
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))


#  Тексты без команд
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

#  Обработка кнопок
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(handle_profile_callback, pattern="^profile_"))
app.add_handler(CallbackQueryHandler(handle_opener_callback, pattern="^opener_"))


app.run_polling()

