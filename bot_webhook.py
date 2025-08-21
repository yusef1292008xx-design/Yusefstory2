import os
import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('8398951288:AAGyuTOK_oZwnXTjsq4wgDsml-tvMc2UF3U')
if not TOKEN:
    logger.error('لم يتم العثور على متغير البيئة TELEGRAM_TOKEN. ضع توكن البوت في متغير البيئة.')
    raise SystemExit('ضع TELEGRAM_TOKEN في environment variables')

bot = Bot(token=TOKEN)
app = Flask(__name__)
# Dispatcher بدون updater: مناسب للاستعمال مع Flask
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# نفس handlers كما في bot.py
def start(update, context):
    user = update.effective_user
    update.message.reply_text(f"مرحبًا {user.first_name}! أنا بوت عبر Webhook. /help")

def help_cmd(update, context):
    update.message.reply_text("استخدم /echo أو /buttons")

def echo_cmd(update, context):
    args = context.args
    if not args:
        update.message.reply_text("استخدم: /echo نص")
        return
    update.message.reply_text(' '.join(args))

def echo_message(update, context):
    update.message.reply_text(f"استلمت: {update.message.text}")

def buttons_cmd(update, context):
    keyboard = [[InlineKeyboardButton("اضغط هنا", callback_data='pressed')]]
    update.message.reply_text("اختر:", reply_markup=InlineKeyboardMarkup(keyboard))

def button_callback(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("تم الضغط! ✅")

# تسجيل المعالجات
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_cmd))
dispatcher.add_handler(CommandHandler('echo', echo_cmd))
dispatcher.add_handler(CommandHandler('buttons', buttons_cmd))
dispatcher.add_handler(CallbackQueryHandler(button_callback))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_message))

@app.route(f"/webhook/{TOKEN}", methods=['POST'])
def webhook():
    # Telegram سيرسل POST JSON هنا
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

if __name__ == '__main__':
    # للتشغيل المحلي (غير آمن للإنتاج):
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))