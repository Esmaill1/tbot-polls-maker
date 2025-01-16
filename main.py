from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
BOT_TOKEN = '7923351343:AAHW1tX2Cl5d2SK3KTkihaltmBLpCeOqNSg'

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Send the image with the instructions as the caption
        with open('ff.jpg', 'rb') as image_file:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=image_file,
                caption=(
                    "اهلاً! تقدر تبعتلي اسئلة بنفس الصيغه دي 👇👇\n\n"
                    "[Your question?]\n"
                    "a [Option 1]\n"
                    "b [Option 2]\n"
                    "c [Option 3]\n"
                    "d [Option 4]\n"
                    "Correct answer is: [correct option]\n\n"
                    "وانا هحول الاسئلة لكويزات بسهولة!\n"
                    "⚡ خد الصيغه دي واستخدمها مع ChatGPT عشان تطلع الأسئلة بالشكل ده.\n"
                    "⚡ تقدر تبعت كذا سؤال مع بعض في نفس الرسالة، بس خلي فيه (سطر واحد فقط) فاضي بين كل سؤال والتاني. (ㆆ_ㆆ)"
                )
            )
    except Exception as e:
        await update.message.reply_text(f"Failed to send the image. Error: {str(e)}")

# Main function to set up the bot
def main():
    # Create the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
