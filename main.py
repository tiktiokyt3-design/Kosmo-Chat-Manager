import time
import os
import sys
import telebot
from html import escape
from telebot import types
from database.storage_role import add_user, get_role, get_user_by_username, set_role
from handlers.roles import roles_number, roles_name
from config import token, owner_id, secret_id
from logger.log import log, log_file

bot = telebot.TeleBot(token, parse_mode="HTML")

# ==== Admin Panel restart_cmd ====
def restart():
    os.execv(sys.executable, ['python'] + sys.argv)

# ==== Functiom ====
def is_admin(message):
    chat_id = message.chat.id 
    user_id = message.from_user.id
    admin = bot.get_chat_administrators(chat_id)
    if user_id == admin:
        bot.reply_to(message, "🚨 Упс... Данный пользователь Админ!")
        return


@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "‼️ бот находиться в разработке!")
        return
    
    add_user(message.from_user.id, message.from_user.username)
    
    if message.from_user.id == owner_id:
        set_role(message.from_user.id, "owner_bot")
    
    if message.from_user.id == secret_id:
        set_role(message.from_user.id, "dayn")
    
    # Logger
    log(f"Новый пользователь зарегистрировался в базу!")

# ==== Moderator command ====
@bot.message_handler(commands=['ban'])
def ban_cmd_moder(message):
    if message.chat.type == "private":
        return

    user_id = message.from_user.id
    role = get_role(user_id)
    is_admin(message)

    if roles_number[role] < roles_number["admin"]:
        return bot.reply_to(message, "❌ Упс... Тебе не доступна команда")

    args = message.text.split()
    if len(args) < 3:
        return bot.reply_to(message, "✍️ Используй: /ban @username 30d")

    username = args[1].replace("@", "")
    target_id = get_user_by_username(username)
    if not target_id:
        return

    try:
        time_arg = args[2]
        unit = time_arg[-1].lower()
        value = int(time_arg[:-1])

        if unit == "m":
            until_date = int(time.time()) + value * 60
        elif unit == "h":
            until_date = int(time.time()) + value * 3600
        elif unit == "d":
            until_date = int(time.time()) + value * 24 * 3600
        else:
            until_date = int(time.time()) + value * 24 * 3600

    except ValueError:
        return bot.reply_to(message, "‼️ Упс... Время должно быть числом с m / h / d")

    chat_id = message.chat.id

    bot.kick_chat_member(chat_id, target_id)
    bot.ban_chat_member(chat_id, target_id, until_date=until_date)

    bot.send_message(chat_id, f"🚫 Пользователь @{username} получил бан на {time_arg}\n🚨 Модератор @{message.from_user.username}")

    # Logger
    log(f"@{message.from_user.username} выдал бан пользователю @{username}")
    
@bot.message_handler(commands=['unban'])
def unban_cmd_moder(message):
    if message.chat.type == "private":
        return

    is_admin(message)
    user_id = message.from_user.id
    role = get_role(user_id)

    if roles_number[role] < roles_number["admin"]:
        return bot.reply_to(message, "❌ Упс... Тебе не доступна команда")

    args = message.text.split()

    if len(args) < 2:
        return bot.reply_to(message, "✍️ Используй: /unban @username")

    username = args[1].replace("@", "")
    target_id = get_user_by_username(username)
    if not target_id:
        return 

    chat_id = message.chat.id
    bot.unban_chat_member(chat_id, target_id)

    bot.send_message(message.chat.id, f"✅ Пользователь @{username} вышел на свободу\n🚨 Модератор @{message.from_user.username}")

    # Logger
    log(f"@{message.from_user.username} выдал разбан пользователю @{username}")

@bot.message_handler(commands=['kick'])
def kick_cmd_moder(message):
    if message.chat.type == "private":
        return

    is_admin(message)

    user_id = message.from_user.id
    chat_id = message.chat.id
    role = get_role(user_id)

    if roles_number[role] < roles_number["moderator"]:
        return bot.reply_to(message, "❌ Упс... Тебе не доступна команда")

    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message, "✍️ Используй: /kick @username")
        return

    username = args[1].replace("@", "")
    target_id = get_user_by_username(username)
    if not target_id:
        return 

    bot.kick_chat_member(chat_id, target_id)

    bot.send_message(message.chat.id, f"👋 Пользователь @{username} выгнали с беседы\n🚨 Модератор @{message.from_user.username}")

    # Logger
    log(f"@{message.from_user.username} кикнул пользователя @{username}")
    
@bot.message_handler(commands=['mute'])
def mute_cmd_moder(message):
    if message.chat.type == "private":
        return

    is_admin(message)

    user_id = message.from_user.id
    chat_id = message.chat.id
    role = get_role(user_id)

    if roles_number[role] < roles_number["moderator"]:
        return bot.reply_to(message, "❌ Упс... Тебе не доступна команда")

    if not message.reply_to_message:
        return bot.reply_to(message, "✍️ Используй: /mute ответом на сообщения 20")

    args = message.text.split()

    if len(args) < 2:
        return bot.reply_to(message,"✍️ Используй: /mute ответом на сообщения 20")

    try:
        target_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or "user"

        minutes = int(args[1])

        until_date = int(time.time()) + minutes * 60
        bot.restrict_chat_member(
            chat_id,
            target_id,
            until_date=until_date,
            can_send_messages=False
        )

        bot.reply_to(message, f"⭐️ Пользователю @{username} заткнули рот на {minutes} мин\n🚨 Модератор @{message.from_user.username}")

    except ValueError:
        return

    # Logger
    log(f"@{message.from_user.username} выдал мут пользователю @{username}")

@bot.message_handler(commands=['unmute']) 
def unmute_cmd_moder(message):
    if message.chat.type == "private":
        return

    is_admin(message)

    user_id = message.from_user.id
    chat_id = message.chat.id
    role = get_role(user_id)

    if roles_number[role] < roles_number["moderator"]:
        return bot.reply_to(message, "❌ Упс... Тебе не доступна команда")

    args = message.text.split()

    if len(args) < 2:
        return bot.reply_to(message, "✍️ Используй: /unmute @username")

    username = args[1].replace("@", "")
    target_id = get_user_by_username(username)
    if not target_id:
        return




    bot.restrict_chat_member(
            chat_id,
            target_id,
            can_send_messages=True
    )

    bot.reply_to(message, f"✅ Пользователь @{username} открил рот\n🚨 Модератор @{message.from_user.username}")

    # Logger
    log(f"@{message.from_user.username} выдал размут пользователю @{username}")
    
@bot.message_handler(commands=['add_role'])
def add_role_cmd_moder(message):
    if message.chat.type == "private":
        return

    user_id = message.from_user.id
    role = get_role(user_id)
    if roles_number[role] < roles_number["admin"]:
        return bot.reply_to(message, "❌ Упс... Тебе не доступна команда")

    try:
        _, username, new_role = message.text.split()
        username = username.replace("@", "")
        new_role = new_role.lower()
        if new_role not in roles_number:
            return bot.reply_to(message, "‼️ Упс... Нету такой роли")
    except:
        return bot.reply_to(message, "✍️ Используй: /add_role @username роль")
    target_id = get_user_by_username(username)
    if not target_id:
        return

    set_role(target_id, new_role)
    bot.send_message(message.chat.id, f"✅ Пользователь @{username} получил роль {new_role}\n🚨 Модератор @{message.from_user.username}")

    # Logger
    log(f"@{message.from_user.username} выдал роль {new_role} пользователю @{username}")
    
# ==== Обычные команды ====
@bot.message_handler(commands=['pin'])
def pin_cmd(message):
    if message.chat.type == "private":
        return
    
    user = message.from_user.username
    
    role=get_role(message.from_user.id)
    if roles_number[role] < roles_number["moderator"]:
        bot.reply_to(message, f"❌ Ты еще не дорос чтобы использивать команду")
        return
    
    chat_id = message.chat.id
    if not message.reply_to_message:
        bot.reply_to(message, f"✍️ Ответь на сообщения которое нужно закрепить!")
        return
    
    bot.pin_chat_message(chat_id, message.reply_to_message.message_id)
    bot.send_message(message.chat.id, f"✅ Сообщения закреплено")

    # logger
    log(f"Пользователь @{user} закрепил сообщения")

@bot.message_handler(commands=['unpin'])
def unpin_cmd(message):
    if message.chat.type == "private":
        return
    
    user = message.from_user.username
    
    role = get_role(message.from_user.id)
    if roles_number[role] < roles_number["moderator"]:
        bot.reply_to(message, f"❌ Ты еще не дорос чтобы использивать команду")
        return
    
    chat_id = message.chat.id
    
    
    bot.unpin_chat_message(chat_id)
    bot.send_message(message.chat.id, f"✅ Сообщения откреплено")

    # logger
    log(f"Пользователь @{user} открепил сообщения")

@bot.message_handler(commands=['profile'])
def profile_cmd(message):
    if message.chat.type == "private":
        return
    
    add_user(message.from_user.id, message.from_user.username)
    
    if message.from_user.id == owner_id:
        set_role(message.from_user.id, "owner_bot")
    
    if message.from_user.id == secret_id:
        set_role(message.from_user.id, "dayn")
    
    role = get_role(message.from_user.id)
    bot.send_message(message.chat.id, 
                     f"🆔 ID: {message.from_user.id}\n"
                     f"👤 First_name: {message.from_user.first_name}\n"
                     f"👤 Last_name: {message.from_user.last_name}\n"
                     f"💫 Username: {message.from_user.username}\n"
                     f"⭐️ Привилегия: {roles_name.get(role, role)}\n")

# ==== Обработчик обычных команд ====


# ==== Обработчик всех команд ====
@bot.message_handler(content_types=['text'])
def text(message):
    text = message.text.lower()
    
    if text == "профиль":
        profile_cmd(message)
    elif text == "бан":
        ban_cmd_moder(message)
    elif text == "мут":
        mute_cmd_moder(message)
    elif text == "размут":
        unmute_cmd_moder(message)
    elif text == "разбан":
        unban_cmd_moder(message)
    elif text == "кик":
        kick_cmd_moder(message)
    elif text == "пин":
        pin_cmd(message)
    elif text == "унпин":
        unpin_cmd(message)
    elif text == "панель":
        adminka_cmd_admin(message)
    else:
        return


# ==== Admin Panel ====
@bot.message_handler(commands=['adminka'])
def adminka_cmd_admin(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    role = get_role(user_id)
    
    if roles_number[role] < roles_number["owner_bot"]:
        return
    
    markup = types.InlineKeyboardMarkup()
    
    btn_1 = types.InlineKeyboardButton("🤖 Перезапустить бота", callback_data="restart_bot")
    btn_2 = types.InlineKeyboardButton("💬 Логи", callback_data="log_bot")
    btn_3 = types.InlineKeyboardButton("⭐️ Писать за бота", callback_data="text_bot")
    markup.add(btn_1)
    markup.add(btn_2)
    markup.add(btn_3)
    
    bot.send_message(message.chat.id, 
                     f"👋 Добро пожаловать в админ панель: @{username}\n\n"
                     f"⭐️ Роль {role}\n"
                     f"👤 First_name {first_name}\n"
                     f"👑 Username @{username}\n"
                     f"🆔 ID {user_id}\n", reply_markup=markup)

# ==== Обрботчик админських команд ====
@bot.callback_query_handler(func=lambda call: call.data=="restart_bot")
def restart_bot_call(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "🔄 Перезапуск...")
    time.sleep(0.1)
    bot.send_message(call.message.chat.id, "✅ Бот успешно перезапущен")
    restart()

@bot.callback_query_handler(func=lambda call: call.data=="log_bot")
def log_bot_call(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    with open(log_file, 'r', encoding="utf-8") as f:
        data = f.read()
    bot.send_message(call.message.chat.id, escape(data), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data=="text_bot")
def text_bot_call(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "💬 Напиши текст")
    bot.register_next_step_handler(call.message, text_bot_call_two)
    
def text_bot_call_two(message):
    username = message.from_user.username
    bot.send_message(message.chat.id, message.text)
    # logger
    log(f"Пользователь @{username} отправил текст за бота: {message.text}")

# ==== Start menu bot ====
os.system('cls')
print("Bot Starting | admin_panel: /adminka")
bot.infinity_polling()