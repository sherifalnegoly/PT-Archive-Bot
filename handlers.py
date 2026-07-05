from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import (
    get_years,
    get_subjects_by_year,
    get_materials_by_subject_and_type,
    get_material_by_id,
)

# ==========================
# START
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    years = get_years()

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"year_{year_id}")]
        for year_id, name in years
    ]

    await update.message.reply_text(
        "🏥 Welcome to PT Archive Bot\n\nChoose Academic Year:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================
# MAIN BUTTON HANDLER
# ==========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # تجاهل الأدمن
    if data.startswith("admin_") or data.startswith("add_"):
      return

    # ==========================
    # YEARS
    # ==========================
    if data.startswith("year_"):

        year_id = int(data.replace("year_", ""))

        subjects = get_subjects_by_year(year_id)

        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"subject_{sid}")]
            for sid, name in subjects
        ]

        await query.message.reply_text(
            "📚 Choose Subject:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # SUBJECTS
    # ==========================
    elif data.startswith("subject_"):

        subject_id = int(data.replace("subject_", ""))

        context.user_data["subject_id"] = subject_id

        keyboard = [
            [InlineKeyboardButton("📚 Lectures", callback_data=f"lectures_{subject_id}")],
            [InlineKeyboardButton("🎥 Records", callback_data=f"records_{subject_id}")],
            [InlineKeyboardButton("📝 Assignments", callback_data=f"assignments_{subject_id}")]
        ]

        await query.message.reply_text(
            "Choose Material Type:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # LECTURES
    # ==========================
    elif data.startswith("lectures_"):

        subject_id = int(data.replace("lectures_", ""))

        items = get_materials_by_subject_and_type(subject_id, "lecture")

        if not items:
            await query.message.reply_text("No lectures available.")
            return

        keyboard = [
            [InlineKeyboardButton(title, callback_data=f"material_{mid}")]
            for mid, title in items
        ]

        await query.message.reply_text(
            "📚 Choose Lecture:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # RECORDS
    # ==========================
    elif data.startswith("records_"):

        subject_id = int(data.replace("records_", ""))

        items = get_materials_by_subject_and_type(subject_id, "record")

        if not items:
            await query.message.reply_text("No records available.")
            return

        keyboard = [
            [InlineKeyboardButton(title, callback_data=f"material_{mid}")]
            for mid, title in items
        ]

        await query.message.reply_text(
            "🎥 Choose Record:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # ASSIGNMENTS
    # ==========================
    elif data.startswith("assignments_"):

        subject_id = int(data.replace("assignments_", ""))

        items = get_materials_by_subject_and_type(subject_id, "assignment")

        if not items:
            await query.message.reply_text("No assignments available.")
            return

        keyboard = [
            [InlineKeyboardButton(title, callback_data=f"material_{mid}")]
            for mid, title in items
        ]

        await query.message.reply_text(
            "📝 Choose Assignment:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # ==========================
    # OPEN MATERIAL
    # ==========================
    elif data.startswith("material_"):

        material_id = int(data.split("_")[1])

        material = get_material_by_id(material_id)

        if not material:
            await query.message.reply_text("Material not found.")
            return

        material_type = material[2]
        title = material[3]
        file_id = material[4]

        if not file_id:
            await query.message.reply_text("File not found.")
            return

        if material_type in ["lecture", "assignment"]:
            await query.message.reply_document(
                document=file_id,
                caption=title
            )

        elif material_type == "record":
            await query.message.reply_video(
                video=file_id,
                caption=title
            )