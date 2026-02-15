    import telebot
from telebot import types

TOKEN = "8153875279:AAGjqdhbiJrvZt58zQjWGc5EpweT6Bb1g6k"
ADMIN_ID =6494419797 apna telegram user id yaha daalo

bot = telebot.TeleBot(TOKEN)

# Cafe Menu Data (Category Wise)
menu = {
    "☕ Coffee": {
        "Espresso - ₹80": 80,
        "Cappuccino - ₹120": 120,
        "Latte - ₹150": 150
    },
    "🥤 Cold Drinks": {
        "Coca Cola - ₹50": 50,
        "Pepsi - ₹50": 50,
        "Cold Coffee - ₹140": 140
    },
    "🍔 Fast Food": {
        "Veg Burger - ₹90": 90,
        "Cheese Pizza - ₹200": 200,
        "Sandwich - ₹70": 70
    },
    "🍰 Desserts": {
        "Chocolate Cake - ₹160": 160,
        "Ice Cream - ₹100": 100,
        "Brownie - ₹120": 120
    }
}

user_orders = {}

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in menu.keys():
        markup.add(category)
    bot.send_message(message.chat.id, "☕ Welcome to Aashish Cafe!\nChoose Category:", reply_markup=markup)

# Category Click
@bot.message_handler(func=lambda message: message.text in menu.keys())
def show_items(message):
    category = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    for item in menu[category].keys():
        markup.add(item)
    
    markup.add("🔙 Back")
    bot.send_message(message.chat.id, f"📋 {category} Menu:", reply_markup=markup)

# Item Click
@bot.message_handler(func=lambda message: any(message.text in items for items in menu.values()))
def add_to_cart(message):
    chat_id = message.chat.id
    item = message.text
    
    if chat_id not in user_orders:
        user_orders[chat_id] = []
    
    user_orders[chat_id].append(item)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛒 View Order", "🔙 Back")
    
    bot.send_message(chat_id, f"✅ {item} Added to cart!", reply_markup=markup)

# View Order
@bot.message_handler(func=lambda message: message.text == "🛒 View Order")
def view_order(message):
    chat_id = message.chat.id
    
    if chat_id not in user_orders or not user_orders[chat_id]:
        bot.send_message(chat_id, "❌ Cart is empty!")
        return
    
    total = 0
    order_text = "🧾 Your Order:\n\n"
    
    for item in user_orders[chat_id]:
        order_text += f"• {item}\n"
        for category in menu.values():
            if item in category:
                total += category[item]
    
    order_text += f"\n💰 Total: ₹{total}"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Confirm Order", "🔙 Back")
    
    bot.send_message(chat_id, order_text, reply_markup=markup)

# Confirm Order
@bot.message_handler(func=lambda message: message.text == "✅ Confirm Order")
def confirm_order(message):
    chat_id = message.chat.id
    
    if chat_id not in user_orders:
        return
    
    order_list = "\n".join(user_orders[chat_id])
    
    bot.send_message(chat_id, "🎉 Order Confirmed! Thank you for ordering.")
    
    # Admin ko notify karega
    bot.send_message(ADMIN_ID, f"📢 New Order:\n\n{order_list}")
    
    user_orders[chat_id] = []

# Back Button
@bot.message_handler(func=lambda message: message.text == "🔙 Back")
def back(message):
    start(message)

print("Bot Running...")
bot.infinity_polling()

