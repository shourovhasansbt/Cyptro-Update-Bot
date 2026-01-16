import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Get Token from Environment Variable (For Security)
TOKEN = os.getenv("BOT_TOKEN")

# Top 10 Coins Mapping (Button Label -> CoinGecko ID)
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
    """Fetches data from CoinGecko API"""
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={coin_id}"
    try:
        response = requests.get(url)
        data = response.json()[0]
        
        current_price = data['current_price']
        high_24h = data['high_24h']
        low_24h = data['low_24h']
        change_24h = data['price_change_percentage_24h']
        
        # Determine Up/Down Icon
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
        return "❌ Error fetching data. Please try again later."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the menu with 10 buttons"""
    keyboard = []
    row = []
    
    # Create buttons in rows of 2
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
    """Handles button clicks and updates the text"""
    query = update.callback_query
    await query.answer() # Close the loading animation
    
    coin_id = query.data
    crypto_info = get_crypto_data(coin_id)
    
    # Keep the buttons so user can click others
    keyboard = []
    row = []
    for cid, cname in COINS.items():
        row.append(InlineKeyboardButton(cname, callback_data=cid))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Edit the message with new data
    await query.edit_message_text(
        text=crypto_info,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    """Start the bot"""
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

