import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# === अपनी जानकारी Render पर Environment Variables में डालना है ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7788642203"))

pending_reply_to = {}

def user_tag(u):
    handle = f"@{u.username}" if u.username else ""
    name = f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip()
    name = name or "Unknown"
    return f"{name} {handle}".strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id == ADMIN_ID:
        await update.message.reply_text("नमस्ते Admin! अब से यूज़र्स के मैसेज यहीं आएँगे।")
    else:
        await update.message.reply_text("नमस्ते! अपना संदेश लिखिए, Admin तक पहुँचा दिया जाएगा।")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "यह सपोर्ट बॉट है:\n"
        "- आपका संदेश Admin तक पहुँचता है।\n"
        "- Admin के जवाब आपको यहीं मिलेंगे।\n\n"
        "Admin के लिए:\n"
        "1) किसी संदेश के नीचे 'Reply' दबाएँ और अपना जवाब भेजें।\n"
        "2) या /reply <user_id> <message> कमांड इस्तेमाल करें।"
    )
    await update.message.reply_text(txt)

async def on_any_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if user and user.id == ADMIN_ID:
        target_user_id = pending_reply_to.get(ADMIN_ID)
        if target_user_id:
            await context.bot.copy_message(
                chat_id=target_user_id,
                from_chat_id=chat.id,
                message_id=msg.message_id
            )
            await msg.reply_text("✅ Reply भेज दिया गया।")
            pending_reply_to.pop(ADMIN_ID, None)
        return

    header = f"📩 From: {user_tag(user)}\n🆔 user_id: {user.id}"
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("↩️ Reply", callback_data=f"reply:{user.id}")
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=header)

    await context.bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=chat.id,
        message_id=msg.message_id,
        reply_markup=keyboard
    )

    await msg.reply_text("✅ आपका संदेश Admin तक पहुँच गया। जवाब यहीं मिलेगा।")

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    await query.answer()

    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        await query.edit_message_reply_markup(None)
        return

    if data.startswith("reply:"):
        try:
            user_id = int(data.split(":", 1)[1])
            pending_reply_to[ADMIN_ID] = user_id
            await query.message.reply_text(
                f"✍️ अब अपना जवाब टाइप करें (भेजते ही user_id {user_id} को जाएगा)।"
            )
        except:
            await query.message.reply_text("❌ Reply सेट करने में दिक्कत हुई।")

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("उपयोग: /reply <user_id> <message>")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ user_id numeric होना चाहिए।")
        return

    text = " ".join(context.args[1:])
    if not text.strip():
        await update.message.reply_text("❌ खाली संदेश नहीं भेज सकते।")
        return

    await context.bot.send_message(chat_id=user_id, text=f"👮 Admin:\n{text}")
    await update.message.reply_text("✅ Reply भेज दिया गया।")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN सेट करें!")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("reply", reply_cmd))

    application.add_handler(CallbackQueryHandler(on_callback))
    application.add_handler(MessageHandler(filters.ALL, on_any_user_message))

    print("Bot is running…")
    application.run_polling()

if __name__ == "__main__":
    main()
