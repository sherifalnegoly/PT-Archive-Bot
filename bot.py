from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)

from handlers import start, button_handler
from admin import admin_panel, admin_handler

from config import TOKEN

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))

app.add_handler(admin_handler)
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot is running...")
app.run_polling()