from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, PollHandler, filters, ContextTypes

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
BOT_TOKEN = '7923351343:AAHW1tX2Cl5d2SK3KTkihaltmBLpCeOqNSg'

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! I'm your quiz bot. To create polls, please send me your questions formatted like this:\n\n"
        "❓ Your question?\n"
        "a) Option 1\n"
        "b) Option 2\n"
        "c) Option 3\n"
        "d) Option 4\n"
        "✅ Correct answer is: c\n\n"
        "🔄 Repeat for each question, and I can handle up to 20 questions at once!\n"
        " Remamber to add an empty line between every quistion and the next one "
    )

# Poll creation handler
async def create_polls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Split the input into questions by double newlines
    questions_raw = text.strip().split("\n\n")

    for question_raw in questions_raw[:20]:  # Limit to 20 questions
        lines = question_raw.split("\n")
        
        # The first line is the question
        question = lines[0]
        
        # Extract options from lines starting with 'a ', 'b ', etc.
        options = [line.split(" ", 1)[1] for line in lines[1:5] if line[0].lower() in "abcd" and " " in line]

        # Extract the correct answer line
        correct_answer_line = next((line for line in lines if line.lower().startswith("correct answer is:")), None)
        correct_answer = correct_answer_line.split(":")[1].strip().lower() if correct_answer_line else None
        
        # Find the index of the correct answer based on the letter provided
        correct_answer_index = "abcd".index(correct_answer) if correct_answer and correct_answer in "abcd" else None

        # Check if we have a question, options, and a correct answer
        if question and len(options) >= 2 and correct_answer_index is not None:
            # Create the poll as a quiz
            poll_message = await context.bot.send_poll(
                chat_id=update.effective_chat.id,
                question=question,
                options=options,
                type=Poll.QUIZ,  # Set poll type to QUIZ
                correct_option_id=correct_answer_index,  # Set the correct answer
                is_anonymous=True
            )
            await update.message.reply_text("✅ Poll created successfully! Good luck to your participants! 🎉")
        else:
            await update.message.reply_text("⚠️ Oops! Please make sure each question has at least 2 options and a correct answer specified.")

# Poll answer handler to show the correct answer
async def poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll.id
    # Send a message to acknowledge the answer (customize if needed)
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="📝 Thank you for your answer! Stay tuned for the correct response.")

# Main function to set up the bot
def main():
    # Create the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Message handler to capture formatted poll requests
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_polls))
    
    # Poll answer handler to acknowledge the answer
    app.add_handler(PollHandler(poll_answer))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
