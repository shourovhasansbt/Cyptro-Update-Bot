import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ---------------------------------------------------------
# কনফিগারেশন (সরাসরি টোকেন বসানো হয়েছে)
# ---------------------------------------------------------
TOKEN = "8506634606:AAFygxDNyAm0z7djZ-jtJ1l-w8qWLU3heA4"

# লগিং সেটআপ (ত্রুটি দেখার জন্য)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# কয়েন ম্যাপিং
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
    """Binance API থেকে ডাটা নিয়ে আসে"""
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return "⚠️ Binance থেকে ডাটা পাওয়া যাচ্ছে না।"
            
        data = response.json()
        
        # ডাটা প্রসেসিং
        price = float(data['lastPrice'])
        high = float(data['highPrice'])
        low = float(data['lowPrice'])
        change = float(data['priceChangePercent'])
        
        trend = "🟢 UP" if change > 0 else "🔴 DOWN"
        
        # নাম বের করা
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
        return "❌ এরর! দয়া করে আবার চেষ্টা করুন।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """মেনু সেন্ড করে"""
    keyboard = []
    row = []
    for symbol, name in COINS.items():
        row.append(InlineKeyboardButton(name, callback_data=symbol))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    # যদি শেষ লাইনে একটা বাটন বাকি থাকে
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 **Crypto Market Tracker (Binance)**\nনিচে যেকোনো একটি কয়েন সিলেক্ট করুন:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বাটন ক্লিক হ্যান্ডেল করে"""
    query = update.callback_query
    
    # লোডিং টোস্ট দেখাবে
    await query.answer("ডাটা লোড হচ্ছে...") 
    
    symbol = query.data
    crypto_info = get_crypto_data(symbol)
    
    # কিবোর্ড আবার তৈরি করা (যেন হারিয়ে না যায়)
    keyboard = []
    row = []
    for sym, name in COINS.items():
        row.append(InlineKeyboardButton(name, callback_data=sym))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=crypto_info,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except error.BadRequest as e:
        if "Message is not modified" in str(e):
            pass # ডাটা একই থাকলে ক্র্যাশ করবে না
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
