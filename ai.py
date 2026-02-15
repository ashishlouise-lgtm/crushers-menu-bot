import os
import http.server
import socketserver
import google.generativeai as genai
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- RENDER PORT BINDING ---
def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# Apna Google Form Link yahan paste karein
FORM_LINK = "https://forms.gle/your_link_here" 

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- MENU DATA ---
MENU = {
    "burgers": {"title": "🍔 BURGERS", "items": {"Veg Burger": 99, "Cheese Burger": 149}},
    "pizza": {"title": "🍕 PIZZA", "items": {"Margherita": 199, "Farmhouse": 299}},
    "coffee": {"title": "☕ COFFEE", "items": {"Cold Coffee": 120, "Hot Coffee": 90}}
}

# --- COMMANDS & HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza'),
         InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')],
        [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')]
    ]
    text = "👋 *Welcome to Crushers Cafe!*\n\nMain aapka smart assistant hoon. Order karne ke liye niche buttons use karein ya mujhse menu ke baare mein kuch bhi puchein:"
    
    # Message ya Callback dono ko handle karne ke liye
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith('cat_'):
        cat = data.split('_')[1]
        info = MENU[cat]
        text = f"*{info['title']} MENU*\n\n"
        keyboard = []
        for item, price in info["items"].items():
            text += f"🔹 {item}: ₹{price}\n"
            keyboard.append([InlineKeyboardButton(f"Book {item}", callback_data=f"book_{item}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='main_menu')])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('book_'):
        item = data.split('_')[1]
        text = (
            f"✅ Aapne *{item}* chuna hai!\n\n"
            "Order confirm karne ke liye bas niche diye gaye link par apni details bhar dein:\n"
            f"🔗 [Confirm My Order]({FORM_LINK})"
        )
        keyboard = [[InlineKeyboardButton("🔙 Menu par wapas jayein", callback_data='main_menu')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'main_menu':
        await start(update, context)

# --- AI CHAT (Gemini) ---
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Waiter style response
        prompt = f"You are a friendly and helpful waiter at Crushers Cafe. Answer briefly in Hinglish: {user_text}"
        response = ai_model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception:
        await update.message.reply_text("Maaf kijiye, main abhi busy hoon. Please menu buttons use karein.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    
    # Conflict errors ko rokne ke liye drop_pending_updates
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    Thread(target=run_health_server, daemon=True).start()
    main()
