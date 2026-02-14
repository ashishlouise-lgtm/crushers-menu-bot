import os
import logging
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 1. Logging Setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. API Keys (Render Environment Variables se)
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 3. Gemini AI Configuration
genai.configure(api_key=GEMINI_KEY)
# "gemini-1.5-flash" sabse stable version hai jo logs ka 404 error fix karega
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Menu Markup Definition
async def get_menu_markup():
    keyboard = [
        [InlineKeyboardButton("🍔 Burgers & Snacks", callback_data='burgers'),
         InlineKeyboardButton("☕ Beverages", callback_data='coffee')],
        [InlineKeyboardButton("🍕 Pizza Specials", callback_data='pizza')],
        [InlineKeyboardButton("📍 Location & Contact", callback_data='contact')]
    ]
    return InlineKeyboardMarkup(keyboard)

# 5. Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = await get_menu_markup()
    welcome_text = (
        "👋 *Welcome to Crushers Cafe!*\n\n"
        "Main aapka AI assistant hoon. Neeche buttons use karein ya mujhse kuch bhi puchein:"
    )
    await update.message.reply_text(welcome_text, reply_markup=markup, parse_mode='Markdown')

# 6. Button Click (Callback) Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    DATA = {
        'burgers': "🍔 *BURGERS*\n🔹 Veg: ₹99\n🔹 Cheese: ₹149\n🔹 Paneer: ₹179",
        'coffee': "☕ *BEVERAGES*\n❄️ Cold Coffee: ₹120\n🥤 Oreo Shake: ₹160\n🔥 Hot Coffee: ₹90",
        'pizza': "🍕 *PIZZAS*\n🔸 Margherita: ₹199\n🔸 Veggie: ₹299\n🔸 Paneer: ₹349",
        'contact': "📍 *Uttarakhand, City Center*\n📞 +91 XXXXX XXXXX"
    }

    if query.data in DATA:
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data='main_menu')]])
        await query.edit_message_text(text=DATA[query.data], reply_markup=back_btn, parse_mode='Markdown')
    elif query.data == 'main_menu':
        markup = await get_menu_markup()
        await query.edit_message_text("Aap kya order karna chahenge?", reply_markup=markup)

# 7. AI Message Handler
async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # AI ko instruction dena ki wo cafe assistant hai
        prompt = f"You are the official AI assistant of Crushers Cafe in Uttarakhand. Answer this customer politely: {user_text}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        await update.message.reply_text("Maaf kijiye, main abhi busy hoon. Please menu buttons use karein.")

# 8. Main Application
def main():
    if not TOKEN:
        logging.error("BOT_TOKEN missing!")
        return
    
    # Conflict se bachne ke liye application builder
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat))
    
    logging.info("Bot is starting...")
    app.run_polling(drop_pending_updates=True) # Purani pending updates delete karega

if __name__ == '__main__':
    # Render aur Cron-job ke liye dummy server
    from threading import Thread
    import http.server
    import socketserver
    
    def run_server():
        port = int(os.environ.get("PORT", 8080))
        class MyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Crushers Cafe AI Bot is Live!")
        
        with socketserver.TCPServer(("", port), MyHandler) as httpd:
            httpd.serve_forever()
            
    Thread(target=run_server, daemon=True).start()
    main()
