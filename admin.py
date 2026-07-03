from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import ADMIN_ID
from db import get_years, get_subjects_by_year, add_material

CHOOSE_YEAR, CHOOSE_SUBJECT, RECEIVE_FILE, RECEIVE_TITLE = range(4)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not allowed")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Add Lecture", callback_data="add_lecture")],
        [InlineKeyboardButton("🎥 Add Record", callback_data="add_record")],
        [InlineKeyboardButton("📝 Add Assignment", callback_data="add_assignment")],
    ]

    await update.message.reply_text(
        "🛠 Admin Panel",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==========================
# Start Lecture
# ==========================

async def start_add_lecture(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["material_type"] = "lecture"

    return await start_add_material(update, context)


# ==========================
# Start Record
# ==========================

async def start_add_record(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["material_type"] = "record"

    return await start_add_material(update, context)


# ==========================
# Start Assignment
# ==========================

async def start_add_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["material_type"] = "assignment"

    return await start_add_material(update, context)


# ==========================
# Common Start
# ==========================

async def start_add_material(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    years = get_years()

    keyboard = []

    for yid, yname in years:
        keyboard.append([
            InlineKeyboardButton(
                yname,
                callback_data=f"year_{yid}"
            )
        ])

    await query.message.reply_text(
        "Choose Year:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CHOOSE_YEAR

async def choose_year(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    year_id = int(query.data.replace("year_", ""))

    context.user_data["year_id"] = year_id

    subjects = get_subjects_by_year(year_id)

    keyboard = []

    for sid, name in subjects:
        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"subject_{sid}"
            )
        ])

    await query.message.reply_text(
        "Choose Subject:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHOOSE_SUBJECT


async def choose_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    subject_id = int(query.data.replace("subject_", ""))

    context.user_data["subject_id"] = subject_id

    material_type = context.user_data["material_type"]

    if material_type == "record":
        await query.message.reply_text("Send Video File")
    else:
        await query.message.reply_text("Send PDF File")

    return RECEIVE_FILE


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    material_type = context.user_data["material_type"]

    if material_type == "record":

        if update.message.video:
            file_id = update.message.video.file_id

        elif update.message.document:
            file_id = update.message.document.file_id

        else:
            await update.message.reply_text("Please send a video.")
            return RECEIVE_FILE

    else:

        if not update.message.document:
            await update.message.reply_text("Please send a PDF.")
            return RECEIVE_FILE

        file_id = update.message.document.file_id

    context.user_data["file_id"] = file_id

    await update.message.reply_text("Send Title")

    return RECEIVE_TITLE


async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):

    title = update.message.text

    add_material(
        subject_id=context.user_data["subject_id"],
        material_type=context.user_data["material_type"],
        title=title,
        file_id=context.user_data["file_id"],
    )

    await update.message.reply_text("✅ Saved Successfully")

    context.user_data.clear()

    return ConversationHandler.END


admin_handler = ConversationHandler(

    entry_points=[

        CallbackQueryHandler(
            start_add_lecture,
            pattern="^add_lecture$"
        ),

        CallbackQueryHandler(
            start_add_record,
            pattern="^add_record$"
        ),

        CallbackQueryHandler(
            start_add_assignment,
            pattern="^add_assignment$"
        ),

    ],

    states={

        CHOOSE_YEAR: [
            CallbackQueryHandler(
                choose_year,
                pattern="^year_"
            )
        ],

        CHOOSE_SUBJECT: [
            CallbackQueryHandler(
                choose_subject,
                pattern="^subject_"
            )
        ],

        RECEIVE_FILE: [
            MessageHandler(
                filters.Document.ALL | filters.VIDEO,
                receive_file
            )
        ],

        RECEIVE_TITLE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receive_title
            )
        ],

    },

    fallbacks=[],
)