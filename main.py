from keep_alive import keep_alive
from telegram import Update
from telegram.ext import (Application, ApplicationBuilder, CommandHandler,
                          MessageHandler, filters, ContextTypes,
                          ConversationHandler)

# 🆔 Укажи свой Telegram ID здесь
ADMIN_ID = 8058164231
# ← Замени на свой ID

ASK_IG, ASK_AGE, ASK_TIME, ASK_PARTY = range(4)

final_message = """✅ Спасибо за анкету!
    
    😈 Welcome в ночное комьюнити Бангкока 🥂🌃
    
    🔥 Переходи в наш *закрытый канал* — там афиши, фото и вся ночная движуха Бангкока
    👉 [Войти в канал](https://t.me/+ztVkwOXZqPozZWE9)
    """


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Это фейс-контроль для приватных тусовок в Бангкоке 🪩\n\n"
        "Хочешь попасть? Давай начнем.\n\n"
        "1️⃣ Ссылку на свой Instagram (без @) или отправь фото.\n"
        "🔓 Профиль должен быть открытым и с личными фото*")

    context.user_data.clear()

    return ASK_IG


async def receive_ig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        user_data["ig_text"] = "📸 Фото"
        user_data["ig_photo"] = file_id
        if update.message.caption:
            user_data["ig_text"] = update.message.caption
        else:
            user_data["ig_text"] = "📸 Фото"
            
    elif update.message.text:
        user_data["ig_text"] = update.message.text
        user_data["ig_photo"] = None
    else:
        await update.message.reply_text("Пожалуйста, отправь фото или ссылку на Instagram.")
        return ASK_IG

    await update.message.reply_text("2️⃣ Сколько тебе лет?")
    return ASK_AGE


async def receive_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("3️⃣ Как давно ты в Бангкоке?")
    return ASK_TIME


async def receive_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text
    await update.message.reply_text("4️⃣ Часто ли бываешь на вечеринках?")
    return ASK_PARTY


async def receive_party(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["party"] = update.message.text

    ig_text = context.user_data.get("ig_text", "-")
    photo_id = context.user_data.get("ig_photo", None)
    age = context.user_data.get("age", "-")
    time = context.user_data.get("time", "-")
    party = context.user_data.get("party", "-")

    username = update.effective_user.username
    user_id = update.effective_user.id
    tg_contact = f"@{username}" if username else f"tg://user?id={user_id}"

    ig_link = f"[📎 Открыть профиль](https://instagram.com/{ig_text.lstrip('@')})" if ig_text != "-" else ""

    message_text = ("📩 *Новая анкета:*\n\n"
                    f"📎 Instagram: {ig_text}\n"
                    f"{ig_link}\n"
                    f"📅 Возраст: {age}\n"
                    f"🌍 В Бангкоке: {time}\n"
                    f"🎉 Тусовки: {party}\n"
                    f"📱 Telegram: {tg_contact}")

    try:
        if photo_id:
            await context.bot.send_photo(chat_id=ADMIN_ID,
                                         photo=photo_id,
                                         caption=message_text,
                                         parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text=message_text,
                                           parse_mode="Markdown")
    except Exception as e:
        print("Ошибка при отправке админу:", e)

    await update.message.reply_text(final_message, parse_mode="Markdown")
    return ConversationHandler.END


async def info(update, context):
    await update.message.reply_text(
        "👋 Этот бот для фейс-контроля в закрытое тусовочное комьюнити Бангкока.\n\n"
        "🚨 Мы собираем ярких, стильных и активных людей, которые любят nightlife.\n\n"
        "📩 Пройди анкету через /start — и если ты с вайбом, тебе откроется доступ к нашему телеграм-каналу с афишами, списками и движем.\n\n"
        "🎉 Вход в наши клубы всегда бесплатный — тусовки, новые лица и алкоголь на месте 🍸"
    )


async def rules(update, context):
    await update.message.reply_text(
        "📜 *Правила участия и поведения:*\n\n"
        "✨ Будь вежлив — здесь собираются классные, разные, но всегда уважительные люди.\n"
        "🚫 Неадекват и агрессия — сразу в черный лист. Мы за комфорт и лёгкий вайб.\n"
        "👟 Дресс-код = настроение вечеринки. Без шлёпанцев, маек-алкоголичек и \"только с пляжа\". Стильно — значит в теме.\n"
        "🎵 Слушай музыку, танцуй, общайся — но не мешай другим кайфовать.\n"
        "⏰ Приходи вовремя — мы ценим тех, кто в теме с первых минут.\n"
        "💜 Если ты с вайбом — welcome. 💜\n"
        "🔞 20+ - только для взрослых.🔞",
        parse_mode="Markdown")


async def contact(update, context):
    await update.message.reply_text("📩 Написать организатору: @igordotgif")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, отменили. Увидимся позже 👋")
    return ConversationHandler.END


def main():
    import os
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.PHOTO | filters.TEXT, receive_ig)
    ],
    states={
            ASK_IG: [MessageHandler(filters.TEXT | filters.PHOTO, receive_ig)],
            ASK_AGE: [MessageHandler(filters.TEXT, receive_age)],
            ASK_TIME: [MessageHandler(filters.TEXT, receive_time)],
            ASK_PARTY: [MessageHandler(filters.TEXT, receive_party)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    keep_alive()
    main()
