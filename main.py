import telebot
from telebot import types

TOKEN = "8646999261:AAGliHfLlH-PKHJtImas9erOsXKCdsyGPxs"
ADMIN_ID = 8702640490  # Sizning Telegram ID raqamingiz

bot = telebot.TeleBot(TOKEN)

# Ma'lumotlar bazasi
users_balance = {}  # {user_id: balance}
admin_income = {ADMIN_ID: 0}  # Sizning daromadingiz (kassangiz)

# Admin va foydalanuvchilarning vaqtinchalik holatlari
admin_withdrawing = {}
user_waiting_for_link = {}  # {user_id: service_code}


# /start komandasi
@bot.message_handler(commands=['start'])
def send_welcome(message):
  user_id = message.from_user.id
  if user_id not in users_balance:
    users_balance[user_id] = 0

  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  btn1 = types.KeyboardButton("🚀 Nakrutka urish")
  btn2 = types.KeyboardButton("💰 Balans")
  btn3 = types.KeyboardButton("🛠 Qo'llab-quvvatlash")

  if user_id == ADMIN_ID:
    btn_admin = types.KeyboardButton("⚙️ Admin Panel")
    markup.add(btn1, btn2)
    markup.add(btn3, btn_admin)
  else:
    markup.add(btn1, btn2)
    markup.add(btn3)

  bot.send_message(
      message.chat.id,
      "👋 Instagram nakrutka botiga xush kelibsiz.\nQuyidagi menyudan kerakli bo'limni tanlang:",
      reply_markup=markup,
  )


# Admin uchun balans qo'shish komandasi: /add ID SUMMA
@bot.message_handler(commands=['add'])
def add_balance(message):
  if message.from_user.id != ADMIN_ID:
    bot.send_message(message.chat.id, "❌ Bu buyruq faqat admin uchun!")
    return

  try:
    parts = message.text.split()
    target_user_id = int(parts[1])
    amount = int(parts[2])

    if target_user_id not in users_balance:
      users_balance[target_user_id] = 0

    users_balance[target_user_id] += amount

    bot.send_message(
        message.chat.id,
        f"✅ Foydalanuvchi ({target_user_id}) balansiga {amount:,} so'm qo'shildi!\nJami balans: {users_balance[target_user_id]:,} so'm",
    )
    bot.send_message(
        target_user_id,
        f"🎉 Sizning balansingizga {amount:,} so'm qo'shildi!\nJami balans: {users_balance[target_user_id]:,} so'm",
    )
  except Exception as e:
    bot.send_message(
        message.chat.id,
        "❌ Xato format!\nTo'g'ri format: `/add ID SUMMA`\nMasalan: `/add 8702640490 50000`",
    )


# Tugmalar va matnlar bo'yicha javoblar
@bot.message_handler(content_types=['text'])
def handle_text(message):
  user_id = message.from_user.id

  # 1. Admin pul yechish uchun karta raqamini yozayotgan bo'lsa
  if user_id == ADMIN_ID and admin_withdrawing.get(user_id, False):
    card_number = message.text
    amount_to_withdraw = admin_income.get(ADMIN_ID, 0)

    if amount_to_withdraw <= 0:
      bot.send_message(message.chat.id, "❌ Kassangizda yechib olish uchun pul yo'q.")
      admin_withdrawing[user_id] = False
      return

    admin_income[ADMIN_ID] = 0
    admin_withdrawing[user_id] = False

    bot.send_message(
        message.chat.id,
        f"✅ **Pulni yechish bo'yicha so'rov yuborildi!**\n\n"
        f"💳 Karta: `{card_number}`\n"
        f"💵 Summa: {amount_to_withdraw:,} so'm\n\n"
        f"Tez orada ko'rsatilgan kartaga pul o'tkazib beriladi.",
        parse_mode="Markdown",
    )
    return

  if user_id not in users_balance:
    users_balance[user_id] = 0

  # 2. Foydalanuvchi tanlagan xizmatiga mos havolani yuborayotgan bo'lsa
  if user_id in user_waiting_for_link and user_waiting_for_link[user_id]:
    link = message.text
    service_code = user_waiting_for_link[user_id]
    user_waiting_for_link[user_id] = None  # Holatni tozalash

    services = {
        "order_subs": {
            "name": "Obunachi (1000 ta)",
            "price": 20000,
            "profit": 10000,
        },
        "order_likes": {
            "name": "Layk (1000 ta)",
            "price": 8000,
            "profit": 7000,
        },
        "order_views": {
            "name": "Tomosha (1000 ta)",
            "price": 6000,
            "profit": 5000,
        },
        "order_comments": {
            "name": "Kommentariya (100 ta)",
            "price": 15000,
            "profit": 10000,
        },
    }

    if service_code not in services:
      bot.send_message(message.chat.id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
      return

    s_info = services[service_code]
    price = s_info["price"]
    profit = s_info["profit"]
    service_name = s_info["name"]

    if users_balance[user_id] >= price:
      users_balance[user_id] -= price
      admin_income[ADMIN_ID] = admin_income.get(ADMIN_ID, 0) + profit

      bot.send_message(
          message.chat.id,
          f"✅ **Buyurtma qabul qilindi!**\n\n"
          f"📦 Xizmat: {service_name}\n"
          f"🔗 Havola: {link}\n"
          f"💰 Yechildi: {price:,} so'm\n"
          f"💳 Qolgan balans: {users_balance[user_id]:,} so'm\n\n"
          f"Tez orada bajariladi!",
          parse_mode="Markdown",
      )

      bot.send_message(
          ADMIN_ID,
          f"🔔 **Yangi buyurtma!**\n\n"
          f"👤 Foydalanuvchi ID: `{user_id}`\n"
          f"📦 Xizmat: {service_name}\n"
          f"🔗 Havola: {link}\n"
          f"💵 Tushgan foyda: {profit:,} so'm",
          parse_mode="Markdown",
      )
    else:
      bot.send_message(
          message.chat.id,
          f"❌ Balansingiz yetarli emas!\nKerakli summa: {price:,} so'm. Sizning balansingiz: {users_balance[user_id]:,} so'm",
      )
    return

  # Oddiy menyular
  if message.text == "💰 Balans":
    balance = users_balance[user_id]
    bot.send_message(
        message.chat.id,
        f"💰 Sizning balansingiz: {balance:,} so'm\n\n"
        f"🆔 ID'ingiz: `{user_id}`\n\n"
        f"💳 Balansni to'ldirish uchun karta raqam:\n"
        f"`9860 3501 4391 7341` Baratov Jasur\n\n"
        f"Pulni o'tkazib, chekni adminga yuboring: @Baratov_o6",
        parse_mode="Markdown",
    )

  elif message.text == "⚙️ Admin Panel":
    if user_id == ADMIN_ID:
      my_income = admin_income.get(ADMIN_ID, 0)
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              "💵 Pulni yechib olish", callback_data="withdraw_income"
          )
      )
      bot.send_message(
          message.chat.id,
          f"⚙️ **Admin Panel**\n\n"
          f"💵 **Sizning umumiy daromadingiz (foydangiz):** {my_income:,} so'm\n\n"
          f"Foydalanuvchiga balans qo'shish uchun quyidagi formatda yozing:\n"
          f"`/add ID SUMMA`\nMasalan: `/add 8702640490 50000`",
          parse_mode="Markdown",
          reply_markup=markup,
      )
    else:
      bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

  elif message.text == "🛠 Qo'llab-quvvatlash":
    bot.send_message(
        message.chat.id,
        "📞 Muammo yoki savollar bo'yicha adminga yozing: @Baratov_o6",
    )

  elif message.text == "🚀 Nakrutka urish":
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "👤 Obunachi (1000 ta = 20,000 so'm)", callback_data="order_subs"
        ),
        types.InlineKeyboardButton(
            "❤️ Layk (1000 ta = 8,000 so'm)", callback_data="order_likes"
        ),
        types.InlineKeyboardButton(
            "👀 Tomosha (1000 ta = 6,000 so'm)", callback_data="order_views"
        ),
        types.InlineKeyboardButton(
            "💬 Kommentariya (100 ta = 15,000 so'm)",
            callback_data="order_comments",
        ),
    )
    bot.send_message(
        message.chat.id,
        "📦 Kerakli xizmat turini tanlang:",
        reply_markup=markup,
    )


# Admin pul yechish tugmasi
@bot.callback_query_handler(func=lambda call: call.data == "withdraw_income")
def withdraw_callback(call):
  user_id = call.from_user.id
  if user_id != ADMIN_ID:
    return

  my_income = admin_income.get(ADMIN_ID, 0)
  if my_income <= 0:
    bot.answer_callback_query(
        call.id, "❌ Kassangizda yechib olish uchun pul yo'q!", show_alert=True
    )
    return

  admin_withdrawing[user_id] = True
  bot.answer_callback_query(call.id)
  bot.send_message(
      call.message.chat.id,
      f"💳 **Pulni yechib olish**\n\n"
      f"Jami yechiladigan summa: **{my_income:,} so'm**\n\n"
      f"Iltimos, pulni tashlab berishimiz uchun **karta raqamingizni** yuboring:",
      parse_mode="Markdown",
  )


# Xizmat tugmalaridan biri bosilganda
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def callback_query(call):
  user_id = call.from_user.id
  service_code = call.data

  service_names = {
      "order_subs": "Obunachi (1000 ta)",
      "order_likes": "Layk (1000 ta)",
      "order_views": "Tomosha (1000 ta)",
      "order_comments": "Kommentariya (100 ta)",
  }

  if service_code not in service_names:
    return

  user_waiting_for_link[user_id] = service_code

  bot.answer_callback_query(call.id)
  bot.send_message(
      call.message.chat.id,
      f"🔗 Iltimos, **{service_names[service_code]}** uchun kerakli **Instagram havolasini** yuboring:",
      parse_mode="Markdown",
  )


print("Bot qayta ishga tushdi va xabarlarni kutmoqda...")
bot.infinity_polling()
