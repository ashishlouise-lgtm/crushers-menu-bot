import os
import logging
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables se keys lena
TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini setup
genai.configure(api_key=API_KEY)
# Yahan model ka naam ekdam sahi format mein rakha hai
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. Cafe Menu Buttons Definition
async def get_menu_markup():
    keyboard = [
        [InlineKeyboardButton("🍔 Burgers & Snacks", callback_data='burgers'),
         InlineKeyboardButton("☕ Beverages", callback_data='coffee')],
        [InlineKeyboardButton("🍕 Pizza Specials", callback_data='pizza')],
        [InlineKeyboardButton("📍 Location & Contact", callback_data='contact')]
    ]
    return InlineKeyboardMarkup(keyboard)

# 2. Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = await get_menu_markup()
    text = "👋 *Welcome to Crushers Cafe!*\n\nNeeche diye gaye buttons se menu check karein ya mujhse kuch bhi puchein:"
    await update.message.reply_text(text, reply_markup=markup, parse_mode='Markdown')

# 3. Button Click Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Menu Data
    DATA = {
        'burgers': "🍔 *BURGERS*\n🔹 Veg: ₹99\n🔹 Cheese: ₹149\n🔹 Paneer: ₹179",
        'coffee': "☕ *BEVERAGES*\n❄️ Cold Coffee: ₹120\n🥤 Oreo Shake: ₹160\n🔥 Hot Coffee: ₹90",
        'pizza': "🍕 *PIZZAS*\n🔸 Margherita: ₹199\n🔸 Veggie: ₹299\n🔸 Paneer: ₹349",
        'contact': "📍 *Uttarakhand, City Center*\n📞 +91 XXXXX XXXXX"
    }

    if query.data in DATA:
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]])
        await query.edit_message_text(text=DATA[query.data], reply_markup=back_btn, parse_mode='Markdown')
    elif query.data == 'main_menu':
        markup = await get_menu_markup()
        await query.edit_message_text("Aap kya order karna chahenge?", reply_markup=markup)

# 4. AI Chat Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Prompt ko clean rakha hai taaki model confused na ho
        prompt = f"You are a helpful assistant for Crushers Cafe. Answer the user politely: {user_text}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        # Agar AI key ya model mein dikkat hai toh hi ye message aayega
        await update.message.reply_text("Maaf kijiye, main abhi busy hoon. Please menu buttons use karein.")

def main():
    if not TOKEN:
        logging.error("BOT_TOKEN is missing!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("Bot is polling...")
    app.run_polling()

if __name__ == '__main__':
    from threading import Thread
    import http.server
    import socketserver
    
    # Dummy server for Render health checks and Cron-job
    def run_server():
        port = int(os.environ.get("PORT", 8080))
        class MyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"AI Bot is Active!")
        
        with socketserver.TCPServer(("", port), MyHandler) as httpd:
            httpd.serve_forever()
            
    Thread(target=run_server, daemon=True).start()
    main()
