
import os
import logging
import asyncio
import google.generativeai as genai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# -------------------- LOGGING --------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -------------------- ENV VARIABLES --------------------
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN missing!")

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY missing!")

# -------------------- GEMINI SETUP --------------------
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------- MENU --------------------
def get_menu_markup():
    keyboard = [
        [
            InlineKeyboardButton("🍔 Burgers & Snacks", callback_data="burgers"),
            InlineKeyboardButton("☕ Beverages", callback_data="coffee"),
        ],
        [InlineKeyboardButton("🍕 Pizza Specials", callback_data="pizza")],
        [InlineKeyboardButton("📍 Location & Contact", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(keyboard)

# -------------------- START --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to Crushers Cafe!*\n\n"
        "Main aapka AI assistant hoon.\n"
        "Menu choose karein ya kuch bhi pooch sakte hain.",
        reply_markup=get_menu_markup(),
        parse_mode="Markdown",
    )

# -------------------- BUTTON HANDLER --------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    DATA = {
        "burgers": "🍔 *BURGERS*\n🔹 Veg: ₹99\n🔹 Cheese: ₹149\n🔹 Paneer: ₹179",
        "coffee": "☕ *BEVERAGES*\n❄️ Cold Coffee: ₹120\n🥤 Oreo Shake: ₹160\n🔥 Hot Coffee: ₹90",
        "pizza": "🍕 *PIZZAS*\n🔸 Margherita: ₹199\n🔸 Veggie: ₹299\n🔸 Paneer: ₹349",
        "contact": "📍 *Uttarakhand, City Center*\n📞 +91 XXXXX XXXXX",
    }

    if query.data in DATA:
        back_btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]]
        )
        await query.edit_message_text(
            text=DATA[query.data],
            reply_markup=back_btn,
            parse_mode="Markdown",
        )

    elif query.data == "main_menu":
        await query.edit_message_text(
            "Aap kya order karna chahenge?",
            reply_markup=get_menu_markup(),
        )

# -------------------- AI HANDLER --------------------
async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        prompt = f"""
        You are the official AI assistant of Crushers Cafe in Uttarakhand.
        Answer politely, briefly and professionally.
        Customer message: {user_text}
        """

        # Async Gemini call (important)
        response = await model.generate_content_async(prompt)

        reply = response.text if response.text else "Sorry, main samajh nahi paya."

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        await update.message.reply_text(
            "⚠️ AI temporarily unavailable. Please try again."
        )

# -------------------- MAIN --------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat))

    logging.info("🚀 Crushers Cafe AI Bot is running...")
    app.run_polling(drop_pending_updates=True)

# -------------------- RENDER KEEP ALIVE --------------------
if __name__ == "__main__":
    from threading import Thread
    import http.server
    import socketserver

    def run_server():
        port = int(os.environ.get("PORT", 10000))

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Crushers Cafe AI Bot is Live!")

        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.serve_forever()

    Thread(target=run_server, daemon=True).start()

    main()

