import os
import sys
import subprocess

# تثبيت المكتبات الناقصة
required_libs = ["python-telegram-bot==20.7", "apscheduler==3.10.4", "pytz"]

def install_missing_packages():
    for lib in required_libs:
        try:
            __import__(lib.split("==")[0])
        except ImportError:
            print(f"📦 تثبيت المكتبة الناقصة: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_missing_packages()

# استيراد المكتبات
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import pytz
os.environ["TZ"] = "UTC"

# توكن البوت
TOKEN = "8398951288:AAGyuTOK_oZwnXTjsq4wgDsml-tvMc2UF3U"

# 🔑 ID الأدمن
ADMIN_ID = 6612812394

# بيانات البوت مؤقتة
bot_data_store = {
    "welcome": "مرحبا بك في البوت 👋",
    "channel": None,
    "users": set(),
    "admin_buttons": {}  # لتخزين الأزرار المخصصة
}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_data_store["users"].add(user_id)

    if user_id == ADMIN_ID:
        await show_admin_panel(update, context)
    else:
        await update.message.reply_text(bot_data_store["welcome"])

# عرض لوحة الأدمن
async def show_admin_panel(update, context):
    keyboard = [
        [InlineKeyboardButton("✍️ تعديل الترحيب", callback_data="set_welcome")],
        [InlineKeyboardButton("📢 إضافة قناة", callback_data="add_channel")],
        [InlineKeyboardButton("📋 عرض الإعدادات", callback_data="view_settings")],
        [InlineKeyboardButton("📣 رسالة جماعية", callback_data="broadcast")],
        [InlineKeyboardButton("➕ إضافة زر جديد", callback_data="add_admin_button")]
    ]

    # إضافة الأزرار المخصصة مسبقاً
    for key, val in bot_data_store["admin_buttons"].items():
        keyboard.append([InlineKeyboardButton(key, callback_data=f"custom_{key}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # إذا جاء من زر
    if update.callback_query:
        await update.callback_query.edit_message_text("⚙️ لوحة الأدمن - اختر الإجراء:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("⚙️ لوحة الأدمن - اختر الإجراء:", reply_markup=reply_markup)

# التعامل مع ضغط أزرار الأدمن
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.edit_message_text("⚠️ لا تملك صلاحية الوصول.")
        return

    data = query.data

    if data == "admin_panel":
        await show_admin_panel(update, context)

    elif data == "set_welcome":
        await query.edit_message_text("✍️ أرسل رسالة الترحيب الجديدة:")
        context.user_data["awaiting_welcome"] = True

    elif data == "add_channel":
        await query.edit_message_text("📢 أرسل رابط القناة لإضافتها:")
        context.user_data["awaiting_channel"] = True

    elif data == "view_settings":
        welcome = bot_data_store.get("welcome")
        channel = bot_data_store.get("channel", "لم يتم إضافة قناة")
        users_count = len(bot_data_store["users"])
        custom_buttons = ", ".join(bot_data_store["admin_buttons"].keys()) or "لا يوجد أزرار مخصصة"
        await query.edit_message_text(
            f"🔧 إعدادات البوت:\n\n👋 الترحيب: {welcome}\n📢 القناة: {channel}\n👥 عدد المستخدمين: {users_count}\n🆕 أزرار الأدمن: {custom_buttons}"
        )

    elif data == "broadcast":
        await query.edit_message_text("📣 أرسل الرسالة الجماعية الآن:")
        context.user_data["awaiting_broadcast"] = True

    elif data == "add_admin_button":
        await query.edit_message_text("➕ أرسل اسم الزر الجديد:")
        context.user_data["awaiting_new_button_name"] = True

    elif data.startswith("custom_"):
        button_name = data.replace("custom_", "")
        await query.edit_message_text(bot_data_store["admin_buttons"][button_name])

# التعامل مع الرسائل بعد اختيار زر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ لا تملك صلاحية الوصول لهذه الأوامر.")
        return

    text = update.message.text

    if context.user_data.get("awaiting_welcome"):
        bot_data_store["welcome"] = text
        context.user_data["awaiting_welcome"] = False
        await update.message.reply_text("✅ تم حفظ رسالة الترحيب!")

    elif context.user_data.get("awaiting_channel"):
        bot_data_store["channel"] = text
        context.user_data["awaiting_channel"] = False
        await update.message.reply_text("✅ تم حفظ القناة!")

    elif context.user_data.get("awaiting_broadcast"):
        context.user_data["awaiting_broadcast"] = False
        count = 0
        for uid in bot_data_store["users"]:
            try:
                await context.bot.send_message(chat_id=uid, text=text)
                count += 1
            except:
                continue
        await update.message.reply_text(f"✅ تم إرسال الرسالة إلى {count} مستخدمين.")

    elif context.user_data.get("awaiting_new_button_name"):
        button_name = text
        context.user_data["awaiting_new_button_name"] = False
        context.user_data["awaiting_new_button_text"] = True
        context.user_data["new_button_name"] = button_name
        await update.message.reply_text(f"➕ أرسل النص الذي سيرسله الزر '{button_name}' عند الضغط:")

    elif context.user_data.get("awaiting_new_button_text"):
        button_text = text
        button_name = context.user_data["new_button_name"]
        bot_data_store["admin_buttons"][button_name] = button_text
        context.user_data["awaiting_new_button_text"] = False
        await update.message.reply_text(f"✅ تم إنشاء الزر '{button_name}' بنجاح!")
        # تحديث لوحة الأدمن بعد إضافة الزر
        await show_admin_panel(update, context)

    else:
        await update.message.reply_text("⚠️ اختر زر من لوحة الأدمن أولاً.")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 البوت يعمل الآن مع إمكانية إضافة أزرار جديدة للأدمن ...")
    app.run_polling()

if __name__ == "__main__":
    main()