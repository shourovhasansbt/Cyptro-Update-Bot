import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Get Token from Environment Variable
TOKEN = os.getenv("8506634606:AAFygxDNyAm0z7djZ-jtJ1l-w8qWLU3heA4")

# Top 10 Coins Mapping (Button Label -> Binance Symbol)
# Note: Stablecoins (USDT/USDC) are compared against other stables for data
COINS = {
    "BTCUSDT": "Bitcoin (BTC)",
    "ETHUSDT": "Ethereum (ETH)",
    "BNBUSDT": "BNB (BNB)",
    "SOLUSDT": "Solana (SOL)",
    "XRPUSDT": "XRP (XRP)",
    "ADAUSDT": "Cardano (ADA)",
    "DOGEUSDT": "Dogecoin (DOGE)",
    "TRXUSDT": "Tron (TRX)",
    "USDCUSDT": "USDC (USDC)",  # USDC vs USDT
    "FDUSDUSDT": "Tether (USDT)" # USDT vs FDUSD (Stable vs Stable)
}

def get_crypto_data(symbol):
    """Fetches data from BINANCE API (No Key Required, Very Fast)"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return "⚠️ Error fetching data from Binance."
            
        data = response.json()
        
        # Binance gives strings, convert to float
        price = float(data['lastPrice'])
        high = float(data['highPrice'])
        low = float(data['lowPrice'])
        change = float(data['priceChangePercent'])
        
        trend = "🟢 UP" if change > 0 else "🔴 DOWN"
        
        # Formatting Name
        name = [v for k, v in COINS.items() if k == symbol][0]

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the menu"""
    keyboard = []
    row = []
    for symbol, name in COINS.items():
        row.append(InlineKeyboardButton(name, callback_data=symbol))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 **Crypto Market Tracker (Binance)**\nSelect a coin for instant update:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks"""
    query = update.callback_query
    
    # Show loading toast
    await query.answer("Fetching live data...") 
    
    symbol = query.data
    crypto_info = get_crypto_data(symbol)
    
    # Rebuild keyboard
    keyboard = []
    row = []
    for sym, name in COINS.items():
        row.append(InlineKeyboardButton(name, callback_data=sym))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=crypto_info,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except error.BadRequest as e:
        if "Message is not modified" in str(e):
            pass # Ignore crash if data is same
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
