import telebot
from telebot import types

TOKEN = "7953258524:AAH_gK6YmO2mQZ-jC_w_d_e_f_g_h_i_j_k"  # O'zingizning bot tokeningiz
ADMIN_ID = 8702640490  # Sizning Telegram ID raqamingiz

bot = telebot.TeleBot(TOKEN)

# Vaqtinchalik ma'lumotlar bazasi (lug'atlar)
users_balance = {}  # {user_id: balance}
user_orders = {}  # {user_id: [orders]}


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

  # Faqat adminga Admin Panel tugmasini chiqarish
  if user_id == ADMIN_ID:
    btn_admin = types.KeyboardButton("⚙️ Admin Panel")
    markup.add(btn1, btn2)
    markup.add(btn3, btn_admin)
  else:
    markup.add(btn1, btn2)
    markup.add(btn3)

  bot.send_message(
      message.chat.id,
      "👋 Instagram nakrutka botiga xush kelibsiz.\nQuyidagi menyudan kerakli"
      " bo'limni tanlang:",
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
        f"✅ Foydalanuvchi ({target_user_id}) balansiga {amount} so'm"
        f" qo'shildi!\nJami balans: {users_balance[target_user_id]} so'm",
    )
    bot.send_message(
        target_user_id,
        f"🎉 Sizning balansingizga {amount} so'm qo'shildi!\nJami balans:"
        f" {users_balance[target_user_id]} so'm",
    )
  except Exception as e:
    bot.send_message(
        message.chat.id,
        "❌ Xato format!\nTo'g'ri format: `/add ID SUMMA`\nMasalan: `/add"
        " 8702640490 50000`",
    )


# Tugmalar bo'yicha javoblar
@bot.message_handler(content_types=['text'])
def handle_text(message):
  user_id = message.from_user.id

  if user_id not in users_balance:
    users_balance[user_id] = 0

  if message.text == "💰 Balans":
    balance = users_balance[user_id]
    bot.send_message(
        message.chat.id,
        f"💰 Sizning balansingiz: {balance} so'm\n\nID'ingiz:"
        f" `{user_id}`\nBalansni to'ldirish uchun adminga murojaat qiling.",
        parse_mode="Markdown",
    )

  elif message.text == "⚙️ Admin Panel":
    if user_id == ADMIN_ID:
      bot.send_message(
          message.chat.id,
          "⚙️ **Admin Panel**\n\nFoydalanuvchiga balans qo'shish uchun"
          " quyidagi formatda yozing:\n`/add ID SUMMA`\nMasalan: `/add"
          " 8702640490 50000`",
          parse_mode="Markdown",
      )
    else:
      bot.send_message(message.chat.id, "❌ Siz admin emassiz!")

  elif message.text == "🛠 Qo'llab-quvvatlash":
    bot.send_message(
        message.chat.id,
        "📞 Muammo yoki savollar bo'yicha adminga yozing: @jasur_jas",
    )

  elif message.text == "🚀 Nakrutka urish":
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "👤 Obunachi (1000 ta = 15,000 so'm)", callback_data="order_subs"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "❤️ Layk (1000 ta = 5,000 so'm)", callback_data="order_likes"
        )
    )
    bot.send_message(
        message.chat.id,
        "📦 Kerakli xizmat turini tanlang:",
        reply_markup=markup,
    )


# Inline tugmalar uchun handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  user_id = call.from_user.id
  if user_id not in users_balance:
    users_balance[user_id] = 0

  if call.data == "order_subs":
    if users_balance[user_id] >= 15000:
      users_balance[user_id] -= 15000
      bot.answer_callback_query(
          call.id, "✅ Buyurtma qabul qilindi! Bajarilmoqda..."
      )
      bot.send_message(
          call.message.chat.id,
          "🚀 Obunachi buyurtmangiz bazaga qo'shildi!\nQolgan balans:"
          f" {users_balance[user_id]} so'm",
      )
    else:
      bot.answer_callback_query(
          call.id, "❌ Balansingiz yetarli emas!", show_alert=True
      )

  elif call.data == "order_likes":
    if users_balance[user_id] >= 5000:
      users_balance[user_id] -= 5000
      bot.answer_callback_query(
          call.id, "✅ Buyurtma qabul qilindi! Bajarilmoqda..."
      )
      bot.send_message(
          call.message.chat.id,
          "🚀 Layk buyurtmangiz bazaga qo'shildi!\nQolgan balans:"
          f" {users_balance[user_id]} so'm",
      )
    else:
      bot.answer_callback_query(
          call.id, "❌ Balansingiz yetarli emas!", show_alert=True
      )


print("Bot qayta ishga tushdi va xabarlarni kutmoqda...")
bot.infinity_polling()
