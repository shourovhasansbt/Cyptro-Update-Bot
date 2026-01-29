import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TOKEN = "8506634606:AAFygxDNyAm0z7djZ-jtJ1l-w8qWLU3heA4"
CHANNEL_USERNAME = "@shourovtech883"  # Your Channel Link

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Coin Mapping
COINS = {
    "BTCUSDT": "Bitcoin (BTC)",
    "ETHUSDT": "Ethereum (ETH)",
    "BNBUSDT": "BNB (BNB)",
    "SOLUSDT": "Solana (SOL)",
    "XRPUSDT": "XRP (XRP)",
    "ADAUSDT": "Cardano (ADA)",
    "DOGEUSDT": "Dogecoin (DOGE)",
    "TRXUSDT": "Tron (TRX)",
    "USDCUSDT": "USDC (USDC)", 
    "FDUSDUSDT": "Tether (USDT)" 
}

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user is a member of the channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # Check if status is member, creator, or admin
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            return True
        return False
    except error.BadRequest:
        print(f"Error checking channel: {CHANNEL_USERNAME}")
        return False
    except Exception as e:
        print(f"Subscription Check Error: {e}")
        return False

def get_join_keyboard():
    """Returns the Join Channel button."""
    # Removes the '@' for the URL link
    channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel to Use Bot", url=channel_link)],
        [InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_crypto_data(symbol):
    """Fetches data from Binance API"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return "⚠️ Error fetching data from Binance."
            
        data = response.json()
        
        price = float(data['lastPrice'])
        high = float(data['highPrice'])
        low = float(data['lowPrice'])
        change = float(data['priceChangePercent'])
        
        trend = "🟢 UP" if change > 0 else "🔴 DOWN"
        name = COINS.get(symbol, symbol)

        return (
            f"💰 **{name}**\n\n"
            f"💵 **Price:** ${price:,.4f}\n"
            f"📈 **24h High:** ${high:,.4f}\n"
            f"📉 **24h Low:** ${low:,.4f}\n"
            f"📊 **Change:** {change:.2f}%\n"
            f"🚀 **Trend:** {trend}"
        )
    except Exception as e:
        print(f"Error: {e}")
        return "❌ Error fetching data. Please try again."

def get_main_menu():
    """Returns the crypto list keyboard"""
    keyboard = []
    row = []
    for symbol, name in COINS.items():
        row.append(InlineKeyboardButton(name, callback_data=symbol))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the bot with subscription check"""
    user_id = update.effective_user.id
    
    # 1. Check Subscription
    if not await check_subscription(user_id, context):
        await update.message.reply_text(
            "🚫 **Access Denied!**\n\nYou must join our Telegram channel to use this bot.",
            reply_markup=get_join_keyboard(),
            parse_mode="Markdown"
        )
        return

    # 2. If subscribed, show menu
    await update.message.reply_text(
        "📊 **Crypto Market Tracker (Binance)**\nSelect a coin below for instant updates:",
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
                "📊 **Crypto Market Tracker (Binance)**\nSelect a coin below for instant updates:",
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
            "🚫 **Access Denied!**\n\nYou must join our Telegram channel to use this bot.",
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

if __name__ == "__main__":
    main()
