    
import os
import logging
import requests
import json
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Keys
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# Yahan apna Google Apps Script URL dalein
SHEET_URL = "YOUR_GOOGLE_WEB_APP_URL_HERE"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Menu Data with Prices
MENU_DATA = {
    'pizza': {"Margherita": 199, "Veggie": 299, "Paneer": 349},
    'burgers': {"Veg Burger": 99, "Cheese Burger": 149, "Paneer Burger": 179},
    'coffee': {"Cold Coffee": 120, "Oreo Shake": 160, "Hot Coffee": 90}
}

# 1. Main Menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza'),
         InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')],
        [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')],
        [InlineKeyboardButton("🛒 View Cart / Checkout", callback_data='view_cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome to *Crushers Cafe*!\nChunye aap kya khana chahenge:", 
                                  reply_markup=reply_markup, parse_mode='Markdown')

# 2. Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # Category dikhana
    if data.startswith('cat_'):
        cat = data.split('_')[1]
        keyboard = []
        for item, price in MENU_DATA[cat].items():
            keyboard.append([InlineKeyboardButton(f"{item} - ₹{price}", callback_data=f"add_{item}_{price}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data='main_menu')])
        await query.edit_message_text(f"Select your {cat}:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Item Cart mein add karna
    elif data.startswith('add_'):
        _, name, price = data.split('_')
        if 'cart' not in context.user_data:
            context.user_data['cart'] = []
        
        context.user_data['cart'].append({"item": name, "price": int(price)})
        
        keyboard = [[InlineKeyboardButton("➕ Add More", callback_data='main_menu')],
                    [InlineKeyboardButton("🏁 Checkout", callback_data='view_cart')]]
        await query.edit_message_text(f"✅ {name} add ho gaya!", reply_markup=InlineKeyboardMarkup(keyboard))

    # Cart aur Checkout
    elif data == 'view_cart':
        cart = context.user_data.get('cart', [])
        if not cart:
            await query.edit_message_text("Cart khali hai!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Menu", callback_data='main_menu')]]))
            return
        
        summary = "\n".join([f"• {i['item']} (₹{i['price']})" for i in cart])
        total = sum(i['price'] for i in cart)
        text = f"🛒 *Your Order:*\n\n{summary}\n\n*Total: ₹{total}*\n\nConfirm karein?"
        
        keyboard = [[InlineKeyboardButton("🔥 Confirm Order", callback_data='confirm')],
                    [InlineKeyboardButton("🗑️ Clear", callback_data='main_menu')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    # Google Sheet mein save karna
    elif data == 'confirm':
        cart = context.user_data.get('cart', [])
        total = sum(i['price'] for i in cart)
        items_str = ", ".join([i['item'] for i in cart])
        user_name = query.from_user.full_name

        # Sending to Google Sheet
        payload = {"name": user_name, "items": items_str, "total": total}
        try:
            requests.post(SHEET_URL, data=json.dumps(payload))
            await query.edit_message_text(f"🎉 Order Place ho gaya!\nTotal: ₹{total}\nSheet mein entry ho chuki hai.")
        except:
            await query.edit_message_text("❌ Error: Sheet connect nahi ho payi.")
        
        context.user_data['cart'] = []

    elif data == 'main_menu':
        keyboard = [[InlineKeyboardButton("🍕 Pizzas", callback_data='cat_pizza'), InlineKeyboardButton("🍔 Burgers", callback_data='cat_burgers')],
                    [InlineKeyboardButton("☕ Beverages", callback_data='cat_coffee')],
                    [InlineKeyboardButton("🛒 View Cart", callback_data='view_cart')]]
        await query.edit_message_text("Kya mangwayenge?", reply_markup=InlineKeyboardMarkup(keyboard))

# 3. AI Chat
async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = model.generate_content(f"You are the AI of Crushers Cafe. Answer briefly: {update.message.text}")
        await update.message.reply_text(response.text)
    except:
        await update.message.reply_text("Main abhi busy hoon, menu use karein.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # (Server code for Render health check yahan purana wala hi rahega)
    main()
