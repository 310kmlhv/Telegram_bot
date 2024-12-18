import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bot_token import TOKEN
def load_countries():
    with open("countries.json", "r", encoding="utf-8") as file:
        return json.load(file)

def save_settings(settings):
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file)

def load_settings():
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_settings()
    user_id = str(update.effective_user.id)
    user_lang = settings.get(user_id, "ru")

    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Выбранный язык: {'🇷🇺 Русский' if user_lang == 'ru' else '🇬🇧 English'}",
        reply_markup=reply_markup
    )

async def list_countries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    countries = load_countries()
    settings = load_settings()
    user_id = str(update.effective_user.id)
    user_lang = settings.get(user_id, "ru")

    keyboard = [[InlineKeyboardButton(f"{data['flag']} {data['description'][user_lang].split(' ')[0]}", callback_data=f"country:{name}")] for name, data in countries.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выберите страну:", reply_markup=reply_markup)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data

    if data.startswith("lang:"):
        settings = load_settings()
        user_id = str(query.from_user.id)
        selected_lang = data.split(":")[1]

        settings[user_id] = selected_lang
        save_settings(settings)

        await query.edit_message_text(
            f"Язык успешно изменён на {'🇷🇺 Русский' if selected_lang == 'ru' else '🇬🇧 English'}."
        )

    elif data.startswith("country:"):
        country_name = data.split(":")[1]
        countries = load_countries()
        settings = load_settings()
        user_id = str(query.from_user.id)
        user_lang = settings.get(user_id, "ru")

        country = countries.get(country_name)
        if country:
            flag = country["flag"]
            description = country["description"][user_lang]
            await query.edit_message_text(f"{flag} {country_name}\n\n{description}")
        else:
            await query.edit_message_text("Информация о стране не найдена.")

async def set_commands(application):
    commands = [
        BotCommand("settings", "Настройки языка"),
        BotCommand("list", "Показать список стран")
    ]
    await application.bot.set_my_commands(commands)

import asyncio

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("list", list_countries))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()
