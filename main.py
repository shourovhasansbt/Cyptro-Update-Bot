# 2. If subscribed, show menu
    await update.message.reply_text(
        "📊 Crypto Market Tracker (Binance)\nSelect a coin below for instant updates:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks"""
    query = update.callback_query
    user_id = query.from_user.id

    # 1. Handle "I Have Joined" button check
    if query.data == "check_join":
        if await check_subscription(user_id, context):
            await query.answer("✅ Welcome back!")
            await query.edit_message_text(
                "📊 Crypto Market Tracker (Binance)\nSelect a coin below for instant updates:",
                reply_markup=get_main_menu(),
                parse_mode="Markdown"
            )
        else:
            await query.answer("❌ You haven't joined yet!", show_alert=True)
        return

    # 2. Double Check Subscription (Security)
    if not await check_subscription(user_id, context):
        await query.answer("⚠️ Please join the channel first!", show_alert=True)
        await query.edit_message_text(
            "🚫 Access Denied!\n\nYou must join our Telegram channel to use this bot.",
            reply_markup=get_join_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    # 3. Fetch and Show Crypto Data
    await query.answer("Fetching live data...") 
    
    symbol = query.data
    crypto_info = get_crypto_data(symbol)
    
    try:
        await query.edit_message_text(
            text=crypto_info,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    except error.BadRequest as e:
        if "Message is not modified" in str(e):
            pass 
        else:
            print(f"Telegram Error: {e}")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN is missing!")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    application.run_polling()

if name == "main":
    main()
