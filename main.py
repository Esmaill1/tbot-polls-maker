# Import necessary modules
from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PollHandler
from PIL import Image
from reportlab.pdfgen import canvas
import os

# Replace with your bot token from BotFather
TOKEN = '7923351343:AAHW1tX2Cl5d2SK3KTkihaltmBLpCeOqNSg'  # Replace this with your actual token

# Variable to keep the bot alive (if JobQueue is available)
keep_alive_counter = 0

# Start command handler with language selection
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to choose a language."""
    context.user_data.clear()
    await update.message.reply_text(
        "مرحباً! Welcome! Please choose a language:\n"
        "/arabic - العربية\n"
        "/english - English"
    )

# Language selection handlers
async def set_arabic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set language to Arabic and show service menu."""
    context.user_data['language'] = 'arabic'
    await update.message.reply_text(
        "تم اختيار اللغة العربية!\n"
        "اختر خدمة:\n"
        "/image2pdf - تحويل الصور إلى PDF\n"
        "/poll - إنشاء استطلاعات"
    )

async def set_english(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set language to English and show service menu."""
    context.user_data['language'] = 'english'
    await update.message.reply_text(
        "English selected!\n"
        "Choose a service:\n"
        "/image2pdf - Convert images to PDF\n"
        "/poll - Create quiz polls"
    )

# --- Image to PDF Service ---
async def image2pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the image-to-PDF service with language-specific message."""
    if 'language' not in context.user_data:
        await update.message.reply_text("Please choose a language first with /start!")
        return
    context.user_data['service'] = 'image2pdf'
    context.user_data['images'] = []
    if context.user_data['language'] == 'arabic':
        await update.message.reply_text(
            "تم تفعيل خدمة تحويل الصور إلى PDF!\n"
            "أرسل لي عدة صور، ثم استخدم /convert لتحويلها إلى PDF.\n"
            "استخدم /cancel للإلغاء."
        )
    else:  # English
        await update.message.reply_text(
            "Image-to-PDF service activated!\n"
            "Send me multiple images, then use /convert to get them as a single PDF.\n"
            "Use /cancel to stop."
        )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store received images if image2pdf service is active."""
    if context.user_data.get('service') != 'image2pdf':
        return
    if 'language' not in context.user_data:
        await update.message.reply_text("Please choose a language first with /start!")
        return

    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"temp_image_{update.message.message_id}_{update.message.chat_id}.jpg"
    await photo_file.download_to_drive(photo_path)
    context.user_data['images'].append(photo_path)
    if context.user_data['language'] == 'arabic':
        await update.message.reply_text("تم استلام الصورة! أرسل المزيد أو استخدم /convert للانتهاء.")
    else:  # English
        await update.message.reply_text("Image received! Send more or use /convert to finish.")

async def convert_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert stored images to a PDF with language-specific messages."""
    if 'language' not in context.user_data:
        await update.message.reply_text("Please choose a language first with /start!")
        return
    if context.user_data.get('service') != 'image2pdf':
        await update.message.reply_text("يرجى تفعيل /image2pdf أولاً!" if context.user_data.get('language') == 'arabic' else "Please activate /image2pdf first!")
        return

    if 'images' not in context.user_data or not context.user_data['images']:
        await update.message.reply_text(
            "لم يتم استلام أي صور بعد! أرسل بعض الصور أولاً." if context.user_data['language'] == 'arabic' else 
            "No images received yet! Send some images first."
        )
        return

    pdf_path = f"converted_{update.message.chat_id}.pdf"
    await update.message.reply_text(
        "جارٍ تحويل الصور إلى PDF..." if context.user_data['language'] == 'arabic' else 
        "Converting your images to PDF..."
    )

    try:
        c = canvas.Canvas(pdf_path)
        for photo_path in context.user_data['images']:
            image = Image.open(photo_path)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            width, height = image.size
            c.setPageSize((width, height))
            c.drawImage(photo_path, 0, 0, width, height)
            c.showPage()
        c.save()

        with open(pdf_path, 'rb') as pdf_file:
            await update.message.reply_document(document=pdf_file, filename="converted_images.pdf")
        await update.message.reply_text(
            "ها هو ملف PDF الخاص بك مع جميع الصور!" if context.user_data['language'] == 'arabic' else 
            "Here’s your PDF with all images!"
        )

    except Exception as e:
        await update.message.reply_text(f"..... {str(e)}" if context.user_data['language'] == 'arabic' else f"....")

    finally:
        for photo_path in context.user_data['images']:
            if os.path.exists(photo_path):
                os.remove(photo_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        context.user_data['images'] = []

# --- Poll Service ---
async def poll_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the poll creation service with language-specific message (Arabic from original)."""
    if 'language' not in context.user_data:
        await update.message.reply_text("Please choose a language first with /start!")
        return
    context.user_data['service'] = 'poll'
    try:
        with open('ff.jpg', 'rb') as image_file:
            caption = (
    "اهلاً! تقدر تبعتلي اسئلة بنفس الصيغه دي 👇👇\n\n"
    "```\n"
    "[Your question?]\n"
    "a [Option 1]\n"
    "b [Option 2]\n"
    "c [Option 3]\n"
    "d [Option 4]\n"
    "Correct answer is: [correct option]\n"
    "```\n\n"
    "⚡ خد الصيغه دي واستخدمها مع ChatGPT عشان تطلع الأسئلة بالشكل ده.\n"
    "⚡ تقدر تبعت كذا سؤال مع بعض في نفس الرسالة، بس خلي فيه (سطر واحد فقط) فاضي بين كل سؤال والتاني. (ㆆ_ㆆ)\n\n"
    "✅ **ملاحظات هامة:**\n"
    "- احرص على أن تكون الخيارات مرتبة كما هو موضح (a, b, c, d).\n"
    "- اكتب **\"Correct answer is:\"** ثم الحرف الصحيح فقط (a, b, c أو d).\n"
    "- ضع **سطرًا فارغًا** بين كل سؤالين لتفادي الأخطاء."
)

            ) if context.user_data['language'] == 'arabic' else (
                "Poll service activated\\!\n"
                "Send questions in this format:\n\n"
                "```\n"
                "[Your question?]\n"
                "a [Option 1]\n"
                "b [Option 2]\n"
                "c [Option 3]\n"
                "d [Option 4]\n"
                "Correct answer is: [correct option]\n"
                "```\n\n"
                "Send multiple questions with one empty line between them\\."
            )
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=image_file,
                caption=caption,
                parse_mode="MarkdownV2"
            )
    except FileNotFoundError:
        await update.message.reply_text(
            "اهلاً\\! تقدر تبعتلي اسئلة بنفس الصيغه دي:\n\n"
            "```\n"
            "\$$ Your question\\?\ $$\n"
            "a \$$ Option 1\ $$\n"
            "b \$$ Option 2\ $$\n"
            "c \$$ Option 3\ $$\n"
            "d \$$ Option 4\ $$\n"
            "Correct answer is\\: \$$ correct option\ $$\n"
            "```\n\n"
            "(الصورة غير موجودة، تأكد من وجود 'ff.jpg' إذا كنت تريد الصورة المثال\\.)" if context.user_data['language'] == 'arabic' else 
            "Poll service activated\\! Send questions in the format above\\.\n"
            "(Image not found, please ensure 'ff.jpg' exists if you want the example image\\.)",
            parse_mode="MarkdownV2"
        )

async def create_polls(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create polls if poll service is active."""
    if context.user_data.get('service') != 'poll':
        return
    if 'language' not in context.user_data:
        await update.message.reply_text("Please choose a language first with /start!")
        return

    text = update.message.text
    questions_raw = text.strip().split("\n\n")

    for question_raw in questions_raw[:20]:
        lines = question_raw.split("\n")
        question = lines[0]
        options = [line.split(" ", 1)[1] for line in lines[1:5] if line[0].lower() in "abcd" and " " in line]
        correct_answer_line = next((line for line in lines if line.lower().startswith("correct answer is:")), None)
        correct_answer = correct_answer_line.split(":")[1].strip().lower() if correct_answer_line else None
        correct_answer_index = "abcd".index(correct_answer) if correct_answer and correct_answer in "abcd" else None

        if question and len(options) >= 2 and correct_answer_index is not None:
            await context.bot.send_poll(
                chat_id=update.effective_chat.id,
                question=question,
                options=options,
                type=Poll.QUIZ,
                correct_option_id=correct_answer_index,
                is_anonymous=True
            )
        else:
            await update.message.reply_text(
                "يرجى تقديم تنسيق صحيح للاستطلاع. تحقق من المثال." if context.user_data['language'] == 'arabic' else 
                "Invalid format for a poll. Check the example."
            )

async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle poll answers with language-specific response."""
    if context.user_data.get('service') == 'poll' and 'language' in context.user_data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="شكراً للإجابة!" if context.user_data['language'] == 'arabic' else "Thank you for answering!"
        )

# Cancel command to reset service
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel the current service with language-specific message."""
    if 'language' not in context.user_data:
        await update.message.reply_text("Please choose a language first with /start!")
        return
    context.user_data.clear()
    await update.message.reply_text(
        "تم إلغاء الخدمة. استخدم /start للاختيار مرة أخرى." if context.user_data['language'] == 'arabic' else 
        "Service canceled. Use /start to choose again."
    )

# Keep-alive task (optional)
async def keep_alive(context: ContextTypes.DEFAULT_TYPE) -> None:
    global keep_alive_counter
    keep_alive_counter += 1

# Main function
def main() -> None:
    """Start the bot."""
    app = Application.builder().token(TOKEN).build()

    # Add keep-alive job if JobQueue is available
    if app.job_queue is not None:
        app.job_queue.run_repeating(keep_alive, interval=7, first=0)
        print("JobQueue activated for keep-alive.")
    else:
        print("JobQueue not available. Running without keep-alive.")

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("arabic", set_arabic))
    app.add_handler(CommandHandler("english", set_english))
    app.add_handler(CommandHandler("image2pdf", image2pdf_start))
    app.add_handler(CommandHandler("poll", poll_start))
    app.add_handler(CommandHandler("convert", convert_to_pdf))
    app.add_handler(CommandHandler("cancel", cancel))

    # Message and poll handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_polls))
    app.add_handler(PollHandler(poll_answer))

    # Start the bot
    print('Bot is running...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
