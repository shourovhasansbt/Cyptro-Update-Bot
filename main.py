import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TOKEN = "8506634606:AAFygxDNyAm0z7djZ-jtJ1l-w8qWLU3heA4"
CHANNEL_USERNAME = "@shourovtech883" 

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
    """Returns the crypto list keyboard with a Join button at the bottom"""
    keyboard = []
    row = []
    
    # Add Coin Buttons
    for symbol, name in COINS.items():
        row.append(InlineKeyboardButton(name, callback_data=symbol))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    # Add simple "Join Channel" button (Link only, no verification)
    channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    keyboard.append([InlineKeyboardButton("📢 Join Official Channel", url=channel_link)])
    
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the bot directly without verification"""
    await update.message.reply_text(
        "📊 **Crypto Market Tracker (Binance)**\n\n"
        "Join our channel for updates: @shourovtech883\n"
        "Select a coin below for instant updates:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks"""
    query = update.callback_query
    
    # Fetch and Show Crypto Data
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
