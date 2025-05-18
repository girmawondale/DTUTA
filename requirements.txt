from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler, ContextTypes, filters
)

# === Configuration ===
BOT_TOKEN = "8123619470:AAH6xn_qiCcnKMBzhf253ZIPIGYH-FNbZBI"  # Replace with your actual bot token
GROUP_ID = -1002547554880          # Replace with your Telegram group ID
ADMIN_IDS = [697616131]            # Replace with actual admin user IDs

# === Approve/Reject Buttons ===
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in ADMIN_IDS:
        await query.answer("⛔ Not authorized.", show_alert=True)
        return

    data = query.data

    if data.startswith("approve|"):
        _, full_name, submitted_text = data.split("|", 2)

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📢 Message from {full_name}:\n\n{submitted_text}"
        )
        await query.edit_message_text("✅ Approved and posted.")
    elif data == "reject":
        await query.edit_message_text("❌ Submission rejected.")

# === Handle Any Text Message ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not text:
        return

    # Get full name (first + last if available)
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve|{full_name}|{text}"),
            InlineKeyboardButton("❌ Reject", callback_data="reject")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"📝 New submission from {full_name}:\n\n{text}",
            reply_markup=reply_markup
        )

    await update.message.reply_text("✅ Sent to admins for approval.")

# === Run Bot ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("🤖 Bot is running...")
    app.run_polling()
