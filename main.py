import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Get Token from Environment Variable
TOKEN = os.getenv("BOT_TOKEN")

# Top 10 Coins Mapping
COINS = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "tether": "Tether (USDT)",
    "binancecoin": "BNB (BNB)",
    "solana": "Solana (SOL)",
    "ripple": "XRP (XRP)",
    "usd-coin": "USDC (USDC)",
    "cardano": "Cardano (ADA)",
    "dogecoin": "Dogecoin (DOGE)",
    "tron": "Tron (TRX)"
}

def get_crypto_data(coin_id):
    """Fetches data from CoinGecko API with Headers to avoid blocking"""
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}"
    
    # Fake browser header to avoid blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "⚠️ API Busy. Please wait 1 minute and try again."
            
        data = response.json()[0]
        
        current_price = data['current_price']
        high_24h = data['high_24h']
        low_24h = data['low_24h']
        change_24h = data['price_change_percentage_24h']
        
        trend = "🟢 UP" if change_24h > 0 else "🔴 DOWN"
        
        return (
            f"💰 **{data['name']} ({data['symbol'].upper()})**\n\n"
            f"💵 **Price:** ${current_price:,}\n"
            f"📈 **24h High:** ${high_24h:,}\n"
            f"📉 **24h Low:** ${low_24h:,}\n"
            f"📊 **Change:** {change_24h:.2f}%\n"
            f"🚀 **Trend:** {trend}"
        )
    except Exception as e:
        print(f"Error: {e}") # Log error for debugging
        return "❌ Error fetching data. CoinGecko API might be busy."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the menu"""
    keyboard = []
    row = []
    for coin_id, coin_name in COINS.items():
        row.append(InlineKeyboardButton(coin_name, callback_data=coin_id))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 **Crypto Market Tracker**\nSelect a coin to see real-time updates:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks with Anti-Crash Logic"""
    query = update.callback_query
    
    # Show "Loading..." toast at the top
    await query.answer("Fetching data...") 
    
    coin_id = query.data
    crypto_info = get_crypto_data(coin_id)
    
    keyboard = []
    row = []
    for cid, cname in COINS.items():
        row.append(InlineKeyboardButton(cname, callback_data=cid))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Try to edit message, ignore error if content is same
    try:
        await query.edit_message_text(
            text=crypto_info,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except error.BadRequest as e:
        if "Message is not modified" in str(e):
            # Do nothing if message is same (prevents crash)
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
