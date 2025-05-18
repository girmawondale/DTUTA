from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes
)
from flask import Flask
from threading import Thread

# === Telegram Bot Config ===
BOT_TOKEN = "8123619470:AAHrkX0FGTUloy8v3EJT3P334U86F6bwG_I"  # Your bot token
GROUP_ID = -1002547554880          # Your group ID
ADMIN_IDS = [697616131]            # List of admin user IDs

# === Flask app to keep Replit awake ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === Telegram Bot Handlers ===
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("⚠️ Use it like:\n/submit Your message here")
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve|{user.first_name}|{user.last_name or ''}|{text}"),
            InlineKeyboardButton("❌ Reject", callback_data="reject")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"📝 New submission from @{user.username or user.first_name}:\n\n{text}",
            reply_markup=reply_markup
        )

    await update.message.reply_text("✅ Sent to admins for approval.")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in ADMIN_IDS:
        await query.answer("⛔ Not authorized.", show_alert=True)
        return

    data = query.data

    if data.startswith("approve|"):
        _, first_name, last_name, submitted_text = data.split("|", 3)
        full_name = f"{first_name} {last_name}".strip()

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📢 Approved submission from {full_name}:\n\n{submitted_text}"
        )
        await query.edit_message_text("✅ Approved and posted.")
    elif data == "reject":
        await query.edit_message_text("❌ Submission rejected.")

# === Main function to run bot and flask concurrently ===
def main():
    # Start Flask app in a new thread
    Thread(target=run_flask).start()

    # Start Telegram bot
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("submit", submit))
    app_bot.add_handler(CallbackQueryHandler(handle_buttons))

    print("🤖 Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
