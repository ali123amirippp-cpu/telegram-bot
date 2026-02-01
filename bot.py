import logging
import sqlite3
import urllib.parse
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# -------------------- تنظیمات --------------------
TOKEN = "8216995020:AAGvoljr486O-2PItdAH7Rvgo_a_SSgAX5c"
ADMIN_WHATSAPP = "93780049843"  # بدون + برای لینک واتساپ
ORDER = 1

# -------------------- دیتابیس --------------------
conn = sqlite3.connect("orders.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    order_text TEXT
)""")
conn.commit()

# -------------------- زبان‌ها --------------------
user_lang = {}

texts = {
    "fa": {
        "welcome": "🤖 به ربات خدمات ساخت ربات خوش آمدید",
        "menu": "🏠 منوی اصلی",
        "services": "🛠 خدمات",
        "prices": "💰 قیمت‌ها",
        "order": "📝 سفارش",
        "support": "📞 پشتیبانی",
        "settings": "⚙ تنظیمات",
        "back": "🔙 برگشت به منو",
        "write_order": "✍ لطفاً توضیحات ربات خود را بنویسید:",
        "order_done": "✅ سفارش شما ثبت شد.\nروی دکمه زیر بزنید تا به واتساپ ارسال شود.",
        "use": "📘 نحوه استفاده:\nاز منو بخش مورد نظر را انتخاب کنید و سفارش بدهید.",
        "contact": "برای تماس مستقیم روی دکمه بزنید 👇",
        "what_build": """🏗 ما ربات‌های زیر را می‌سازیم:

• فروشگاهی  
• خبری  
• پاسخ خودکار  
• اطلاع رسانی  
• شخصی  

ربات‌ها همیشه آنلاین و مناسب همه کسب‌وکارها هستند.
برای سفارش به بخش سفارش بروید.""",
        "rules": "📜 ما طبق قوانین تلگرام کار می‌کنیم و مسئولیت سوءاستفاده بر عهده کاربر است.",
        "privacy": "🔒 حریم خصوصی شما محفوظ است و هیچ دسترسی به اطلاعات شما نداریم.",
        "simple": "🤖 ربات ساده مناسب کسب‌وکار کوچک.\nقیمت از ( ) تا ( )",
        "medium": "⚙ ربات متوسط با امکانات بیشتر.\nقیمت از ( ) تا ( )",
        "pro": "🚀 ربات پیشرفته کاملاً هوشمند.\nقیمت از ( ) تا ( )"
    },
    "en": {
        "welcome": "🤖 Welcome to our Bot Services",
        "menu": "🏠 Main Menu",
        "services": "🛠 Services",
        "prices": "💰 Prices",
        "order": "📝 Order",
        "support": "📞 Support",
        "settings": "⚙ Settings",
        "back": "🔙 Back to Menu",
        "write_order": "✍ Please write your bot order details:",
        "order_done": "✅ Your order has been received.\nClick the button below to send to WhatsApp.",
        "use": "📘 How to use:\nSelect the desired section from the menu and place your order.",
        "contact": "Click the button to contact directly 👇",
        "what_build": """🏗 We build the following bots:

• Store bots  
• News bots  
• Auto-reply bots  
• Notification bots  
• Personal bots  

Bots are always online and suitable for all businesses.
Go to the Order section to get your bot.""",
        "rules": "📜 We follow Telegram rules. Any misuse is the user's responsibility.",
        "privacy": "🔒 Your privacy is fully protected, we have no access to your data.",
        "simple": "🤖 Simple bot for small businesses.\nPrice from ( ) to ( )",
        "medium": "⚙ Medium bot with extra features.\nPrice from ( ) to ( )",
        "pro": "🚀 Advanced bot for professional use.\nPrice from ( ) to ( )"
    },
    "ar": {
        "welcome": "🤖 مرحبًا بكم في خدمة إنشاء البوت",
        "menu": "🏠 القائمة الرئيسية",
        "services": "🛠 الخدمات",
        "prices": "💰 الأسعار",
        "order": "📝 الطلب",
        "support": "📞 الدعم",
        "settings": "⚙ الإعدادات",
        "back": "🔙 العودة للقائمة",
        "write_order": "✍ الرجاء كتابة تفاصيل طلب البوت:",
        "order_done": "✅ تم استلام طلبك.\nاضغط على الزر أدناه للإرسال عبر واتساب.",
        "use": "📘 كيفية الاستخدام:\nاختر القسم المطلوب من القائمة وقم بالطلب.",
        "contact": "اضغط على الزر للتواصل مباشرة 👇",
        "what_build": """🏗 نحن نصنع البوتات التالية:

• بوتات المتجر  
• بوتات الأخبار  
• بوتات الرد التلقائي  
• بوتات الإشعارات  
• بوتات شخصية  

البوتات دائمًا متصلة ومناسبة لجميع الأعمال.
اذهب إلى قسم الطلب للحصول على البوت الخاص بك.""",
        "rules": "📜 نتبع قوانين تلغرام وأي استخدام خاطئ هو مسؤولية المستخدم.",
        "privacy": "🔒 خصوصيتك محفوظة تمامًا، ليس لدينا وصول إلى بياناتك.",
        "simple": "🤖 بوت بسيط للأعمال الصغيرة.\nالسعر من ( ) إلى ( )",
        "medium": "⚙ بوت متوسط مع ميزات إضافية.\nالسعر من ( ) إلى ( )",
        "pro": "🚀 بوت متقدم للمستخدمين المحترفين.\nالسعر من ( ) إلى ( )"
    }
}

# ---------- منوها ----------
def main_menu_keyboard(lang):
    t = texts[lang]
    return ReplyKeyboardMarkup([
        [t["services"], t["prices"]],
        [t["order"], t["support"]],
        [t["settings"]]
    ], resize_keyboard=True)

def back_keyboard(lang):
    return ReplyKeyboardMarkup([[texts[lang]["back"]]], resize_keyboard=True)

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang[update.effective_user.id] = "fa"
    await update.message.reply_text(texts["fa"]["welcome"], reply_markup=main_menu_keyboard("fa"))

# خدمات
async def services(update: Update, context):
    lang = user_lang[update.effective_user.id]
    kb = ReplyKeyboardMarkup([
        ["🏗 ما چی می‌سازیم"],
        ["📜 قوانین ما"],
        ["🔒 حفظ حریم خصوصی"],
        [texts[lang]["back"]]
    ], resize_keyboard=True)
    await update.message.reply_text("🛠 بخش خدمات", reply_markup=kb)

async def what_build(update: Update, context):
    lang = user_lang[update.effective_user.id]
    await update.message.reply_text(texts[lang]["what_build"], reply_markup=back_keyboard(lang))

async def rules(update: Update, context):
    lang = user_lang[update.effective_user.id]
    await update.message.reply_text(texts[lang]["rules"], reply_markup=back_keyboard(lang))

async def privacy(update: Update, context):
    lang = user_lang[update.effective_user.id]
    await update.message.reply_text(texts[lang]["privacy"], reply_markup=back_keyboard(lang))

# قیمت‌ها
async def prices(update: Update, context):
    lang = user_lang[update.effective_user.id]
    kb = ReplyKeyboardMarkup([
        ["🤖 ساده"],
        ["⚙ متوسط"],
        ["🚀 پیشرفته"],
        [texts[lang]["back"]]
    ], resize_keyboard=True)
    await update.message.reply_text("💰 بخش قیمت‌ها", reply_markup=kb)

# سفارش
async def order_start(update: Update, context):
    lang = user_lang[update.effective_user.id]
    await update.message.reply_text(texts[lang]["write_order"], reply_markup=back_keyboard(lang))
    return ORDER

async def receive_order(update: Update, context):
    uid = update.effective_user.id
    lang = user_lang.get(uid, "fa")
    user_text = update.message.text

    # ذخیره در دیتابیس
    c.execute("INSERT INTO orders (user_id, username, order_text) VALUES (?, ?, ?)", 
              (uid, update.effective_user.username, user_text))
    conn.commit()

    # لینک واتساپ
    msg = urllib.parse.quote(f"سفارش جدید:\n{user_text}")
    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text={msg}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📤 ارسال به واتساپ", url=wa_link)]])
    await update.message.reply_text(texts[lang]["order_done"], reply_markup=kb)
    return ConversationHandler.END

# پشتیبانی
async def support(update: Update, context):
    lang = user_lang[update.effective_user.id]
    kb = ReplyKeyboardMarkup([
        ["📘 نحوه استفاده"],
        ["💬 تماس با ما"],
        [texts[lang]["back"]]
    ], resize_keyboard=True)
    await update.message.reply_text("📞 پشتیبانی", reply_markup=kb)

async def how_to_use(update: Update, context):
    lang = user_lang[update.effective_user.id]
    await update.message.reply_text(texts[lang]["use"], reply_markup=back_keyboard(lang))

async def contact(update: Update, context):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📲 واتساپ", url=f"https://wa.me/{ADMIN_WHATSAPP}")]])
    await update.message.reply_text(texts["fa"]["contact"], reply_markup=kb)

# تنظیمات
async def settings(update: Update, context):
    kb = ReplyKeyboardMarkup([
        ["🇮🇷 فارسی", "🇬🇧 English", "🇸🇦 عربي"],
        ["🔙 برگشت به منو"]
    ], resize_keyboard=True)
    await update.message.reply_text("🌍 انتخاب زبان", reply_markup=kb)

async def set_language(update: Update, context):
    text = update.message.text
    uid = update.effective_user.id
    if "فارسی" in text: user_lang[uid] = "fa"
    elif "English" in text: user_lang[uid] = "en"
    elif "عربي" in text: user_lang[uid] = "ar"
    lang = user_lang[uid]
    await update.message.reply_text("✅ زبان تنظیم شد", reply_markup=main_menu_keyboard(lang))

# برگشت
async def back(update: Update, context):
    uid = update.effective_user.id
    lang = user_lang.get(uid, "fa")
    await update.message.reply_text(texts[lang]["menu"], reply_markup=main_menu_keyboard(lang))

# پیام خارج از منو
async def unknown(update: Update, context):
    uid = update.effective_user.id
    lang = user_lang.get(uid, "fa")
    await update.message.reply_text("از دکمه‌ها استفاده کنید 👆", reply_markup=main_menu_keyboard(lang))

# -------------------- اجرا --------------------
app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("📝 سفارش"), order_start)],
    states={ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_order)]},
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("🛠 خدمات"), services))
app.add_handler(MessageHandler(filters.Regex("🏗 ما چی می‌سازیم"), what_build))
app.add_handler(MessageHandler(filters.Regex("📜 قوانین ما"), rules))
app.add_handler(MessageHandler(filters.Regex("🔒 حفظ حریم خصوصی"), privacy))
app.add_handler(MessageHandler(filters.Regex("💰 قیمت‌ها"), prices))
app.add_handler(conv)
app.add_handler(MessageHandler(filters.Regex("📞 پشتیبانی"), support))
app.add_handler(MessageHandler(filters.Regex("📘 نحوه استفاده"), how_to_use))
app.add_handler(MessageHandler(filters.Regex("💬 تماس با ما"), contact))
app.add_handler(MessageHandler(filters.Regex("⚙ تنظیمات"), settings))
app.add_handler(MessageHandler(filters.Regex("فارسی|English|عربي"), set_language))
app.add_handler(MessageHandler(filters.Regex("🔙"), back))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, unknown))

print("Bot Running...")
app.run_polling()