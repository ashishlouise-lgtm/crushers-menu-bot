
import os
import logging
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
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
model = genai.GenerativeModel('gemini-1.5-flash')
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # AI ko batana ki wo cafe assistant hai
        prompt = f"You are a helpful assistant for Crushers Cafe. If the user asks for menu, tell them to use buttons. User: {user_text}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        await update.message.reply_text("Maaf kijiye, main abhi busy hoon. Please menu buttons use karein.")

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    from threading import Thread
    import http.server
    import socketserver
    def run_server():
        port = int(os.environ.get("PORT", 8080))
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    Thread(target=run_server, daemon=True).start()
    main()
