
   
import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

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
    text = "👋 *Welcome to Crushers Cafe!*\n\nNeeche diye gaye buttons se menu check karein:"
    await update.message.reply_text(text, reply_markup=markup, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()
    if any(word in user_msg for word in ["hi", "hello", "hey", "menu"]):
        markup = await get_menu_markup()
        await update.message.reply_text("Welcome back! Menu hazir hai:", reply_markup=markup)
    else:
        await update.message.reply_text("Please click /start or say 'Hi' to see the menu.")

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
    if not TOKEN:
        print("Error: BOT_TOKEN not found!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    # Render port error se bachne ke liye
    os.system(f"python3 -m http.server {os.environ.get('PORT', 8080)} &")
    main()
