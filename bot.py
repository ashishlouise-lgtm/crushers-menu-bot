import os
import http.server
import socketserver
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- RENDER PORT FIX ---
def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

# --- CAFE DATA ---
MENU = {
    "burgers": {
        "title": "🍔 BURGERS MENU",
        "items": {"Veg Burger": 99, "Cheese Burger": 149, "Paneer Burger": 179}
    },
    "pizza": {
        "title": "🍕 PIZZA SPECIALS",
        "items": {"Margherita": 199, "Farmhouse": 299, "Peppy Paneer": 349}
    },
    "coffee": {
        "title": "☕ BEVERAGES",
        "items": {"Cold Coffee": 120, "Oreo Shake": 160, "Hot Coffee": 90}
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')],
        [InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza')],
        [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')]
    ]
    await update.message.reply_text("Welcome to *Crushers Cafe*!\nCategory chuniye:", 
                                  reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith('cat_'):
        cat_key = data.split('_')[1]
        cat_info = MENU[cat_key]
        text = f"*{cat_info['title']}*\n\n"
        keyboard = []
        for item, price in cat_info["items"].items():
            text += f"🔹 {item}: ₹{price}\n"
            keyboard.append([InlineKeyboardButton(f"Book {item}", callback_data=f"book_{item}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='main_menu')])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith('book_'):
        item = data.split('_')[1]
        await query.edit_message_text(f"✅ *Order Received!*\n\nAapne {item} book kiya hai.", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='main_menu')]]),
                                      parse_mode='Markdown')

    elif data == 'main_menu':
        keyboard = [[InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')], 
                    [InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza')],
                    [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')]]
        await query.edit_message_text("Category chuniye:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    Thread(target=run_health_server, daemon=True).start()
    main()
