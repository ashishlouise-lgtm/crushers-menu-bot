
   
import os
import logging
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Keys setup
TOKEN = os.getenv("BOT_TOKEN")
GEN_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini configuration
genai.configure(api_key=GEN_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def get_menu_markup():
    keyboard = [
        [InlineKeyboardButton("🍔 Burgers & Snacks", callback_data='burgers'),
         InlineKeyboardButton("☕ Beverages", callback_data='coffee')],
        [InlineKeyboardButton("🍕 Pizza Specials", callback_data='pizza')],
        [InlineKeyboardButton("📍 Location & Contact", callback_data='contact')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = await get_menu_markup()
    text = "👋 *Welcome to Crushers Cafe!*\n\nMain ek AI Bot hoon. Menu dekhein ya mujhse kuch bhi puchein!"
    await update.message.reply_text(text, reply_markup=markup, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    
    # Check if user wants menu
    if any(word in user_msg.lower() for word in ["hi", "hello", "menu", "hey"]):
        markup = await get_menu_markup()
        await update.message.reply_text("Welcome back! Menu hazir hai:", reply_markup=markup)
        return

    # AI Chat Response logic
    try:
        # AI ko context dena ki wo ek cafe assistant hai
        prompt = f"You are a friendly AI assistant for 'Crushers Cafe' in Uttarakhand. Keep answers short and professional. Customer asks: {user_msg}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        await update.message.reply_text("Maaf kijiye, main abhi busy hoon. Please menu check karein.")

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
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]])
        await query.edit_message_text(text=DATA[query.data], reply_markup=back_btn, parse_mode='Markdown')
    elif query.data == 'main_menu':
        markup = await get_menu_markup()
        await query.edit_message_text("Aap kya order karna chahenge?", reply_markup=markup)

def main():
    if not TOKEN or not GEN_API_KEY:
        print("Error: Tokens not found!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == '__main__':
    from threading import Thread
    import http.server
    import socketserver

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
