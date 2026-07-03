from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import (
    get_years,
    get_subjects_by_year,
    get_materials_by_subject_and_type,
    get_material_by_id,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    years = get_years()

    keyboard = []

    for year_id, year_name in years:
        keyboard.append([
            InlineKeyboardButton(
                year_name,
                callback_data=f"year_{year_id}"
            )
        ])

    await update.message.reply_text(
        "🏥 Welcome to PT Archive Bot\n\nChoose Academic Year:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("admin_") or data in ["add_lecture", "add_record", "add_assignment"]:
        return
    # ==========================
    # Choose Year
    # ==========================
    if data.startswith("year_"):

        year_id = int(data.replace("year_", ""))

        subjects = get_subjects_by_year(year_id)
        print(subjects)

        keyboard = []

        for subject_id, subject_name in subjects:
            keyboard.append([
                InlineKeyboardButton(
                    subject_name,
                    callback_data=f"subject_{subject_id}"
                )
            ])

        await query.message.reply_text(
            "📚 Choose Subject:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # Choose Subject
    # ==========================
    elif data.startswith("subject_"):

        subject_id = int(data.replace("subject_", ""))

        context.user_data["subject_id"] = subject_id

        keyboard = [
            [
                InlineKeyboardButton(
                    "📚 Lectures",
                    callback_data=f"lectures_{subject_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎥 Records",
                    callback_data=f"records_{subject_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📝 Assignments",
                    callback_data=f"assignments_{subject_id}"
                )
            ],
        ]

        await query.message.reply_text(
            "Choose Material Type:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # ==========================
    # Lectures
    # ==========================
    elif data.startswith("lectures_"):

        subject_id = int(data.replace("lectures_", ""))

        items = get_materials_by_subject_and_type(
            subject_id,
            "lecture"
        )

        if not items:
            await query.message.reply_text(
                "No lectures available."
            )
            return

        keyboard = []

        for material_id, title in items:

            keyboard.append([
                InlineKeyboardButton(
                    title,
                    callback_data=f"material_{material_id}"
                )
            ])

        await query.message.reply_text(
            "📚 Choose Lecture:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # Records
    # ==========================
    elif data.startswith("records_"):

        subject_id = int(data.replace("records_", ""))

        items = get_materials_by_subject_and_type(
            subject_id,
            "record"
        )

        if not items:
            await query.message.reply_text(
                "No records available."
            )
            return

        keyboard = []

        for material_id, title in items:

            keyboard.append([
                InlineKeyboardButton(
                    title,
                    callback_data=f"material_{material_id}"
                )
            ])

        await query.message.reply_text(
            "🎥 Choose Record:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==========================
    # Assignments
    # ==========================
    elif data.startswith("assignments_"):

        subject_id = int(data.replace("assignments_", ""))

        items = get_materials_by_subject_and_type(
            subject_id,
            "assignment"
        )

        if not items:
            await query.message.reply_text(
                "No assignments available."
            )
            return

        keyboard = []

        for material_id, title in items:

            keyboard.append([
                InlineKeyboardButton(
                    title,
                    callback_data=f"material_{material_id}"
                )
            ])

        await query.message.reply_text(
            "📝 Choose Assignment:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==========================
# Open Material
# ==========================
    elif data.startswith("material_"):

     material_id = int(data.replace("material_", ""))

    material = get_material_by_id(material_id)

    if not material:
        await query.message.reply_text(
            "Material not found."
        )
        return

    material_type = material[2]
    title = material[3]
    file_id = material[4]

    if not file_id:
        await query.message.reply_text(
            "File not found."
        )
        return

    if material_type == "lecture":

        await query.message.reply_document(
            document=file_id,
            caption=title
        )

    elif material_type == "assignment":

        await query.message.reply_document(
            document=file_id,
            caption=title
        )

    elif material_type == "record":

        await query.message.reply_video(
            video=file_id,
            caption=title
        )