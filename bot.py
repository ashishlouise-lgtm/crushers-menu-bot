  
    import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. Menu Data (Category wise Items & Prices)
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

# 2. /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')],
        [InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza')],
        [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to *Crushers Cafe*! Category chuniye:", 
                                  reply_markup=reply_markup, parse_mode='Markdown')

# 3. Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # Category click hone par Prices dikhana
    if data.startswith('cat_'):
        cat_key = data.split('_')[1]
        cat_info = MENU[cat_key]
        
        text = f"*{cat_info['title']}*\n\n"
        keyboard = []
        
        for item, price in cat_info["items"].items():
            text += f"🔹 {item}: ₹{price}\n"
            # Direct order button (Cart ke bina)
            keyboard.append([InlineKeyboardButton(f"Book {item}", callback_data=f"book_{item}_{price}")])
            
        keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data='main_menu')])
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # Direct Booking confirmation
    elif data.startswith('book_'):
        _, item_name, price = data.split('_')
        # Yahan aap apna Google Sheet wala URL ya Admin message logic daal sakte hain
        confirm_text = f"✅ *Order Received!*\n\nItem: {item_name}\nPrice: ₹{price}\n\nHum aapka order jaldi tyar karenge!"
        
        keyboard = [[InlineKeyboardButton("🔙 Order Something Else", callback_data='main_menu')]]
        await query.edit_message_text(text=confirm_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'main_menu':
        keyboard = [
            [InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')],
            [InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza')],
            [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')]
        ]
        await query.edit_message_text("Category chuniye:", reply_markup=InlineKeyboardMarkup(keyboard))

# 4. Main Function
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Cafe Bot is live...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
